# Parallax — Claude Code Guide

Multi-Agent Research Network. 7 AI agents run in parallel to deliver cross-validated,
confidence-scored research reports in minutes.

**GitHub:** https://github.com/VenkataAnilKumar/ParallaxAI
**Owner:** Venkata (VenkataAnilKumar)

---

## Project Structure

```
parallax/
├── backend/          # FastAPI + Celery (Python 3.12, uv)
│   └── app/
│       ├── agents/   # All research agents
│       ├── api/      # REST routes + WebSocket
│       ├── models/   # SQLAlchemy ORM
│       ├── schemas/  # Pydantic schemas
│       ├── services/ # search.py, billing.py, usage.py
│       ├── tasks/    # Celery task (parallel agent execution)
│       └── core/     # auth.py, exceptions.py
├── frontend/         # Next.js 15 App Router (TypeScript)
│   └── src/
│       ├── app/      # Pages (landing, login, /app/*)
│       ├── components/research/  # ResearchInput, AgentProgress, ReportViewer
│       ├── lib/      # api.ts, websocket.ts, supabase.ts
│       └── stores/   # Zustand research store
├── docs/             # 13 product + technical documents
└── docker-compose.yml
```

---

## Running Locally

```bash
# Start infrastructure
docker compose up db redis -d

# Backend (from /backend)
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Celery worker (new terminal)
cd backend && uv run celery -A app.celery_app worker --loglevel=info

# Frontend (from /frontend)
npm install && npm run dev
```

---

## Key Architecture Decisions

| Decision | What | Why |
|---|---|---|
| **Parallel execution** | `ThreadPoolExecutor` in Celery task | All 7 agents run concurrently — total time = slowest agent |
| **Search-first agents** | Tavily → Exa fallback → Claude | Agents ground findings in live web data, not just training |
| **Structured JSON output** | Every agent returns typed JSON | `parse_response()` with fallback prevents silent failures |
| **Redis pub/sub** | Agent events → WebSocket | Celery workers publish, FastAPI streams to frontend in real-time |
| **Supabase JWT** | Auto-provisioning on first login | No separate registration flow; backend creates User from claims |
| **pgvector** | Findings stored as 1536-dim embeddings | Semantic dedup + future similarity search across history |
| **Opus for planning** | Orchestrator, Validator, Synthesizer use claude-opus-4-6 | Complex reasoning tasks; Sonnet for the 7 research agents |

---

## Agent Pipeline

```
OrchestratorAgent (claude-opus-4-6)
    └── Decomposes query, decides which agents to run

    Parallel via ThreadPoolExecutor:
    ├── MarketAgent        → Tavily: "market size TAM growth rate 2025"
    ├── CompetitorAgent    → Tavily: "competitors key players alternatives"
    ├── RegulatoryAgent    → Tavily: "regulation compliance law risk"
    ├── NewsAgent          → Tavily: "news announcement funding launch"
    ├── FinancialAgent     → Tavily: "funding valuation revenue VC"
    ├── SentimentAgent     → Tavily: "reviews opinions Reddit Twitter"
    └── AcademicAgent      → Exa:    semantic paper search (use_exa_search=True)

CrossValidatorAgent (claude-opus-4-6)
    └── Finds contradictions, assigns confidence scores

SynthesisAgent (claude-opus-4-6, max_tokens=8192)
    └── Writes executive report, key findings, strategic implications
```

---

## Adding a New Agent

1. Create `backend/app/agents/research/myagent.py`:

```python
from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent

class MyAgent(BaseResearchAgent):
    agent_type = "myagent"
    model = "claude-sonnet-4-6"

    def build_search_query(self, inp: AgentInput) -> str:
        return f"{inp.query} <domain-specific keywords>"

    @property
    def system_prompt(self) -> str:
        return """You are the X Agent for Parallax...
        Respond with JSON: { "summary": ..., "findings": [...], "sources": [...], "confidence_score": ... }"""

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        # parse JSON, return AgentOutput
        ...
```

2. Register in `backend/app/agents/research/__init__.py`:
```python
from app.agents.research.myagent import MyAgent
ALL_AGENTS = { ..., "myagent": MyAgent }
```

---

## Environment Variables

All defined in `backend/app/config.py`. Copy `.env.example` → `.env`.

| Variable | Required | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | All agents use Claude |
| `DATABASE_URL` | ✅ | PostgreSQL (pgvector extension required) |
| `REDIS_URL` | ✅ | Celery broker + WebSocket pub/sub |
| `SUPABASE_URL` | ✅ | Auth |
| `SUPABASE_ANON_KEY` | ✅ | Frontend client |
| `SUPABASE_SERVICE_KEY` | ✅ | Backend admin operations |
| `SUPABASE_JWT_SECRET` | ✅ | JWT verification (Project Settings → API) |
| `TAVILY_API_KEY` | ⚡ | Live web search (agents degrade gracefully without it) |
| `EXA_API_KEY` | ⚡ | Academic/semantic search for AcademicAgent |
| `STRIPE_SECRET_KEY` | 💳 | Billing (optional for dev) |
| `SECRET_KEY` | ✅ | Min 64 chars |

---

## Database

- **ORM:** SQLAlchemy 2.0 async, models in `app/models/`
- **Migrations:** Alembic — `uv run alembic upgrade head`
- **New migration:** `uv run alembic revision --autogenerate -m "description"`
- **pgvector:** ResearchFinding.embedding is Vector(1536) — requires `CREATE EXTENSION vector`

---

## Testing

```bash
cd backend
uv run pytest                          # all tests
uv run pytest tests/test_search.py    # search service tests
uv run pytest --cov=app               # with coverage
```

Tests use a real PostgreSQL database (`parallax_test`). No mocking of DB.

---

## CI/CD

- **PR checks:** `.github/workflows/pr.yml` — ruff, mypy, pytest, tsc, eslint
- **Deploy:** `.github/workflows/deploy.yml` — Railway (API + worker) + Vercel (frontend)
- **Required secrets:** `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`

---

## Deployment

| Service | Platform | Notes |
|---|---|---|
| API | Railway | Service: `parallax-api` |
| Worker | Railway | Service: `parallax-worker`, command: `uv run celery -A app.celery_app worker` |
| PostgreSQL | Railway plugin | Needs pgvector extension enabled |
| Redis | Railway plugin | |
| Frontend | Vercel | Root dir: `frontend` |

---

## Cost Model

- `claude-opus-4-6`: $0.000015/input token, $0.000075/output token
- `claude-sonnet-4-6`: $0.000003/input token, $0.000015/output token
- Blended estimate: ~$0.000012/token (defined in `tasks/research.py`)
- Standard research task: ~$0.82 total API cost
- Defined in `COST_PER_TOKEN` dict in `backend/app/tasks/research.py`

---

## Known Remaining TODOs

- [ ] Stripe billing webhook handlers are stubs — implement subscription lifecycle
- [ ] API rate limiting — add `slowapi` or Railway-level throttling
- [ ] Workspace_id not set on ResearchTask — needed for team billing
- [ ] PDF export — integrate `reportlab` or headless browser
- [ ] Langfuse tracing — wire `LANGFUSE_PUBLIC_KEY` for LLM observability
