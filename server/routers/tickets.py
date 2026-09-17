from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from typing import Optional
import io
import pandas as pd
from sqlalchemy import text
from server.db import engine, execute_raw_sql

router = APIRouter(prefix="/api", tags=["Tickets"])

@router.get("/stats")
def get_dashboard_stats():
    """Returns aggregated high-level KPIs and category distributions."""
    df = pd.read_sql("SELECT * FROM tickets", con=engine)
    
    if df.empty:
        return {}
        
    total_tickets = len(df)
    open_tickets = len(df[df["status"].isin(["Open", "Escalated"])])
    resolved_tickets = len(df[df["status"] == "Resolved"])
    critical_tickets = len(df[df["priority"] == "Critical"])
    
    avg_resp_time = round(df["resp_time_hrs"].mean(), 1) if not df["resp_time_hrs"].dropna().empty else 0
    avg_resol_time = round(df[df["status"] == "Resolved"]["resol_time_hrs"].mean(), 1) if not df[df["status"] == "Resolved"]["resol_time_hrs"].dropna().empty else 0
    avg_rating = round(df["cust_rating"].dropna().mean(), 2) if not df["cust_rating"].dropna().empty else 0
    
    category_dist = df["category"].value_counts().to_dict()
    priority_dist = df["priority"].value_counts().to_dict()
    status_dist = df["status"].value_counts().to_dict()
    
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "critical_tickets": critical_tickets,
        "avg_resp_time_hrs": avg_resp_time,
        "avg_resol_time_hrs": avg_resol_time,
        "avg_rating": avg_rating,
        "category_distribution": category_dist,
        "priority_distribution": priority_dist,
        "status_distribution": status_dist
    }

@router.get("/tickets")
def get_tickets(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500)
):
    """Retrieves list of tickets with optional filters."""
    query = "SELECT * FROM tickets WHERE 1=1"
    
    if category:
        query += f" AND category = '{category}'"
    if priority:
        query += f" AND priority = '{priority}'"
    if status:
        query += f" AND status = '{status}'"
    if agent_id:
        query += f" AND agent_id = '{agent_id}'"
        
    query += f" ORDER BY created_at DESC LIMIT {limit};"
    
    rows = execute_raw_sql(query)
    return {"count": len(rows), "tickets": rows}

@router.post("/upload-csv")
async def upload_tickets_csv(file: UploadFile = File(...)):
    """Ingests a custom support tickets CSV file into the database, replacing existing records."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Verify required columns
        required_cols = {"ticket_id", "created_at", "category", "priority", "status"}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise HTTPException(status_code=400, detail=f"CSV missing required columns: {missing}")
            
        # Clean numeric columns
        if 'resol_time_hrs' in df.columns:
            df['resol_time_hrs'] = pd.to_numeric(df['resol_time_hrs'], errors='coerce')
        if 'cust_rating' in df.columns:
            df['cust_rating'] = pd.to_numeric(df['cust_rating'], errors='coerce')
            
        # Clear existing table and insert new CSV rows
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM tickets;"))
            conn.commit()
            
        df.to_sql("tickets", con=engine, if_exists="append", index=False)
        return {
            "success": True,
            "message": f"Successfully uploaded and ingested {len(df)} records into database.",
            "filename": file.filename,
            "total_records": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Upload Ingestion Error: {str(e)}")
