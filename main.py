from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
import os
from rag_engine import RAGEngine
from llm import generate_answer

app = FastAPI()


rag = RAGEngine()


security = HTTPBearer()


API_TOKEN = os.getenv("APP_SECRET_TOKEN")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    if token != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access. Please provide a valid authentication token."
        )


@app.post("/upload", dependencies=[Depends(verify_token)])
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    rag.ingest_pdf(file_path)

    return {
        "authenticated": True,
        "message": "PDF uploaded and processed successfully"
    }



@app.post("/ask", dependencies=[Depends(verify_token)])
async def ask_question(question: str):
    chunks = rag.search(question)
    context = "\n".join(chunks)

    answer = generate_answer(context, question)

    return {
        "authenticated": True,
        "answer": answer
    }