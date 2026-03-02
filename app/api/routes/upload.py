from fastapi import APIRouter, UploadFile, File, Depends
import tempfile
import os

from app.services.rag_service import RAGEngine
from app.api.deps import verify_token

router = APIRouter(prefix="/upload", tags=["Upload"])

rag = RAGEngine()


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...),
    _: str = Depends(verify_token)
):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    rag.ingest_pdf(file_path)

    return {"message": "PDF uploaded and processed"}