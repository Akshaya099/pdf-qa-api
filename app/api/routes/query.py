from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import List
from pydantic import BaseModel
from app.services.rag_service import RAGEngine
from app.services.llm_service import generate_answer
from app.api.deps import verify_token

router = APIRouter(
    prefix="/query",
    tags=["Question Answering"]
)

rag = RAGEngine()


# -------------------- Response Models -------------------- #

class SourceMetadata(BaseModel):
    document: str
    page: int
    chunk_index: int


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceMetadata]


# -------------------- Endpoint -------------------- #

@router.post(
    "/",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about the uploaded document",
    description="""
Submit a question related to a previously uploaded PDF document.

Steps:
1. Ensure a PDF has been uploaded using the /upload endpoint.
2. Enter your question in the input field below.
3. Click "Execute" to receive the AI-generated answer with source references.
""",
    responses={
        200: {"description": "Successful response"},
        401: {"description": "Unauthorized - Invalid or missing token"},
        404: {"description": "No relevant content found"},
        500: {"description": "Internal server error"}
    }
)
async def ask_question(
    question: str = Form(
    ...,
    min_length=5,
    description="""
Enter your question related to the uploaded document.

Example:
Summarize the key objectives mentioned in the document.
"""),
    _: str = Depends(verify_token)
):
    try:
        results = rag.search(question)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant content found. Please upload a document first."
            )

        # Build context from structured RAG output
        context = "\n".join([r["content"] for r in results])

        answer = generate_answer(context, question)

        return QueryResponse(
            question=question,
            answer=answer,
            sources=[
                SourceMetadata(
                    document=r["document"],
                    page=r["page"],
                    chunk_index=r["chunk_index"]
                )
                for r in results
            ]
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query processing failed."
        )