from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import upload, query, pdf


# -------------------- Application Initialization -------------------- #

app = FastAPI(
    title="Secure Document Intelligence API",
    description="""
Secure Document Intelligence API provides AI-powered document processing 
and question-answering capabilities using Retrieval-Augmented Generation (RAG).

Authentication
--------------
All protected endpoints require authentication using a Bearer token.

To authorize requests:
1. Click the **Authorize** button in Swagger UI.
2. Enter your token (example):

   YOUR_SECRET_TOKEN

3. Click "Authorize" and close the dialog.

After authorization, the token will be automatically included in subsequent requests.

Available Features
------------------
1. Document Question Answering (RAG)
   - Upload PDF documents
   - Submit contextual questions
   - Receive AI-generated answers with source references

2. Text-to-PDF Generation
   - Submit text content with file name
   - Generate a downloadable PDF document


""",
    version="1.0.0",
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