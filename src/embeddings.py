from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .config import EMBEDDING_MODEL, GEMINI_API_KEY


def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=GEMINI_API_KEY
    )