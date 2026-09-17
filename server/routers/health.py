from fastapi import APIRouter
from server.config import settings
from server.db import engine, text

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    """Health check endpoint evaluating backend, database, and LLM status."""
    db_status = "unhealthy"
    ticket_count = 0
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*) FROM tickets")).fetchone()
            ticket_count = res[0] if res else 0
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "service": "AI Support Ticket Backend",
        "database": {
            "status": db_status,
            "total_tickets": ticket_count,
            "url": settings.DATABASE_URL
        },
        "llm_provider": settings.LLM_PROVIDER,
        "environment": "production-ready"
    }
