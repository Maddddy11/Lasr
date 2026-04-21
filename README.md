# AI Access Gateway

AI Access Gateway routes prompts to the best AI provider using deterministic policy controls for role-based access, complexity, PII risk, and fallback safety.

## Features

- FastAPI backend with:
  - `POST /v1/route`
  - `GET /v1/policies`
  - `GET /v1/events`
  - `GET /healthz`
- Deterministic routing using role tiers (Intern, Employee, Executive, Admin), complexity heuristics, and cloud/local fallback.
- PII redaction for emails, phones, SSNs, credit cards, API keys/tokens.
- Policy enforcement: if PII is detected and role is not Admin, request is forced to local LM Studio.
- Provider adapters for LM Studio (OpenAI-compatible), Google Gemini, and Groq.
- SQLite event logging with cost/carbon estimates.
- React + Vite + TypeScript dashboard for events, policies, and summaries.
- Pytest unit coverage for redaction and routing policy decisions.

## Repository Structure

- `/backend` — FastAPI app and routing engine
- `/frontend` — React (Vite + TS) dashboard
- `/tests` — pytest tests

## Setup

1. Copy environment template:

```bash
cp /home/runner/work/Lasr/Lasr/.env.example /home/runner/work/Lasr/Lasr/.env
```

2. Backend install:

```bash
cd /home/runner/work/Lasr/Lasr/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run backend:

```bash
cd /home/runner/work/Lasr/Lasr
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Frontend install + run:

```bash
cd /home/runner/work/Lasr/Lasr/frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

## API Example

```bash
curl -X POST http://localhost:8000/v1/route \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u-123",
    "role": "Employee",
    "prompt": "Email me at user@example.com and help me summarize this report"
  }'
```

## Notes

- If `GEMINI_API_KEY` and `GROQ_API_KEY` are missing, routing falls back to LM Studio.
- Event logs are stored in SQLite at `backend/data/events.db` by default.
