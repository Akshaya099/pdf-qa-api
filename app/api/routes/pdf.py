from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.services.pdf_service import create_pdf
from app.api.deps import verify_token

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


@router.post("/create")
def generate_pdf(
    text: str = Form(...),
    filename: str = Form(...),
    _: str = Depends(verify_token)
):
    """
    Generate a PDF from provided text and return it as a download.
    """
    try:
        file_path = create_pdf(text, filename)

        # ensure extension
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