import os
import pandas as pd
from sqlalchemy import create_engine, text, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from server.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(String(50), primary_key=True, index=True)
    created_at = Column(String(50), index=True)
    category = Column(String(50), index=True)
    priority = Column(String(50), index=True)
    status = Column(String(50), index=True)
    resp_time_hrs = Column(Float)
    resol_time_hrs = Column(Float, nullable=True)
    agent_id = Column(String(50), index=True)
    cust_rating = Column(Integer, nullable=True)
    issue_summary = Column(String(500))
    remarks = Column(String(500), nullable=True)

def init_db(csv_path: str = None):
    """Initializes the database schema and ingests CSV data if table is empty."""
    if "mysql" in settings.DATABASE_URL:
        try:
            import pymysql
            conn = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}`;")
            conn.close()
        except Exception as e:
            print(f"[DB Warning] MySQL database check: {e}")

    Base.metadata.create_all(bind=engine)
    
    # Ensure remarks column exists on existing tables
    try:
        with engine.connect() as conn:
            if "mysql" in settings.DATABASE_URL:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS remarks VARCHAR(500);"))
            else:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN remarks VARCHAR(500);"))
            conn.commit()
    except Exception:
        pass
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM tickets")).fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            if not csv_path or not os.path.exists(csv_path):
                # Search default paths
                possible_paths = [
                    os.path.join(os.path.dirname(__file__), "data", "support_tickets.csv"),
                    os.path.join(os.path.dirname(__file__), "data", "support_tickets.csv.csv"),
                    os.path.join(os.path.dirname(__file__), "..", "support_tickets.csv"),
                    "support_tickets.csv"
                ]
                for p in possible_paths:
                    if os.path.exists(p):
                        csv_path = p
                        break

            if csv_path and os.path.exists(csv_path):
                print(f"[DB] Ingesting CSV dataset from {csv_path}...")
                df = pd.read_csv(csv_path)
                
                # Standardize column types and names
                if 'Remarks' in df.columns:
                    df.rename(columns={'Remarks': 'remarks'}, inplace=True)
                if 'response_time_hrs' in df.columns:
                    df.rename(columns={'response_time_hrs': 'resp_time_hrs'}, inplace=True)
                if 'resolution_time_hrs' in df.columns:
                    df.rename(columns={'resolution_time_hrs': 'resol_time_hrs'}, inplace=True)
                if 'customer_rating' in df.columns:
                    df.rename(columns={'customer_rating': 'cust_rating'}, inplace=True)

                df['resol_time_hrs'] = pd.to_numeric(df['resol_time_hrs'], errors='coerce')
                df['cust_rating'] = pd.to_numeric(df['cust_rating'], errors='coerce')
                
                df.to_sql("tickets", con=engine, if_exists="append", index=False)
                print(f"[DB] Successfully ingested {len(df)} records into MySQL database.")
            else:
                print("[DB Warning] support_tickets.csv not found for initial ingestion.")

def execute_raw_sql(sql_query: str):
    """Executes a SQL query safely and returns results as a list of dicts."""
    # Simple SQL injection prevention / read-only guard
    query_upper = sql_query.strip().upper()
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        raise ValueError("Only SELECT and read-only queries are permitted.")
        
    for forbidden in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]:
        if f" {forbidden} " in f" {query_upper} ":
            raise ValueError(f"Write operation '{forbidden}' is forbidden.")
            
    with engine.connect() as conn:
        res = conn.execute(text(sql_query))
        keys = res.keys()
        rows = [dict(zip(keys, row)) for row in res.fetchall()]
        return rows
