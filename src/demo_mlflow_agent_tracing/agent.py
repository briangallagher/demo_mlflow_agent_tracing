"""Agent."""

import logging

import aiosqlite
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from demo_mlflow_agent_tracing.base import ContextSchema
from demo_mlflow_agent_tracing.chat_model import get_chat_model
from demo_mlflow_agent_tracing.constants import CHECKPOINTER_PATH, DIRECTORY_PATH

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant. You help manage an online wiki site. 

When a user asks you to help write a wiki page, the `create_new_wiki_page` tool will write the page for you.

You can check if the wiki page was successfully created using the `list_wiki_pages` tool.
""".strip()


async def get_checkpointer_conn():
    """Get the database connection."""
    conn = await aiosqlite.connect(CHECKPOINTER_PATH)
    return conn


async def build_agent():
    """Build the agent."""
    # Construct the agent
    llm = get_chat_model()
    llm.temperature = 0.0
    mcp_client = MultiServerMCPClient(
        {
            "content_writer": {
                "transport": "stdio",
                "command": "python",
                "args": [str(DIRECTORY_PATH / "src" / "demo_mlflow_agent_tracing" / "mcp_server.py")],
            }
        }
    )
    tools = await mcp_client.get_tools()
    conn = await get_checkpointer_conn()
    checkpointer = AsyncSqliteSaver(conn=conn)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        context_schema=ContextSchema,
        checkpointer=checkpointer,
    )

    return agent
