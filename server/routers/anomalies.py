from fastapi import APIRouter, HTTPException
from server.services.anomaly_detector import run_anomaly_detection

router = APIRouter(prefix="/api", tags=["Anomaly Detection"])

@router.get("/anomalies")
def get_anomalies():
    """Detects and flags anomalies in resolution times, unresolved SLA risks, agent ratings, and escalation rates."""
    try:
        report = run_anomaly_detection()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")
