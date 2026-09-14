import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue


QDRANT_PATH = "../qdrant_data"
EMBEDDING_SIZE = 384

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    path=QDRANT_PATH
)

# Cache vector stores by repository
_vector_stores = {}

def get_collection_name(repo: str) -> str:
    """
    Generate a unique Qdrant collection name for a repository.
    """

    safe_repo = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        repo
    )

    return f"repo_{safe_repo.lower()}"


def collection_exists(repo: str) -> bool:
    """
    Check whether the Qdrant collection for the repository exists.
    """

    collection_name = get_collection_name(repo)

    collections = client.get_collections()

    return any(
        collection.name == collection_name
        for collection in collections.collections
    )


def create_collection(repo: str):
    """
    Create a Qdrant collection for the repository if it does not exist.
    """

    collection_name = get_collection_name(repo)

    if collection_exists(repo):
        return

    print(f"Creating Qdrant collection: {collection_name}")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print("Qdrant collection created successfully.")


def get_vector_store(repo: str):
    """
    Get the Qdrant vector store for a specific repository.
    """

    collection_name = get_collection_name(repo)

    if repo not in _vector_stores:

        create_collection(repo)

        _vector_stores[repo] = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

    return _vector_stores[repo]


def create_store_from_documents(documents, repo: str):
    """
    Create a vector store and add documents for a repository.
    """

    if not documents:
        return

    collection_name = get_collection_name(repo)

    print(f"Creating Qdrant store with {len(documents)} chunks...")

    create_collection(repo)

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    
    vector_store.add_documents(documents=documents)
    
    _vector_stores[repo] = vector_store
    
    print("Qdrant vector store created successfully.")


def add_documents(documents, repo: str):
    """
    Add documents to the Qdrant collection belonging to the repository.
    """

    if not documents:
        return

    if not collection_exists(repo):
        create_store_from_documents(documents, repo)
        return

    vector_store = get_vector_store(repo)
    vector_store.add_documents(documents=documents)

    print(f"Qdrant update completed for: {repo}")


def delete_file_vectors(file_path: str, repo: str):
    """
    Delete all vectors belonging to a specific file
    from the repository's Qdrant collection.
    """

    if not collection_exists(repo):
        return

    collection_name = get_collection_name(repo)
    
    client.delete(
        collection_name=collection_name,
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
    print(
        f"Deleted vectors for {file_path} "
        f"from {collection_name}"
    )


def get_documents_by_file(file_path: str, repo: str, limit: int = 100):
    """
    Retrieve all stored chunks belonging to an exact file.
    This does not use semantic similarity.
    """

    if not collection_exists(repo):
        return []

    if not file_path:
        return []

    collection_name = get_collection_name(repo)
    print(f"\nExact file retrieval: {file_path}")

    points, _ = client.scroll(
        collection_name=collection_name,
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
        page_content = payload.get("page_content", "")
        metadata = payload.get("metadata", {})

        if page_content:

            documents.append(
                Document(
                    page_content=page_content,
                    metadata=metadata
                )
            )

    print(f"Exact file chunks found: {len(documents)}")
    return documents


def get_retriever(repo: str, k: int = 8):
    """
    Get a semantic retriever for a repository.
    """

    vector_store = get_vector_store(repo)

    return vector_store.as_retriever(
        search_kwargs={"k": k}
    )


def get_semantic_documents(query: str, repo: str, k: int = 8):
    """
    Perform semantic vector retrieval
    from the repository's collection.
    """

    if not query:
        return []
    retriever = get_retriever(repo, k)
    documents = retriever.invoke(query)
    return documents

def close_qdrant():
    """
    Close the Qdrant client.
    """

    try:
        client.close()

    except Exception:
        pass