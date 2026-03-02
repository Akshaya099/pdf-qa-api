from openai import OpenAI
import os

# -------------------- OpenRouter / OpenAI Client -------------------- #

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in environment variables")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def generate_answer(context: str, question: str) -> str:
    """
    Generate an answer using the provided context.
    Ensures responses are grounded in retrieved document content.
    """

    if not context.strip():
        return "No relevant information found in the document."

    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",   # fast & cost-efficient
        messages=[
            {
                "role": "system",
                "content": "You answer questions strictly using the provided context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300,
        temperature=0.2
    )

    return response.choices[0].message.content.strip()