from langchain_openai import ChatOpenAI

from demo_mlflow_agent_tracing.settings import Settings

settings = Settings()


def get_chat_model() -> ChatOpenAI:
    """Get the chat model as defined in the environment variables."""
    # OpenAI-compatible Servers
    chat_model = ChatOpenAI(
        base_url=settings.OPENAI_BASE_URL,
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
    )
    return chat_model
