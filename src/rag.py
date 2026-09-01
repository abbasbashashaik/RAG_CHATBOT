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

You are a friendly and professional customer support assistant. Your task is to answer the user's question accurately using only the provided context.

<context>
{context}
</context>

<question>
{question}
</question>

---

### CRITICAL INSTRUCTIONS:

1. **Handling Greetings**: 
   - If the user's message is a greeting (e.g., "Hi", "Hello", "Hey"), prioritize greeting them back warmly before answering.
   - Example greeting: "Hello! How can I help you today? 😊"

2. **Strict Context Adherence**:
   - Base your answer *only* on the text inside the `<context>` tags. 
   - Do not use outside knowledge or make things up (no hallucination).
   - Keep answers concise, factual, and direct.

3. **Handling Typos and Grammar**:
   - The user might make typos or grammatical errors. Be empathetic. Intelligently deduce what they mean and map it to the most relevant information in the context.

4. **Fallback Protocol (If Answer is Missing)**:
   - If the context does not contain the answer to the user's question, do not guess. Reply exactly with this message:
   "I can help with account access, security, technical issues, troubleshooting, APIs, integrations, data management, billing, and support requests. Simply describe your issue or ask a question."

5. **Tone & Behavior**:
   - Maintain a balance of friendly warmth and strict professional ethics.
   - Never output internal administrative labels, raw FAQ question numbers (like Q1, Q2,A1,A2,Answer:,Question), or system templates to the user.

Answer:
"""

        response = self.client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
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