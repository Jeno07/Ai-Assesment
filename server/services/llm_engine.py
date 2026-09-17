import re
import httpx
from typing import Dict, Any, List
from server.config import settings
from server.db import execute_raw_sql

SYSTEM_PROMPT = """You are an expert SQL Data Analyst for a Customer Support Ticket database.
Given a natural language user question, generate a clean, accurate MySQL / SQL SELECT query to answer it.

Table Schema:
Table Name: tickets
Columns:
- ticket_id: String (e.g. 'TKT-001')
- created_at: Datetime string ('YYYY-MM-DD HH:MM')
- category: String ('Billing', 'Technical', 'General')
- priority: String ('Low', 'Medium', 'High', 'Critical')
- status: String ('Open', 'Resolved', 'Escalated')
- resp_time_hrs: Float (Response time in hours)
- resol_time_hrs: Float (Resolution time in hours, NULL if unresolved)
- agent_id: String (e.g. 'AGT-01')
- cust_rating: Integer 1-5 (NULL if unresolved)
- issue_summary: String (Text description)
- remarks: String (Resolution notes or remarks)

Instructions:
1. Return ONLY valid SELECT queries inside a ```sql ... ``` block or plain text.
2. Do not use UPDATE, DELETE, DROP, or INSERT statement.
3. For open/unresolved tickets, use status IN ('Open', 'Escalated') or status != 'Resolved'.
4. Format column names cleanly.
"""

def generate_heuristic_sql(question: str) -> str:
    """Intelligent rule-based SQL generator that dynamically parses user keywords."""
    q = question.lower().strip()
    
    where_conditions = []
    
    # Category detection
    if "billing" in q:
        where_conditions.append("category = 'Billing'")
    elif "technical" in q or "tech" in q:
        where_conditions.append("category = 'Technical'")
    elif "general" in q:
        where_conditions.append("category = 'General'")
        
    # Priority detection
    if "critical" in q:
        where_conditions.append("priority = 'Critical'")
    elif "high" in q:
        where_conditions.append("priority = 'High'")
    elif "medium" in q:
        where_conditions.append("priority = 'Medium'")
    elif "low" in q:
        where_conditions.append("priority = 'Low'")

    # Status detection
    if "open" in q or "unresolved" in q:
        where_conditions.append("status IN ('Open', 'Escalated')")
    elif "resolved" in q:
        where_conditions.append("status = 'Resolved'")
    elif "escalated" in q:
        where_conditions.append("status = 'Escalated'")
        
    # Agent detection (e.g. AGT-01, AGT-05, agent 3)
    agent_match = re.search(r"agt-\d{2}", q)
    if agent_match:
        where_conditions.append(f"agent_id = '{agent_match.group().upper()}'")

    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""

    # Aggregations vs counts vs listings
    if "how many" in q or "count" in q or "total number" in q:
        return f"SELECT COUNT(*) AS total_count FROM tickets{where_clause};"
        
    if "average rating" in q or "avg rating" in q or "rating" in q:
        if "lowest" in q or "worst" in q:
            return f"SELECT agent_id, ROUND(AVG(cust_rating), 2) AS avg_rating, COUNT(*) AS ticket_count FROM tickets WHERE cust_rating IS NOT NULL GROUP BY agent_id ORDER BY avg_rating ASC LIMIT 5;"
        elif "highest" in q or "best" in q or "top" in q:
            return f"SELECT agent_id, ROUND(AVG(cust_rating), 2) AS avg_rating, COUNT(*) AS ticket_count FROM tickets WHERE cust_rating IS NOT NULL GROUP BY agent_id ORDER BY avg_rating DESC LIMIT 5;"
        else:
            return f"SELECT category, ROUND(AVG(cust_rating), 2) AS avg_rating FROM tickets WHERE cust_rating IS NOT NULL GROUP BY category ORDER BY avg_rating DESC;"

    if "response time" in q or "resp_time" in q:
        return f"SELECT ticket_id, category, priority, status, resp_time_hrs, agent_id, remarks FROM tickets{where_clause} ORDER BY resp_time_hrs DESC LIMIT 10;"

    if "resolution time" in q or "resol_time" in q:
        return f"SELECT ticket_id, category, priority, status, resol_time_hrs, agent_id, remarks FROM tickets{where_clause} ORDER BY resol_time_hrs DESC LIMIT 10;"

    # Default listing with filters applied
    return f"SELECT ticket_id, created_at, category, priority, status, resp_time_hrs, resol_time_hrs, agent_id, cust_rating, issue_summary, remarks FROM tickets{where_clause} ORDER BY created_at DESC LIMIT 20;"

def extract_sql_from_text(text: str) -> str:
    """Extracts SQL query from markdown block or text."""
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match_code = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match_code:
        return match_code.group(1).strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sql_lines = [l for l in lines if l.upper().startswith("SELECT") or l.upper().startswith("WITH")]
    if sql_lines:
        return " ".join(lines)
    return text.strip()

