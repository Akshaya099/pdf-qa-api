from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb


model = SentenceTransformer("all-MiniLM-L6-v2")


client = chromadb.PersistentClient(path="./chroma_db")


collection = client.get_or_create_collection(name="pdf_documents")


class RAGEngine:
    def ingest_pdf(self, file_path):
        reader = PdfReader(file_path)

        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

      
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        embeddings = model.encode(chunks)

        
        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{file_path}_{i}"],
                embeddings=[embeddings[i]],
                documents=[chunk],
                metadatas=[{"source": file_path}] 
            )
        #return len(chunks)  
        print(f"Stored {len(chunks)} chunks in ChromaDB")  

    def search(self, query, k=3):
        query_embedding = model.encode([query])

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )

        return results["documents"][0]
  