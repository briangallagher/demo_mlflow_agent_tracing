from demo_mlflow_agent_tracing.constants import WIKI_PATH, DB_PATH
from langchain_text_splitters import MarkdownHeaderTextSplitter
import frontmatter
from langchain_chroma import Chroma

def ingest():
    
    # Load all pages as documents
    paths = WIKI_PATH.glob("*.md")
    docs = []
    for path in paths:
        # Get the file content and metadata
        content = path.read_text()
        metadata = frontmatter.loads(content)
        metadata["path"] = path.as_posix()
        metadata["filename"] = path.name
        
        # Chunk each document
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=True)
        chunks = splitter.split_text(content)
        
        # Update the metadata of each chunk
        for chunk in chunks:
            chunk.metadata = chunk.metadata | metadata
        
        docs.extend(chunks)
        
    # Save the chunks to a new chroma collection
    db = Chroma(persist_directory=DB_PATH)
    db.reset_collection()
    db.add_documents(documents=docs)
        
    return docs

if __name__ == "__main__":
    ingest()