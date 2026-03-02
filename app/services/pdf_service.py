import os
import re
import tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Use temporary directory for serverless environments
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "generated_files")


def sanitize_filename(name: str) -> str:
    """
    Remove unsafe characters from filename.
    """
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "", name)


def create_pdf(text: str, filename: str) -> str:
    """
    Generate a PDF from text content and save it to disk.
    Returns the file path.
    """

    if not text.strip():
        raise ValueError("Text content cannot be empty.")

    # ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # sanitize filename
    filename = sanitize_filename(filename)

    # ensure .pdf extension
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    file_path = os.path.join(OUTPUT_DIR, filename)

    # create PDF document
    doc = SimpleDocTemplate(
        file_path,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    # convert text into paragraphs
    for line in text.split("\n"):
        clean_line = line.strip()
        if clean_line:
            content.append(Paragraph(clean_line, styles["Normal"]))
            content.append(Spacer(1, 10))

    # build PDF
    doc.build(content)

    return file_path