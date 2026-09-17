import csv
import random
from datetime import datetime, timedelta

def generate_support_tickets(num_rows=500, output_path="support_tickets.csv"):
    categories = ["Billing", "Technical", "General"]
    priorities = ["Low", "Medium", "High", "Critical"]
    statuses = ["Open", "Resolved", "Escalated"]
    
    agent_ids = [f"AGT-{i:02d}" for i in range(1, 11)]
    
    issue_summaries = {
        "Billing": [
            "Incorrect charge on invoice",
            "Refund not processed",
            "Double billing on subscription",
            "Payment gateway transaction failed",
            "Update billing credit card info",
            "Invoice receipt missing for tax filing",
            "Subscription tier downgrade requested",
            "Promo code not applied at checkout",
            "Unrecognized charge on bank statement",
            "Auto-renewal cancellation request"
        ],
        "Technical": [
            "Login failure after update",
            "API timeout in production",
            "Database connection pool exhausted",
            "SSO authentication error 500",
            "Dashboard widget loading state frozen",
            "Export to CSV throwing 502 Bad Gateway",
            "Webhook notifications delayed",
            "Mobile app crash on iOS 17 startup",
            "SSL certificate expiry warning",
            "High CPU usage on background worker"
        ],
        "General": [
            "Request for product docs",
            "Feature request: Dark mode support",
            "Account deletion and GDPR data wipe",
            "Inquiry regarding API rate limits",
            "User permissions setup assistance",
            "Onboarding guidance for new team members",
            "Feedback on recent UI update",
            "Inquiry about SLA guarantees",
            "Language translation support request",
            "Custom domain configuration inquiry"
        ]
    }
    
    start_date = datetime(2024, 1, 1, 8, 0)
    tickets = []
    
    for i in range(1, num_rows + 1):
        ticket_id = f"TKT-{i:03d}"
        
        # Random creation date within last 60 days
        minutes_offset = random.randint(0, 60 * 24 * 60)
        created_dt = start_date + timedelta(minutes=minutes_offset)
        created_at = created_dt.strftime("%Y-%m-%d %H:%M")
        
        category = random.choices(categories, weights=[0.35, 0.45, 0.20])[0]
        priority = random.choices(priorities, weights=[0.30, 0.40, 0.20, 0.10])[0]
        
        # Determine status with logical weighting
        if priority == "Critical" and random.random() < 0.25:
            status = random.choice(["Open", "Escalated"])
        else:
            status = random.choices(statuses, weights=[0.20, 0.70, 0.10])[0]
            
        agent_id = random.choice(agent_ids)
        issue_summary = random.choice(issue_summaries[category])
        
        # Response time (0.1 to 12.0 hours)
        resp_time_hrs = round(random.expovariate(1.0 / 1.5) + 0.1, 1)
        if resp_time_hrs > 24.0:
            resp_time_hrs = 23.5
            
        # Resolution time & rating dependent on status
        if status == "Resolved":
            # Normal resolution time 0.5 to 15 hours, with occasional synthetic outliers (> 30 hours)
            if random.random() < 0.05:  # 5% anomalies in resolution time
                resol_time_hrs = round(random.uniform(32.0, 72.0), 1)
            else:
                resol_time_hrs = round(resp_time_hrs + random.expovariate(1.0 / 4.0) + 0.5, 1)
                
            # Customer rating (1 to 5) - AGT-07 slightly lower to create realistic pattern query scenario
            if agent_id == "AGT-07":
                cust_rating = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.30, 0.20, 0.10, 0.05])[0]
            else:
                cust_rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.15, 0.35, 0.35])[0]
        # Remarks generation
        if status == "Resolved":
            remarks_list = [
                "Issue verified fixed and customer confirmed resolution.",
                "Sent direct link to documentation and user guide.",
                "Refund processed and credit memo issued.",
                "Database connection pool expanded and performance restored.",
                "SSO certificate renewed and tested in production.",
                "Patch deployed to production successfully.",
                "Invoice corrected and sent to customer email.",
                "User guided through password reset and login restored."
            ]
            remarks = random.choice(remarks_list)
        elif status == "Escalated":
            remarks_list = [
                "Escalated to senior engineering team due to complexity.",
                "Escalated to DevOps for infrastructure investigation.",
                "Priority escalation triggered by SLA breach threshold.",
                "Customer requested manager escalation."
            ]
            remarks = random.choice(remarks_list)
        else:
            remarks_list = [
                "Under active investigation by support staff.",
                "Awaiting customer response to troubleshooting steps.",
                "Assigned to L2 technical support queue.",
                "Logs collected and queued for review."
            ]
            remarks = random.choice(remarks_list)

        tickets.append({
            "ticket_id": ticket_id,
            "created_at": created_at,
            "category": category,
            "priority": priority,
            "status": status,
            "resp_time_hrs": resp_time_hrs,
            "resol_time_hrs": resol_time_hrs,
            "agent_id": agent_id,
            "cust_rating": cust_rating,
            "issue_summary": issue_summary,
            "remarks": remarks
        })
        
    fieldnames = [
        "ticket_id", "created_at", "category", "priority", "status",
        "resp_time_hrs", "resol_time_hrs", "agent_id", "cust_rating", "issue_summary", "remarks"
    ]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tickets)
        
    print(f"Successfully generated {num_rows} tickets in '{output_path}'.")

if __name__ == "__main__":
    generate_support_tickets()
