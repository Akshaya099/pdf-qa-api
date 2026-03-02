from pypdf import PdfReader
import chromadb
import os
import hashlib
from openai import OpenAI

# -------------------- OpenRouter Client -------------------- #

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set")

client_openai = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def get_embedding(text: str):
    """
    Generate embeddings using OpenRouter API.
    """
    try:
        response = client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {e}")


# -------------------- Vector Database -------------------- #

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="pdf_documents")


# -------------------- RAG Engine -------------------- #

class RAGEngine:
    """
    Handles PDF ingestion and semantic search.
    """

    def ingest_pdf(self, file_path: str):
        """
        Extract text from PDF, create embeddings,
        and store chunks in ChromaDB.
        """
        reader = PdfReader(file_path)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise ValueError("No readable text found in PDF.")

        # split into chunks (better boundary handling)
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        for chunk in chunks:
            if not chunk.strip():
                continue

            embedding = get_embedding(chunk)

            # create stable ID using hash (prevents duplicates)
            chunk_id = hashlib.md5(chunk.encode()).hexdigest()

            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": os.path.basename(file_path)}]
            )

        print(f"Stored {len(chunks)} chunks in ChromaDB")

    def search(self, query: str, k: int = 3):
        """
        Perform semantic search on stored document chunks.
        """
        if not query.strip():
            return []

        query_embedding = [get_embedding(query)]

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        return results.get("documents", [[]])[0]