async def call_groq_api(question: str) -> str:
    """Calls Groq API using active models to generate SQL query."""
    if not settings.GROQ_API_KEY or "dummy" in settings.GROQ_API_KEY.lower():
        raise ValueError("Groq API key is empty or dummy.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    models = ["groq/compound-mini", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    last_error = None
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for model in models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Generate a MySQL SELECT query for: {question}"}
                ],
                "temperature": 0.1
            }
            try:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    last_error = f"Groq API ({model}) Error {resp.status_code}: {resp.text}"
            except Exception as e:
                last_error = str(e)
                
    raise RuntimeError(last_error or "Groq API model failed")

async def call_groq_synthesize(question: str, sql: str, results: List[Dict[str, Any]]) -> str:
    """Synthesizes human conversational answer using Groq LLM based on question and query results."""
    if not settings.GROQ_API_KEY or "dummy" in settings.GROQ_API_KEY.lower():
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    sample_data = str(results[:10]) if len(results) > 10 else str(results)
    prompt = f"""You are a helpful customer support data analyst.
User asked: "{question}"
SQL executed: `{sql}`
Total records returned: {len(results)}
Data results (sample): {sample_data}

Provide a direct, helpful, natural language summary answering the user's question accurately based on the data. Do NOT use static templates or mention code internal variable names. Keep it conversational, clear, and informative."""

    payload = {
        "model": "groq/compound-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Strip reasoning block if model returns reasoning tags
            content = re.sub(r"<reasoning>.*?</reasoning>", "", content, flags=re.DOTALL).strip()
            # Normalize unicode quotes, spaces, and hyphens
            import unicodedata
            content = unicodedata.normalize("NFKD", content)
            content = content.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
            return content
    return None

async def synthesize_natural_answer(question: str, sql: str, results: List[Dict[str, Any]]) -> str:
    """Synthesizes human-readable natural language answer dynamically."""
    if not results:
        return f"No matching tickets found for your query: '{question}'."

    # Try LLM synthesis first if Groq API key is available
    if settings.GROQ_API_KEY and "dummy" not in settings.GROQ_API_KEY.lower():
        try:
            llm_summary = await call_groq_synthesize(question, sql, results)
            if llm_summary:
                return llm_summary
        except Exception as e:
            print(f"[LLM Engine] Synthesis LLM call skipped/failed: {e}")

    # Dynamic Rule-Based Synthesis
    if len(results) == 1 and len(results[0]) == 1:
        key, val = list(results[0].items())[0]
        readable_key = key.replace('_', ' ').title()
        return f"Based on the database, the **{readable_key}** is **{val}**."

    if len(results) == 1:
        details = ", ".join([f"**{k.replace('_', ' ').title()}**: {v}" for k, v in results[0].items() if v is not None])
        return f"QueryResult: {details}"

    # Dynamic multi-row summary
    count = len(results)
    categories, priorities, statuses = {}, {}, {}
    
    for row in results:
        if "category" in row and row["category"]:
            categories[row["category"]] = categories.get(row["category"], 0) + 1
        if "priority" in row and row["priority"]:
            priorities[row["priority"]] = priorities.get(row["priority"], 0) + 1
        if "status" in row and row["status"]:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1

    summary_parts = [f"Found **{count}** tickets matching your query."]
    if categories:
        summary_parts.append("**Categories**: " + ", ".join([f"{k} ({v})" for k, v in categories.items()]))
    if priorities:
        summary_parts.append("**Priorities**: " + ", ".join([f"{k} ({v})" for k, v in priorities.items()]))
    if statuses:
        summary_parts.append("**Statuses**: " + ", ".join([f"{k} ({v})" for k, v in statuses.items()]))

    return " | ".join(summary_parts)

async def process_natural_language_query(question: str) -> Dict[str, Any]:
    """Processes natural language query using available LLM or dynamic rule engine."""
    provider_used = "Smart Rule Engine"
    raw_sql = ""
    
    # Groq Provider
    if settings.LLM_PROVIDER in ["groq", "auto"] and settings.GROQ_API_KEY and "dummy" not in settings.GROQ_API_KEY.lower():
        try:
            raw_sql = await call_groq_api(question)
            provider_used = "Groq AI (groq/compound-mini)"
        except Exception as e:
            print(f"[LLM Engine] Groq API call skipped/failed: {e}")

    # Fallback to dynamic heuristic query generator
    if not raw_sql:
        raw_sql = generate_heuristic_sql(question)
        provider_used = "Dynamic Rule & Text-to-SQL Engine"

    clean_sql = extract_sql_from_text(raw_sql)
    
    # Execute SQL
    try:
        results = execute_raw_sql(clean_sql)
        nl_answer = await synthesize_natural_answer(question, clean_sql, results)
        
        return {
            "success": True,
            "question": question,
            "sql_query": clean_sql,
            "results_count": len(results),
            "results": results[:50],
            "answer": nl_answer,
            "provider": provider_used
        }
    except Exception as err:
        fallback_sql = "SELECT ticket_id, created_at, category, priority, status, agent_id, cust_rating, issue_summary FROM tickets ORDER BY created_at DESC LIMIT 10;"
        results = execute_raw_sql(fallback_sql)
        return {
            "success": False,
            "question": question,
            "sql_query": clean_sql,
            "error": str(err),
            "fallback_sql": fallback_sql,
            "results": results,
            "answer": f"Executed fallback query due to SQL execution notice: {str(err)}.",
            "provider": provider_used
        }
