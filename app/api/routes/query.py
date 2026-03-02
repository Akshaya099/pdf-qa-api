from fastapi import APIRouter, Depends
from app.services.rag_service import RAGEngine
from app.services.llm_service import generate_answer
from app.api.deps import verify_token

router = APIRouter(prefix="/query", tags=["Query"])

rag = RAGEngine()


@router.post("/")
async def ask_question(question: str, _: str = Depends(verify_token)):
    chunks = rag.search(question)
    context = "\n".join(chunks)

    answer = generate_answer(context, question)

    return {"answer": answer}