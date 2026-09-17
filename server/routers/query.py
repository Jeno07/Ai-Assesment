from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from server.services.llm_engine import process_natural_language_query

router = APIRouter(prefix="/api", tags=["Natural Language Query"])

class QueryRequest(BaseModel):
    question: str = Field(..., example="How many critical tickets are unresolved?")

@router.post("/query")
async def run_query(request: QueryRequest):
    """Processes natural language questions about customer support tickets using LLM Text-to-SQL engine."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        response = await process_natural_language_query(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")
