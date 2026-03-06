from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import upload, query, pdf, upload_file


# -------------------- Application Initialization -------------------- #

app = FastAPI(
    title="Secure Document Intelligence API",
    description="""
Secure Document Intelligence API provides AI-powered document processing
and question-answering capabilities using Retrieval-Augmented Generation (RAG).

Base URL
--------
```http
https://pdf-qa-api-indol.vercel.app
```
Available Features
------------------
1. Document Question Answering (RAG)
- Upload PDF documents for indexing
- Ask questions related to uploaded documents
- Receive AI-generated answers with source references

2. Text-to-PDF Generation
- Convert raw text into a downloadable PDF file
- Specify a custom filename
""",
    version="1.0.1",
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1
    }
)


# -------------------- CORS Configuration -------------------- #

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pdf-qa-api-indol.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Router Registration -------------------- #


app.include_router(upload.router)
app.include_router(query.router)
app.include_router(pdf.router)
app.include_router(upload_file.router)