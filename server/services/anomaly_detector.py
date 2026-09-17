import numpy as np
import pandas as pd
from typing import Dict, Any, List
from server.db import engine, execute_raw_sql

def run_anomaly_detection() -> Dict[str, Any]:
    """
    Performs multi-vector anomaly detection on customer support tickets:
    1. Unresolved High/Critical Priority tickets created over 24 hours ago (or high response time).
    2. Statistical Outliers in Resolution Time (using Z-score and IQR).
    3. Underperforming Agents (abnormally low average ratings or high escalation rates).
    4. Unusually high response times across categories.
    """
    df = pd.read_sql("SELECT * FROM tickets", con=engine)
    
    if df.empty:
        return {
            "summary": {"total_anomalies": 0},
            "anomalies": []
        }
        
    anomalies_found = []
    
    # Vector 1: Unresolved High / Critical Tickets > 24 Hours
    unresolved_high = df[
        (df["status"].isin(["Open", "Escalated"])) & 
        (df["priority"].isin(["High", "Critical"])) &
        (df["resp_time_hrs"] > 2.0)  # High initial delay on open critical items
    ]
    
    for _, row in unresolved_high.iterrows():
        anomalies_found.append({
            "id": f"ANO-CRIT-{row['ticket_id']}",
            "ticket_id": row["ticket_id"],
            "type": "Unresolved High-Priority SLA Risk",
            "severity": "CRITICAL" if row["priority"] == "Critical" else "HIGH",
            "category": row["category"],
            "agent_id": row["agent_id"],
            "metric_value": f"Response Time: {row['resp_time_hrs']} hrs",
            "description": f"Ticket {row['ticket_id']} ({row['priority']} priority, {row['category']}) is still '{row['status']}' with a high response delay of {row['resp_time_hrs']} hours.",
            "issue_summary": row["issue_summary"]
        })
        
    # Vector 2: Statistical Resolution Time Outliers (IQR / Z-score)
    resolved_df = df[df["status"] == "Resolved"].copy()
    if not resolved_df.empty:
        resol_times = resolved_df["resol_time_hrs"].dropna()
        q1 = resol_times.quantile(0.25)
        q3 = resol_times.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + (1.5 * iqr)
        
        # Z-score outlier threshold
        mean_resol = resol_times.mean()
        std_resol = resol_times.std()
        
        outliers = resolved_df[resolved_df["resol_time_hrs"] > upper_bound]
        
        for _, row in outliers.iterrows():
            z_score = round((row["resol_time_hrs"] - mean_resol) / (std_resol if std_resol > 0 else 1), 2)
            anomalies_found.append({
                "id": f"ANO-TIME-{row['ticket_id']}",
                "ticket_id": row["ticket_id"],
                "type": "Abnormally Long Resolution Time",
                "severity": "HIGH" if z_score > 3.0 else "MEDIUM",
                "category": row["category"],
                "agent_id": row["agent_id"],
                "metric_value": f"{row['resol_time_hrs']} hrs (Z-score: {z_score})",
                "description": f"Ticket {row['ticket_id']} took {row['resol_time_hrs']} hours to resolve, exceeding the IQR threshold ({round(upper_bound, 1)} hrs) with a Z-score of {z_score}.",
                "issue_summary": row["issue_summary"]
            })
            
    # Vector 3: Agent Performance Anomalies (Low ratings & High Escalations)
    agent_stats = df.groupby("agent_id").agg(
        total_tickets=("ticket_id", "count"),
        avg_rating=("cust_rating", "mean"),
        escalated_count=("status", lambda s: (s == "Escalated").sum())
    ).reset_index()
    
    for _, agent_row in agent_stats.iterrows():
        if pd.notnull(agent_row["avg_rating"]) and agent_row["avg_rating"] < 2.5:
            anomalies_found.append({
                "id": f"ANO-AGENT-{agent_row['agent_id']}",
                "ticket_id": "N/A",
                "type": "Subpar Agent Satisfaction Rating",
                "severity": "HIGH",
                "category": "Agent Performance",
                "agent_id": agent_row["agent_id"],
                "metric_value": f"Avg Rating: {round(agent_row['avg_rating'], 2)} / 5.0",
                "description": f"Agent {agent_row['agent_id']} has an unusually low customer satisfaction rating of {round(agent_row['avg_rating'], 2)} across {agent_row['total_tickets']} tickets.",
                "issue_summary": f"Agent performance audit recommended for {agent_row['agent_id']}."
            })
            
        escalation_rate = (agent_row["escalated_count"] / agent_row["total_tickets"]) * 100
        if escalation_rate > 25.0 and agent_row["total_tickets"] >= 10:
            anomalies_found.append({
                "id": f"ANO-ESC-{agent_row['agent_id']}",
                "ticket_id": "N/A",
                "type": "High Ticket Escalation Rate",
                "severity": "MEDIUM",
                "category": "Operational Bottleneck",
                "agent_id": agent_row["agent_id"],
                "metric_value": f"{round(escalation_rate, 1)}% Escalated",
                "description": f"Agent {agent_row['agent_id']} has an escalation rate of {round(escalation_rate, 1)}% ({agent_row['escalated_count']}/{agent_row['total_tickets']} tickets).",
                "issue_summary": f"High escalation rate pattern detected for {agent_row['agent_id']}."
            })
            
    # Summary stats
    critical_count = sum(1 for a in anomalies_found if a["severity"] == "CRITICAL")
    high_count = sum(1 for a in anomalies_found if a["severity"] == "HIGH")
    medium_count = sum(1 for a in anomalies_found if a["severity"] == "MEDIUM")
    
    return {
        "summary": {
            "total_anomalies": len(anomalies_found),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "overall_health_score": max(0, 100 - (critical_count * 15 + high_count * 5 + medium_count * 2))
        },
        "anomalies": anomalies_found
    }
