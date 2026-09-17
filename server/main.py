import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.config import settings
from server.db import init_db
from server.routers import health, query, anomalies, tickets

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("[Server Startup] Initializing SQLite database and dataset ingestion...")
    init_db()
    print("[Server Startup] Database ready.")
    yield
    # Shutdown actions
    print("[Server Shutdown] Cleaning up resources...")

app = FastAPI(
    title="AI Customer Support Ticket System API",
    description="Backend service providing LLM Natural Language Querying, Anomaly Detection, and Analytics for Customer Support Tickets.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(anomalies.router)
app.include_router(tickets.router)

@app.get("/")
def root():
    return {
        "message": "AI Customer Support Ticket Backend API is running.",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
