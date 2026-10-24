import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.rag_engine import ingest_pdf, answer_question, FAISS_PATH, GRAPH_PATH

app = FastAPI(
    title="Hybrid Graph-RAG API",
    description="FastAPI Backend combining FAISS Vector DB and NetworkX Knowledge Graph"
)

class QueryRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    """Checks if the FastAPI server and databases are ready."""
    db_ready = os.path.exists(FAISS_PATH) and os.path.exists(GRAPH_PATH)
    return {
        "status": "running",
        "databases_initialized": db_ready
    }

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Uploads a PDF and builds both the Vector DB and Knowledge Graph."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = os.path.join("./storage", file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        stats = ingest_pdf(temp_path)
        return {
            "message": f"Successfully ingested '{file.filename}' into Vector DB and Knowledge Graph!",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_customer_question(request: QueryRequest):
    """Queries both Vector DB and Knowledge Graph to answer a customer's question."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = answer_question(request.question)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result