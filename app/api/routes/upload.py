from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import tempfile
import os

from app.services.rag_service import RAGEngine
from app.api.deps import verify_token

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

rag = RAGEngine()


@router.post(
    "/",
    summary="Upload PDF document",
    description="""
🔐 **Authentication Required**

Upload your PDF to start searching and asking questions

Only authorized requests will be processed.


"""
)
async def upload_pdf(
    file: UploadFile = File(
        ...,
        description="Upload PDF file (required)"
    ),
    _: str = Depends(verify_token)
):
    """
    Upload a PDF file and process it for semantic search.
    """

    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # Save file temporarily (serverless-safe)
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Process and index document
        rag.ingest_pdf(file_path)

        return {
            "message": "PDF uploaded and processed successfully",
            "status": "Document is ready for querying"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )