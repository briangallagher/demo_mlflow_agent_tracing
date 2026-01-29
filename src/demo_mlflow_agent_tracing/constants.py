"""Constants for the expense agent."""

from pathlib import Path

DIRECTORY_PATH = Path(__file__).parent.parent.parent

VECTOR_DB_PATH = DIRECTORY_PATH / "vectordb"
DB_PATH = DIRECTORY_PATH / "db"
CHECKPOINTER_PATH = DB_PATH / "checkpointer.db"
