# ingest.py

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENT_PATH,
)


def load_document() -> str:
    """Load the source document."""

    loader = TextLoader(str(DOCUMENT_PATH))
    documents = loader.load()

    return documents[0].page_content


def create_chunks(text: str) -> list[str]:
    """Split document into overlapping chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_text(text)


def load_and_chunk_document() -> list[str]:
    """Load document and split it into chunks."""

    text = load_document()

    return create_chunks(text)