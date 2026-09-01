# config.py

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

DOCUMENT_PATH = DATA_DIR / "dataset.txt"
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss.index"
METADATA_PATH = VECTOR_STORE_DIR / "metadata.pkl"

GEMINI_API_KEY =os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-2"
GENERATION_MODEL = "gemini-3.6-flash"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

TOP_K = 5


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")