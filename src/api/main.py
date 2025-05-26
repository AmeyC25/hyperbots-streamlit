from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from pathlib import Path
from typing import Dict, Any
import logging

from src.chatbot import chatbot
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document QA Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    metadata: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup."""
    try:
        chatbot.initialize()
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")

@app.get("/")
async def root():
    return {"message": "Document QA Chatbot API", "status": "running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the knowledge base."""
    try:
        # Check file type
        allowed_types = {'.pdf', '.docx', '.txt'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {allowed_types}"
            )
        
        # Save uploaded file
        file_path = Path(settings.upload_dir) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to knowledge base
        result = chatbot.add_document(str(file_path))
        
        if result["success"]:
            return {
                "message": result["message"],
                "filename": file.filename,
                "chunks_added": result["chunk_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the document knowledge base."""
    try:
        result = chatbot.query(request.question)
        
        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get chatbot statistics."""
    try:
        return chatbot.get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset")
async def reset_knowledge_base():
    """Reset the knowledge base (clear all documents)."""
    try:
        # This would require implementing a reset method in the chatbot
        return {"message": "Knowledge base reset functionality not implemented"}
    except Exception as e:
        logger.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)