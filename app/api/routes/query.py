from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.rag_service import RAGEngine
from app.services.llm_service import generate_answer
from app.api.deps import verify_token

router = APIRouter(
    prefix="/query",
    tags=["Query"]
)

rag = RAGEngine()


@router.post(
    "/",
    summary="Ask questions from uploaded documents",
    description="""
🔐 **Authentication Required**

Ask questions based on the PDF you uploaded.

**Note:**

• Documents must be uploaded before querying.  
• Without authentication, the request will NOT be processed.
"""
)
async def ask_question(
    question: str = Query(
        ...,
        description="Enter your question related to the uploaded document"
    ),
    _: str = Depends(verify_token)
):
    """
    Retrieve relevant document content and generate an AI-based answer.
    """

    try:
        # Retrieve relevant chunks
        chunks = rag.search(question)

        if not chunks:
            return {
                "answer": "No relevant content found. Please upload a document first."
            }

        context = "\n".join(chunks)

        # Generate AI response
        answer = generate_answer(context, question)

        return {
            "question": question,
            "answer": answer,
            "source": "Generated from uploaded document context"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )