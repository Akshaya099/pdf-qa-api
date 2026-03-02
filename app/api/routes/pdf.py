from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.services.pdf_service import create_pdf
from app.api.deps import verify_token

router = APIRouter(
    prefix="/pdf",
    tags=["Text2PDF"]
)


@router.post(
    "/create",
    summary="Generate PDF from text",
    description="""
🔐 **Authentication Required**

Enter text and a file name to create and download a PDF.

**Note:**
    Without authentication, the PDF will NOT be generated.
"""
)
def generate_pdf(
    text: str = Form(
        ...,
        description="Enter the text content to be converted into PDF"
    ),
    filename: str = Form(
        ...,
        description="Enter the desired name for the PDF file"
    ),
    _: str = Depends(verify_token)
):
    """
    Generate a PDF from provided text and return it as a downloadable file.
    """

    try:
        file_path = create_pdf(text, filename)

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )