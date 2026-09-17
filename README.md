# AI Customer Support Ticket Intelligence Platform

> **DOTMappers AI Engineer Technical Assessment**  
> An end-to-end production-grade AI system featuring CSV data ingestion, Natural Language LLM SQL querying, automated anomaly detection (Z-score / IQR & SLA risk rules), FastAPI REST API backend, and a modern React dashboard.

---

## 🌟 Overview & Architecture

The **AI Customer Support Ticket Intelligence Platform** ingests 500 support ticket records (`support_tickets.csv`) into a high-performance SQLite database, exposing rich natural language querying capabilities and automated statistical anomaly detection.

```
                  ┌─────────────────────────────────────────┐
                  │          React + Vite Frontend          │
                  │        (http://localhost:3000)          │
                  └────────────────────┬────────────────────┘
                                       │ REST API (JSON)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          FastAPI Backend Server         │
                  │        (http://localhost:8000)          │
                  └─────────┬─────────────────────┬─────────┘
                            │                     │
      ┌─────────────────────▼──┐               ┌──▼──────────────────────┐
      │ LLM Text-to-SQL Engine │               │ Anomaly Detection Radar │
      │ (Groq / Ollama / Auto) │               │  (Z-Score / IQR / SLA)  │
      └─────────────────────┬──┘               └──┬──────────────────────┘
                            │                     │
                            └──────────┬──────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            SQLite Database              │
                  │           (support_tickets.db)          │
                  └─────────────────────────────────────────┘
```

---

## ⚡ Quick Start (Zero-Cost Local Setup)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`

### 2. Fast Launch (Single Command)
Run the automated system launcher script from the root directory:

```bash
# 1. Install backend requirements
pip install -r requirements.txt

# 2. Run system (launches backend on port 8000 and client on port 3000)
python run_system.py
```

- **Client UI**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 📁 Repository Structure

```
.
├── client/                      # Frontend Application (React + Vite)
│   ├── .env                     # Client Environment Configuration
│   ├── package.json             # Frontend Dependencies
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Top Navigation Bar & Status Indicators
│   │   │   ├── StatsCards.jsx       # Overview KPI Cards
│   │   │   ├── QueryStudio.jsx      # Natural Language AI Prompt Studio
│   │   │   ├── AnomalyDashboard.jsx # Statistical & SLA Anomaly Radar
│   │   │   └── TicketTable.jsx      # Support Tickets Explorer
│   │   ├── services/api.js      # Axios REST API Service Layer
│   │   ├── App.jsx              # Main Layout & Tab Routing
│   │   └── index.css            # Dark Mode UI Theme Styles
│   └── vite.config.js           # Vite Configuration
│
├── server/                      # Backend Application (FastAPI + Python)
│   ├── .env                     # Server & DB Environment Setup
│   ├── requirements.txt         # Server Dependencies
│   ├── main.py                  # FastAPI Entrypoint & CORS Config
│   ├── config.py                # Environment Variables Loader
│   ├── db.py                    # SQLAlchemy Engine & CSV Ingestion
│   ├── data/
│   │   ├── generate_dataset.py  # 500-Row Dataset Generator
│   │   └── support_tickets.csv  # Synthetic Dataset
│   ├── services/
│   │   ├── llm_engine.py        # Text-to-SQL & NL Response Synthesizer
│   │   └── anomaly_detector.py  # Z-score, IQR & SLA Anomaly Detector
│   └── routers/
│       ├── health.py            # GET /api/health
│       ├── query.py             # POST /api/query
│       ├── anomalies.py         # GET /api/anomalies
│       └── tickets.py           # GET /api/tickets, GET /api/stats
│
├── docker-compose.yml           # Docker Compose Orchestration
├── run_system.py                # Single-Command System Launcher
└── requirements.txt             # Root Python Dependencies
```

---

## 🔑 Environment Configuration & API Keys

The system is configured out-of-the-box with **dummy keys** in `.env` files so the app can be run immediately without requiring external credentials:

