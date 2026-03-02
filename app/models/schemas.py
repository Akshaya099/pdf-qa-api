from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class PDFRequest(BaseModel):
    text: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)