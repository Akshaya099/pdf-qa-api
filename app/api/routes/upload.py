from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
import tempfile
import os

from app.services.rag_instance import rag

from app.api.deps import verify_token

router = APIRouter(
    prefix="/upload",
    tags=["Document Management"]
)




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
Upload a PDF document to index it for semantic search.

After successful upload and processing, the document will be stored in the vector
database and will be available for AI-powered question answering.

Authentication
--------------
This endpoint requires Bearer Token authentication.

Header:
```http
Authorization: Bearer YOUR_API_TOKEN
```
Base URL
--------
```http
https://pdf-qa-api-indol.vercel.app
```
Example Request
---------------

```http
POST https://pdf-qa-api-indol.vercel.app/upload/
Authorization: Bearer YOUR_API_TOKEN
Content-Type: multipart/form-data

content=This is a sample paragraph
filename=test

pdf_file=@document.pdf

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
            "description": "Document uploaded and processed successfully",
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
            "description": "Invalid file format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Only PDF files are allowed."
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or missing authentication token."
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File processing failed."
                    }
                }
            }
        }
    }
)
async def upload_pdf(
    pdf_file: UploadFile = File(
        ...,
        description="Upload a PDF document that will be indexed for semantic search and question answering."
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

        # Process document using RAG engine
        rag.ingest_pdf(file_path)

        # Remove temporary file
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