from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import base64
import tempfile
import os
import uuid

from app.services.rag_instance import rag
from app.api.deps import verify_token

router = APIRouter(
    prefix="/upload-file",
    tags=["Document Management"]
)




# -------------------- Request Model -------------------- #

class Base64FileUpload(BaseModel):
    filename: str
    file_data: str


# -------------------- Response Model -------------------- #

class UploadResponse(BaseModel):
    message: str
    status: str


# -------------------- Endpoint -------------------- #

@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF using Base64 encoding",
    description="""
Upload a PDF file using JSON format with Base64 encoding.

Authentication
--------------
```http
Authorization: Bearer YOUR_API_TOKEN
```
Example Request
---------------
```json
{
  "filename": "document.pdf",
  "file_data": "JVBERi0xLjQKJcfs..."
}
```
Example Response
----------------
```json
{
  "message": "PDF uploaded and processed successfully.",
  "status": "Document is ready for querying."
}
""",
    responses={
        201: {
            "description": "Document uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "PDF uploaded and processed successfully.",
                        "status": "Document is ready for querying."
                    }
                }
            }
        },
        400: {
            "description": "Invalid file format or Base64 data"
        },
        401: {
            "description": "Unauthorized - Invalid or missing token"
        },
        500: {
            "description": "Internal server error"
        }
    }
)

async def upload_file_base64(
    payload: Base64FileUpload,
    _: str = Depends(verify_token)
):

    try:
        # Validate file extension
        if not payload.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed."
            )

        # Decode Base64 file
        try:
            file_bytes = base64.b64decode(payload.file_data, validate=True)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Base64 encoded file."
            )

        # Optional file size check (10MB limit)
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit."
            )

        # Create unique temporary file path
        temp_dir = tempfile.gettempdir()
        unique_filename = f"{uuid.uuid4()}_{payload.filename}"
        file_path = os.path.join(temp_dir, unique_filename)

        # Save decoded file
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Process document with RAG pipeline
        rag.ingest_pdf(file_path)
        rag.current_document = os.path.basename(file_path)
        # Remove temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

        return UploadResponse(
            message="PDF uploaded in form of JSON and processed successfully.",
            status="Document is ready for querying."
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )