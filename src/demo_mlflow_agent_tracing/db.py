from langchain_chroma import Chroma

from demo_mlflow_agent_tracing.constants import VECTOR_DB_PATH


def get_db() -> Chroma:
    """Get vector db."""
    embedding_function = None
    db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding_function)
    return db
