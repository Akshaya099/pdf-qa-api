from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Form
from fastapi.responses import FileResponse
from app.services.pdf_service import create_pdf
from app.api.deps import verify_token
import os

router = APIRouter(
    prefix="/pdf",
    tags=["PDF Utilities"]
)


# -------------------- Cleanup Helper -------------------- #

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)


# -------------------- Endpoint -------------------- #

@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    summary="Generate a PDF from raw text",
    description="""
Convert raw text into a downloadable PDF file.

Steps:
1. Enter the text content you want to convert.
2. Provide a filename (without .pdf extension).
3. Submit the request to generate and download the PDF.
""",
    responses={
        200: {
            "description": "PDF generated successfully",
            "content": {"application/pdf": {}}
        },
        401: {"description": "Unauthorized - Invalid or missing token"},
        500: {"description": "Internal server error"}
    }
)
def generate_pdf(
    background_tasks: BackgroundTasks,
    content: str = Form(
        ...,
        min_length=1,
        description="""
Raw text content to convert into a PDF document.

Example:
This is a sample paragraph.

You can paste large raw text here to generate a downloadable PDF file.
"""
    ),
    filename: str = Form(
        ...,
        min_length=1,
        description="""
Desired name of the output PDF file (without extension).

Example:
my_document
"""
    ),
    _: str = Depends(verify_token)
):
    try:
        filename = filename.strip()

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        file_path = create_pdf(content, filename)

        # Schedule automatic deletion after response is sent
        background_tasks.add_task(remove_file, file_path)

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF generation failed."
        )