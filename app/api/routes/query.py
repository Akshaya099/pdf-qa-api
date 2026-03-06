from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import List
from pydantic import BaseModel
from app.services.rag_instance import rag
from app.services.llm_service import generate_answer
from app.api.deps import verify_token

router = APIRouter(
    prefix="/query",
    tags=["Question Answering"]
)

# Initialize RAG engine



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

The system performs semantic search over the indexed document and
uses an AI model to generate an answer with source references.

Authentication
--------------
This endpoint requires Bearer Token authentication.

```http
Authorization: Bearer YOUR_API_TOKEN
```
Base URL
--------
```http
https://pdf-qa-api-indol.vercel.app
```
Endpoint
--------
```http
POST https://pdf-qa-api-indol.vercel.app/query/
```
Headers
-------
```http
Authorization: Bearer YOUR_API_TOKEN
Content-Type: multipart/form-data
```
Example Request
---------------

```http
question = What is this document about?
```
Example Response
---------------

```json
{
  "question": "What is this document about?",
  "answer": "The document describes the fundamentals of RAG (Retrieval Augmented Generation).",
  "sources": [
    {
      "document": "RAG_Technology.pdf",
      "page": 2,
      "chunk_index": 5
    }
  ]
}

""",
    responses={
        200: {
            "description": "Successful response"
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
        404: {
            "description": "No relevant content found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No relevant content found. Please upload a document first."
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Query processing failed."
                    }
                }
            }
        }
    }
)
async def ask_question(
    question: str = Form(
        ...,
        min_length=5,
        description="Enter a question related to the uploaded document."
    ),
    _: str = Depends(verify_token)
):
    try:
        # Perform semantic search
        results = rag.search(question)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant content found. Please upload a document first."
            )

        # Build context for LLM
        context = "\n".join([r["content"] for r in results])

        # Generate answer using LLM
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

    except Exception as e:
        print("Query Error:", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query processing failed."
        )