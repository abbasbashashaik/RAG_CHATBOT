#vectorstore.py

import pickle
from pathlib import Path

import faiss
import numpy as np


def create_vector_store(
    chunks: list[str],
    vectors: list[list[float]],
    index_path: Path,
    metadata_path: Path,
) -> None:
    """Create and persist a FAISS vector store."""

    index_path.parent.mkdir(parents=True, exist_ok=True)

    vector_array = np.asarray(vectors, dtype=np.float32)

    dimension = vector_array.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vector_array)

    faiss.write_index(index, str(index_path))

    with open(metadata_path, "wb") as file:
        pickle.dump(chunks, file)


def load_vector_store(
    index_path: Path,
    metadata_path: Path,
):
    """Load a persisted FAISS index and its chunks."""

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "rb") as file:
        chunks = pickle.load(file)

    return index, chunks


def vector_store_exists(
    index_path: Path,
    metadata_path: Path,
) -> bool:
    """Check whether the persisted vector store exists."""

    return index_path.exists() and metadata_path.exists()


def search_vector_store(
    index,
    chunks: list[str],
    query_vector: list[float],
    top_k: int,
):
    """Search the FAISS index and return the most relevant chunks."""

    query = np.asarray(query_vector, dtype=np.float32)
    query = query.reshape(1, -1)

    distances, indices = index.search(query, top_k)

    results = []

    for distance, index_id in zip(distances[0], indices[0]):
        if index_id == -1:
            continue

        results.append(
            {
                "chunk": chunks[index_id],
                "distance": float(distance),
                "index": int(index_id),
            }
        )

    return results