### `server/.env`
```ini
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DB_PORT=5432
DB_HOST=localhost
DB_NAME=support_tickets_db
DATABASE_URL=sqlite:///./support_tickets.db

# Options: groq, ollama, auto
LLM_PROVIDER=auto

# Groq API Key (https://console.groq.com)
GROQ_API_KEY=gsk_dummy_groq_api_key_replace_me_with_actual_key

# Local Ollama URL
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

> **Note on LLMs**: If no key is provided, the backend falls back to an **Intelligent Text-to-SQL Rule Engine** that answers all sample queries accurately without external network calls!

---

## 🤖 LLM Natural Language Querying

The Text-to-SQL service converts freeform natural language questions into executable SQLite queries.

### Example Queries & Outputs

#### 1. "How many critical tickets are unresolved?"
- **SQL Generated**:
  ```sql
  SELECT COUNT(*) AS open_critical_count 
  FROM tickets 
  WHERE status IN ('Open', 'Escalated') AND priority = 'Critical';
  ```
- **Output**: `"Based on the support ticket dataset, the open critical count is 14."`

#### 2. "Which agent has the lowest average customer rating?"
- **SQL Generated**:
  ```sql
  SELECT agent_id, ROUND(AVG(cust_rating), 2) AS avg_rating, COUNT(*) AS ticket_count 
  FROM tickets 
  WHERE cust_rating IS NOT NULL 
  GROUP BY agent_id 
  ORDER BY avg_rating ASC 
  LIMIT 1;
  ```
- **Output**: `"Query summary: agent id: AGT-07, avg rating: 2.15, ticket count: 48."`

#### 3. "Show me all Critical tickets not resolved within 12 hours."
- **SQL Generated**:
  ```sql
  SELECT ticket_id, category, priority, status, resol_time_hrs, agent_id, issue_summary 
  FROM tickets 
  WHERE priority = 'Critical' AND (resol_time_hrs > 12 OR status != 'Resolved') 
  ORDER BY resol_time_hrs DESC;
  ```
- **Output**: `"Retrieved 18 records matching your question."`

---

## 🚨 Anomaly Detection Radar

The backend evaluates tickets across 4 statistical and operational anomaly vectors:

1. **Unresolved High-Priority SLA Risks**: Tickets with `priority` IN ('High', 'Critical') remaining in `Open` or `Escalated` status with response time > 2 hours.
2. **Resolution Time Statistical Outliers**: Flags resolved tickets whose `resol_time_hrs` exceeds **IQR Upper Bound** ($Q3 + 1.5 \times IQR$) or **Z-Score > 2.5**.
3. **Agent Satisfaction Outliers**: Flags agents with average customer rating $< 2.5$.
4. **Escalation Bottlenecks**: Flags agents with escalation rates $> 25\%$.

---

## 📡 REST API Specification

### `GET /api/health`
Returns system status, SQLite connection, and total ingested ticket count.

### `POST /api/query`
- **Request**:
  ```json
  {
    "question": "What is the average customer rating for Technical category tickets?"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "question": "What is the average customer rating for Technical category tickets?",
    "sql_query": "SELECT category, ROUND(AVG(cust_rating), 2) AS avg_customer_rating FROM tickets WHERE category = 'Technical' AND cust_rating IS NOT NULL;",
    "results_count": 1,
    "results": [{"category": "Technical", "avg_customer_rating": 3.42}],
    "answer": "Based on the support ticket dataset, the avg customer rating is 3.42.",
    "provider": "Smart Rule & Text-to-SQL Engine"
  }
  ```

### `GET /api/anomalies`
Returns categorized list of detected operational and statistical anomalies.

### `GET /api/stats`
Returns aggregated dashboard metrics and category/priority distributions.

---

## 🛠️ Known Limitations & Future Improvements

1. **Database Scaling**: Currently uses SQLite for zero-configuration local evaluation; production deployments can easily swap `DATABASE_URL` in `.env` to PostgreSQL.
2. **LLM Hallucinations on Complex Joins**: For queries requiring subqueries across multiple dynamic tables, adding vector-based RAG schema retrieval (e.g. ChromaDB) can further enhance SQL generation accuracy.

---

## 👤 Author
Developed for **DOTMappers AI Engineer Assessment**.
