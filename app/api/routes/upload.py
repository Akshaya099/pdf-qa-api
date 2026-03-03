from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
import tempfile
import os

from app.services.rag_service import RAGEngine
from app.api.deps import verify_token

router = APIRouter(
    prefix="/upload",
    tags=["Document Management"]
)

rag = RAGEngine()


# -------------------- Response Model -------------------- #

class UploadResponse(BaseModel):
    message: str
    status: str


# -------------------- Endpoint -------------------- #

@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF document",
    description="""
Upload a PDF file to index it for semantic search.

After successful upload and processing,
the document will be available for querying.

How to Upload:

- Use the "Choose File" button below.
- Select a PDF file from your system.
- Click "Execute" to upload and process the document.

Only PDF files are supported.
""",
    responses={
        201: {"description": "Document uploaded and processed successfully"},
        400: {"description": "Invalid file format"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        500: {"description": "Internal server error"}
    }
)
async def upload_pdf(
    pdf_file: UploadFile = File(
        ...,
        description="Select a PDF document to upload and index for semantic search."
    ),
    _: str = Depends(verify_token)
):
    try:
        # Validate file type
        if not pdf_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed."
            )

        # Save file temporarily
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, pdf_file.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await pdf_file.read())

        # Process document
        rag.ingest_pdf(file_path)

        # Remove temp file after ingestion
        if os.path.exists(file_path):
            os.remove(file_path)

        return UploadResponse(
            message="PDF uploaded and processed successfully.",
            status="Document is ready for querying."
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File processing failed."
        )