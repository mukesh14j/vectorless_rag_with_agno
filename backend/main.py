import os
import uuid

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

from agno.agent import Agent
from agno.models.ollama import Ollama

from rag_engine import VectorlessRAG

app = FastAPI()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

rag = VectorlessRAG()

agent = Agent(
    model=Ollama(
        id="qwen3:8b"
    ),
    markdown=True
)


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not (
        file.filename.endswith(".pdf")
        or file.filename.endswith(".docx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF/DOCX supported"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as f:
        f.write(await file.read())

    document_id = rag.ingest(file_path)

    return {
        "document_id": document_id,
        "message": "Indexed successfully"
    }


@app.post("/ask")
async def ask_question(data: dict):

    document_id = data.get("document_id")
    question = data.get("question")

    try:

        results = rag.retrieve(
            document_id=document_id,
            query=question,
            top_k=5
        )

        print("\n========== RETRIEVED ==========")

        for chunk, score in results:
            print(f"\nSCORE: {score}\n")
            print(chunk[:1000])

        print("\n===============================\n")

        context = "\n\n".join([
            chunk
            for chunk, score in results
        ])

        prompt = f"""
You are a helpful document assistant.

Use the context to answer.

CONTEXT:
{context}

QUESTION:
{question}

Provide concise answer.
"""

        response = agent.run(prompt)

        return {
            "answer": response.content,
            "chunks": [
                {
                    "score": float(score),
                    "chunk": chunk[:500]
                }
                for chunk, score in results
            ]
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "answer": f"Error: {str(e)}",
            "chunks": []
        }