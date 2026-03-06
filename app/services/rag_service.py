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

    def __init__(self):
        # Track the latest uploaded document
        self.current_document = None

    def ingest_pdf(self, file_path: str):
        """
        Extract text page-by-page, create embeddings,
        and store structured chunks with metadata.
        """
        reader = PdfReader(file_path)
        filename = os.path.basename(file_path)

        # Set current document
        self.current_document = filename

        total_chunks = 0

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()

            if not page_text or not page_text.strip():
                continue

            # Chunk per page
            chunks = [page_text[i:i+500] for i in range(0, len(page_text), 500)]

            for chunk_index, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                embedding = get_embedding(chunk)

                unique_string = f"{filename}_{page_number}_{chunk_index}"
                chunk_id = hashlib.md5(unique_string.encode()).hexdigest()

                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "document": filename,
                        "page": page_number,
                        "chunk_index": chunk_index
                    }]
                )

                total_chunks += 1

        print(f"Stored {total_chunks} structured chunks in ChromaDB")

    def search(self, query: str, k: int = 3):
        """
        Perform semantic search only on the latest uploaded document.
        """
        if not query.strip():
            return []

        query_embedding = [get_embedding(query)]

        # Filter by latest uploaded document
        if self.current_document:
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=k,
                where={"document": self.current_document}
            )
        else:
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=k
            )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        structured_results = []

        for doc, meta in zip(documents, metadatas):
            structured_results.append({
                "content": doc,
                "document": meta.get("document"),
                "page": meta.get("page"),
                "chunk_index": meta.get("chunk_index")
            })

        return structured_results