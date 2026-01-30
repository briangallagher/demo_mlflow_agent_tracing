import logging

from demo_mlflow_agent_tracing.constants import DB_PATH, DIRECTORY_PATH
from demo_mlflow_agent_tracing.db import get_db
from demo_mlflow_agent_tracing.settings import Settings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def main():
    """Run ingestion."""
    # Check if the Chroma store exists already
    if (DB_PATH / "chroma.sqlite3").exists():
        logger.info("Chroma store already exists, skipping creation.")
        return

    logger.info("Chroma store does not exist, creating...")

    # Load settings
    settings = Settings()

    # Load the text corpus
    corpus = DIRECTORY_PATH / "public" / "oscorp_policies"
    paths = list(corpus.glob("*.md"))
    logger.info(f"Read {len(paths)} texts from {corpus}")

    # Set up Chroma DB
    db = get_db()
    db.reset_collection()

    # Load all texts as documents
    documents: list[Document] = []
    for path in paths:
        # Get the file content and id
        content = path.read_text()

        # Add document prefix (if exists)
        if settings.EMBEDDING_DOCUMENT_PREFIX is not None:
            content = settings.EMBEDDING_DOCUMENT_PREFIX + content

        # Create a document
        document = Document(page_content=content, metadata={"file": path.name})
        documents.append(document)

    # Save the documents to chroma
    logger.info(f"Loading {len(documents)} texts into Chroma DB...")
    db.add_documents(documents=documents)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    main()
