"""Agent."""

import logging

import aiosqlite
import mlflow
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.runtime import Runtime
from mlflow.langchain.langchain_tracer import MlflowLangchainTracer

from demo_mlflow_agent_tracing.base import ContextSchema
from demo_mlflow_agent_tracing.chat_model import get_chat_model
from demo_mlflow_agent_tracing.constants import CHECKPOINTER_PATH, DIRECTORY_PATH
from demo_mlflow_agent_tracing.settings import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant. You answer questions using a knowledge base.

When a user asks a question, you must search for the answer in the knowledge base.

DO NOT provide any answer that is not supported by information from the knowledge base.

If you cannot find any information on the topic in the knowledge base, tell the user and do not attempt to answer the question on your own.
""".strip()


async def get_checkpointer_conn():
    """Get the database connection."""
    conn = await aiosqlite.connect(CHECKPOINTER_PATH)
    return conn


def format_input(content: str, user_identifier: str):
    """Format graph input."""
    messages = [{"role": "user", "content": content}]
    input = {"messages": messages, "user_info": user_identifier}
    return input


def format_config(thread_id: str):
    """Format graph config."""
    config = {"configurable": {"thread_id": thread_id}, "callbacks": [MlflowLangchainTracer(run_inline=True)]}
    return config


def format_context(user_identifier: str):
    """Format graph context."""
    context = ContextSchema(user_info=user_identifier)
    return context


@before_agent
def update_tracing(state: AgentState, runtime: Runtime):
    """Update MLFlow tracing params."""
    context: ContextSchema = runtime.context
    user = context.user_info
    mlflow.update_current_trace(metadata={"mlflow.trace.user": user})


async def build_agent():
    """Build the agent."""
    # Construct the agent
    settings = Settings()

    # Get the chat model
    llm = get_chat_model()
    llm.temperature = 0.0

    # Get tools from MCP server
    mcp_client = MultiServerMCPClient(
        {
            "content_writer": {
                "transport": "stdio",
                "command": "python",
                "args": [str(DIRECTORY_PATH / "src" / "demo_mlflow_agent_tracing" / "mcp_server.py")],
                "env": {
                    "OPENAI_API_KEY": settings.OPENAI_API_KEY.get_secret_value(),
                    "OPENAI_MODEL_NAME": settings.OPENAI_MODEL_NAME,
                    "OPENAI_BASE_URL": settings.OPENAI_BASE_URL,
                    "CHAINLIT_AUTH_SECRET": settings.CHAINLIT_AUTH_SECRET.get_secret_value(),
                    "EMBEDDING_API_KEY": settings.EMBEDDING_API_KEY.get_secret_value(),
                    "EMBEDDING_MODEL_NAME": settings.EMBEDDING_MODEL_NAME,
                    "EMBEDDING_BASE_URL": settings.EMBEDDING_BASE_URL,
                    "EMBEDDING_SEARCH_PREFIX": settings.EMBEDDING_SEARCH_PREFIX,
                },
            }
        }
    )
    tools = await mcp_client.get_tools()

    # Load system prompt from MLFlow if requested
    if settings.MLFLOW_SYSTEM_PROMPT_URI is not None:
        logger.info(f"Loading prompt from MLFlow: {settings.MLFLOW_SYSTEM_PROMPT_URI}")
        system_prompt = mlflow.genai.load_prompt(settings.MLFLOW_SYSTEM_PROMPT_URI).format()
    else:
        logger.info("No system prompt specified. Using default system prompt.")
        system_prompt = SYSTEM_PROMPT

    # Create agent
    conn = await get_checkpointer_conn()
    checkpointer = AsyncSqliteSaver(conn=conn)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        context_schema=ContextSchema,
        checkpointer=checkpointer,
        middleware=[update_tracing],
    )

    return agent
