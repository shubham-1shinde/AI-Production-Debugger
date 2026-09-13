from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "gstassistant_code"
EMBEDDING_SIZE = 384

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(path=QDRANT_PATH)

_vector_store = None


def collection_exists():
    collections = client.get_collections()

    return any(
        collection.name == COLLECTION_NAME
        for collection in collections.collections
    )


def create_collection():
    if collection_exists():
        return

    print(
        f"Creating Qdrant collection: {COLLECTION_NAME}"
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print("Qdrant collection created successfully.")


def get_vector_store():
    global _vector_store

    if _vector_store is None:
        create_collection()

        _vector_store = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
        )

    return _vector_store


def create_store_from_documents(documents):
    global _vector_store

    if not documents:
        return

    print(
        f"Creating Qdrant store with {len(documents)} chunks..."
    )

    create_collection()

    _vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

    _vector_store.add_documents(
        documents=documents
    )

    print(
        "Qdrant vector store created successfully."
    )


def add_documents(documents):
    if not documents:
        return

    global _vector_store

    if not collection_exists():
        create_store_from_documents(documents)
        return

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=documents
    )

    print("Qdrant update completed.")


def delete_file_vectors(file_path):
    if not collection_exists():
        return

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="metadata.path",
                    match=MatchValue(
                        value=file_path
                    )
                )
            ]
        )
    )


def get_documents_by_file(
    file_path: str,
    limit: int = 100
):
    """
    Retrieve ALL stored chunks belonging to an exact file.
    This does not use semantic similarity.
    """

    if not collection_exists():
        return []

    if not file_path:
        return []

    print(
        f"\nExact file retrieval: {file_path}"
    )

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,

        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.path",
                    match=MatchValue(
                        value=file_path
                    )
                )
            ]
        ),

        limit=limit,

        with_payload=True,
        with_vectors=False,
    )

    documents = []

    for point in points:

        payload = point.payload or {}

        page_content = payload.get(
            "page_content",
            ""
        )

        metadata = payload.get(
            "metadata",
            {}
        )

        if page_content:
            documents.append(
                Document(
                    page_content=page_content,
                    metadata=metadata
                )
            )

    print(
        f"Exact file chunks found: {len(documents)}"
    )

    return documents


def get_retriever(k=8):
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_kwargs={
            "k": k
        }
    )


def get_semantic_documents(
    query: str,
    k: int = 8
):
    """
    Perform normal semantic vector retrieval.
    """

    if not query:
        return []

    retriever = get_retriever(k)

    documents = retriever.invoke(
        query
    )

    return documents


def close_qdrant():
    try:
        client.close()
    except Exception:
        pass