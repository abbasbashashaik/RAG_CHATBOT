#rag.py
from google import genai
from google.genai import types

from .config import (
    FAISS_INDEX_PATH,
    GENERATION_MODEL,
    GEMINI_API_KEY,
    METADATA_PATH,
    TOP_K,
)
from .embeddings import get_embedding_model
from .ingest import load_and_chunk_document
from .vectorstore import (
    create_vector_store,
    load_vector_store,
    search_vector_store,
    vector_store_exists,
)


class RAGPipeline:

    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        self.embedding_model = get_embedding_model()

        self.index = None
        self.chunks = None

    def initialize(self):
        """
        Load an existing vector store.
        If it doesn't exist, create it.
        """

        if vector_store_exists(
            FAISS_INDEX_PATH,
            METADATA_PATH,
        ):
            self.index, self.chunks = load_vector_store(
                FAISS_INDEX_PATH,
                METADATA_PATH,
            )

            return

        self.chunks = load_and_chunk_document()

        vectors = self.embedding_model.embed_documents(
            self.chunks
        )

        create_vector_store(
            chunks=self.chunks,
            vectors=vectors,
            index_path=FAISS_INDEX_PATH,
            metadata_path=METADATA_PATH,
        )

        self.index, self.chunks = load_vector_store(
            FAISS_INDEX_PATH,
            METADATA_PATH,
        )

    def retrieve(self, question: str):
        """Retrieve relevant chunks for the question."""

        question_vector = self.embedding_model.embed_query(
            question
        )

        results = search_vector_store(
            index=self.index,
            chunks=self.chunks,
            query_vector=question_vector,
            top_k=TOP_K,
        )

        return results

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: list[dict],
    ) -> str:
        """Generate an answer using retrieved context."""

        context = "\n\n".join(
            result["chunk"]
            for result in retrieved_chunks
        )

        prompt = f"""

Context:
{context}

Question:
{question}

Answer the question using the provided context.and greet user when he input like hi hello type of things.

Rules:
- Do not hallucinate.
- understand the spelling mistakes and grammer mistakes and try to find the better suitable answer based on the query context from the provided information.
- Do not use information outside the context.
- And also try to greet the user like how can i help you [place here with any emojis] when he texts you as like [Hi,hello]
- If the answer is not present in the context, say:
  " I can help with account access, security, technical issues, troubleshooting, APIs, integrations, data management, billing, and support requests.
    Simply describe your issue or ask a question."
- be friendly with the user and also maintain profession ethics.
- Keep the answer concise.

Answer:
"""

        response = self.client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
                ),

            ),
        )

        return response.text.strip()

    def ask(self, question: str) -> str:
        """Complete RAG pipeline."""

        retrieved_chunks = self.retrieve(question)

        return self.generate_answer(
            question,
            retrieved_chunks,
        )