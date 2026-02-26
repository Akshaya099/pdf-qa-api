from pypdf import PdfReader

# ❌ REMOVE local embedding model (too heavy for serverless)
# from sentence_transformers import SentenceTransformer

import chromadb
import os
from openai import OpenAI


# ❌ Local model initialization (causes 7GB deployment)
# model = SentenceTransformer("all-MiniLM-L6-v2")


# ✅ OpenRouter / OpenAI compatible client
client_openai = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ✅ Function to generate embeddings using OpenRouter API
def get_embedding(text):
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",  # lightweight & fast
        input=text
    )
    return response.data[0].embedding


# ChromaDB persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="pdf_documents")


class RAGEngine:
    def ingest_pdf(self, file_path):
        reader = PdfReader(file_path)

        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

        # split text into chunks
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        # ❌ OLD local embeddings
        # embeddings = model.encode(chunks)

        # ✅ NEW API embeddings
        embeddings = [get_embedding(chunk) for chunk in chunks]

        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{file_path}_{i}"],
                embeddings=[embeddings[i]],
                documents=[chunk],
                metadatas=[{"source": file_path}]
            )

        print(f"Stored {len(chunks)} chunks in ChromaDB")

    def search(self, query, k=3):
        # ❌ OLD local embedding
        # query_embedding = model.encode([query])

        # ✅ NEW API embedding
        query_embedding = [get_embedding(query)]

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        return results["documents"][0]