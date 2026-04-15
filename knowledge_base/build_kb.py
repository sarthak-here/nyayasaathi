"""
NyayaSaathi — Knowledge Base Builder
Indexes legal documents from knowledge_base/docs/ into ChromaDB.
Run this once before starting the app.
"""

import os
import glob
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DOCS_PATH = os.getenv("DOCS_PATH", "./knowledge_base/docs")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHUNK_SIZE = 400       # tokens (~1600 chars)
CHUNK_OVERLAP = 50     # tokens (~200 chars)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents(docs_path: str) -> list[dict]:
    """Load all .txt files from the docs folder."""
    docs = []
    txt_files = glob.glob(os.path.join(docs_path, "*.txt"))

    if not txt_files:
        print(f"[!] No .txt files found in {docs_path}")
        return docs

    for filepath in txt_files:
        filename = Path(filepath).stem
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        docs.append({"filename": filename, "content": content, "path": filepath})
        print(f"    Loaded: {filename} ({len(content)} chars)")

    return docs


def chunk_documents(docs: list[dict]) -> list[dict]:
    """Split documents into overlapping chunks using LangChain text splitter."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    # Approximate: 1 token ≈ 4 chars
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE * 4,
        chunk_overlap=CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    for doc in docs:
        split_texts = splitter.split_text(doc["content"])
        for i, text in enumerate(split_texts):
            chunks.append({
                "id": f"{doc['filename']}_chunk_{i}",
                "text": text,
                "metadata": {
                    "source": doc["filename"],
                    "filepath": doc["path"],
                    "chunk_index": i,
                    "total_chunks": len(split_texts),
                }
            })

    return chunks


def build_knowledge_base(docs_path: str = DOCS_PATH, db_path: str = CHROMA_DB_PATH):
    """Main function to build ChromaDB from legal documents."""
    import chromadb
    from chromadb.utils import embedding_functions

    print("=" * 60)
    print("NyayaSaathi — Legal Knowledge Base Builder")
    print("=" * 60)

    # Load documents
    print(f"\n[1/4] Loading documents from: {docs_path}")
    docs = load_documents(docs_path)
    if not docs:
        print("No documents found. Please add .txt files to knowledge_base/docs/")
        return

    print(f"      -> {len(docs)} documents loaded")

    # Chunk documents
    print(f"\n[2/4] Chunking documents ({CHUNK_SIZE} tokens, {CHUNK_OVERLAP} overlap)...")
    chunks = chunk_documents(docs)
    print(f"      -> {len(chunks)} chunks created")

    # Set up embeddings
    print(f"\n[3/4] Loading embedding model: {EMBED_MODEL}")
    print("      (Downloading model on first run — will be cached locally)")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    # Build ChromaDB
    print(f"\n[4/4] Indexing into ChromaDB at: {db_path}")
    client = chromadb.PersistentClient(path=db_path)

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("legal_docs")
        print("      Deleted existing collection (rebuilding)")
    except Exception:
        pass

    collection = client.create_collection(
        name="legal_docs",
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Index in batches of 100
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"      Indexed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks...", end="\r")

    print(f"\n\n{'=' * 60}")
    print(f"Knowledge base built successfully!")
    print(f"  Documents indexed : {len(docs)}")
    print(f"  Total chunks      : {len(chunks)}")
    print(f"  Database location : {db_path}")
    print(f"{'=' * 60}")

    # Quick test
    print("\n[Test] Running sample query: 'wage theft salary not paid'")
    results = collection.query(query_texts=["wage theft salary not paid"], n_results=2)
    for j, doc in enumerate(results["documents"][0]):
        src = results["metadatas"][0][j]["source"]
        print(f"  Result {j+1} [{src}]: {doc[:120]}...")

    return collection


if __name__ == "__main__":
    build_knowledge_base()
