<div align="center">

<br />

<img src="https://img.shields.io/badge/status-building-6366f1?style=for-the-badge&labelColor=0f0f0f" />
&nbsp;
<img src="https://img.shields.io/badge/Claude%20API-claude--opus--4--6-d97706?style=for-the-badge&logo=anthropic&logoColor=white&labelColor=0f0f0f" />
&nbsp;
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0f0f0f" />
&nbsp;
<img src="https://img.shields.io/badge/Next.js%2015-black?style=for-the-badge&logo=next.js&logoColor=white&labelColor=0f0f0f" />

<br /><br />

```
◎  P A R A L L A X
```

### Multi-Agent Research Network

**One question. Seven specialist AI agents. One complete picture.**

Research that used to take 3 days — delivered in 6 minutes.
Cross-validated. Confidence-scored. Source-cited.

<br />

[**Getting Started**](#getting-started) · [**Architecture**](#system-architecture) · [**API**](#api-overview) · [**Tech Stack**](#tech-stack) · [**Docs**](#documentation)

<br />

</div>

---

## The Problem

Every analyst, VC, consultant, and founder runs into the same wall:

- **Research is slow** — hours of manual searching, reading, and synthesizing
- **Research is shallow** — one perspective, one angle, critical gaps missed
- **Research is unverified** — contradictory sources with no way to resolve them

Existing tools (Perplexity, ChatGPT, Claude) give you *one AI seeing one angle*. That's still just one perspective.

**Parallax deploys a coordinated team.**

---

## How It Works

```
You ask: "Should I build a B2B payments product in Southeast Asia?"
                              │
                    ┌─────────▼─────────┐
                    │   ORCHESTRATOR    │  ← Decomposes query, assigns agents
                    │  claude-opus-4-6  │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │           Parallel Execution           │
          │                                        │
    ┌─────▼─────┐  ┌──────────▼──────┐  ┌────────▼───────┐
    │  Market   │  │   Competitor    │  │  Regulatory    │
    │  Agent    │  │    Agent        │  │    Agent       │
    └─────┬─────┘  └──────────┬──────┘  └────────┬───────┘
          │                   │                   │
    ┌─────▼─────┐  ┌──────────▼──────┐  ┌────────▼───────┐
    │   News    │  │   Financial     │  │   Sentiment    │
    │  Agent    │  │    Agent        │  │    Agent       │
    └─────┬─────┘  └──────────┬──────┘  └────────┬───────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  CROSS-VALIDATOR  │  ← Finds contradictions, scores confidence
                    │  claude-opus-4-6  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │    SYNTHESIZER    │  ← Writes the final report
                    │  claude-opus-4-6  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  RESEARCH REPORT  │
                    │  ✓ Cross-validated│
                    │  ✓ Confidence %   │
                    │  ✓ Source-cited   │
                    └───────────────────┘
```

**Result:** A structured, executive-quality research report — in 6 minutes.

---

## The Agents

| Agent | Role | Model |
|---|---|---|
| 🧭 **Orchestrator** | Decomposes query, assigns agents, defines research plan | claude-opus-4-6 |
| 📊 **Market** | TAM/SAM/SOM, growth rates, key trends, market drivers | claude-sonnet-4-6 |
| 🔍 **Competitor** | Landscape mapping, player positioning, gaps | claude-sonnet-4-6 |
| ⚖️ **Regulatory** | Legal risks, compliance requirements, policy trends | claude-sonnet-4-6 |
| 📰 **News** | Recent events, announcements, momentum signals | claude-sonnet-4-6 |
| 💰 **Financial** | Funding rounds, valuations, unit economics | claude-sonnet-4-6 |
| 💬 **Sentiment** | Public perception, analyst opinions, brand signals | claude-sonnet-4-6 |
| 🎓 **Academic** | Peer-reviewed research, scientific consensus | claude-sonnet-4-6 |
| ✅ **Cross-Validator** | Contradiction detection, confidence scoring | claude-opus-4-6 |
| 📝 **Synthesizer** | Final report generation, executive summary | claude-opus-4-6 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│              Next.js 15 · TypeScript · Tailwind CSS             │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST + WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                          API LAYER                              │
│              FastAPI · Pydantic · Supabase JWT Auth             │
└──────┬───────────────────────────────────┬──────────────────────┘
       │                                   │
┌──────▼──────┐                 ┌──────────▼──────────┐
│   CELERY    │                 │      WEBSOCKET       │
│  Task Queue │                 │  Redis Pub/Sub       │
│  + Redis    │                 │  Live Agent Events   │
└──────┬──────┘                 └─────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│                  AGENT LAYER                        │
│                                                     │
│  OrchestratorAgent                                  │
│         │                                           │
│         ├── MarketAgent ──┐                         │
│         ├── CompetitorAgent                         │
│         ├── RegulatoryAgent  ← ThreadPoolExecutor   │
│         ├── NewsAgent        (parallel execution)   │
│         ├── FinancialAgent                          │
│         ├── SentimentAgent                          │
│         └── AcademicAgent ──┘                       │
│                  │                                  │
│         CrossValidatorAgent                         │
│                  │                                  │
│          SynthesisAgent                             │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│                  DATA LAYER                         │
│         PostgreSQL + pgvector · SQLAlchemy          │
│         Alembic Migrations · Redis Cache            │
└─────────────────────────────────────────────────────┘
```

**Real-time updates via WebSocket** — the frontend receives agent events (started / completed / failed) as they happen, updating a live progress grid.

---

## Tech Stack

### Backend
| | Technology | Why |
|---|---|---|
| **Framework** | FastAPI (Python 3.12) | Async-first, automatic OpenAPI docs, type safety |
| **Task Queue** | Celery + Redis | Parallel agent execution, retries, monitoring |
| **Database** | PostgreSQL + pgvector | Relational + vector embeddings for semantic search |
| **ORM** | SQLAlchemy 2.0 (async) | Type-safe queries, async session management |
| **Migrations** | Alembic | Schema versioning |
| **Package Manager** | uv | 10–100× faster than pip |

### AI & Search
| | Technology | Why |
|---|---|---|
| **LLM** | Anthropic Claude API | Best-in-class reasoning, structured JSON output |
| **Orchestration** | claude-opus-4-6 | Complex planning, validation, synthesis |
| **Research agents** | claude-sonnet-4-6 | Fast, cost-effective specialist agents |
| **Web Search** | Tavily API | Real-time search optimized for AI agents |
| **Deep Search** | Exa API | Semantic search for high-quality sources |

### Frontend
| | Technology | Why |
|---|---|---|
| **Framework** | Next.js 15.5 (App Router) | React Server Components, typed routes |
| **Styling** | Tailwind CSS | Utility-first, dark theme |
| **State** | Zustand + Immer | Lightweight, devtools-friendly |
| **Real-time** | WebSocket (custom client) | Live agent progress with auto-reconnect |
| **Auth** | Supabase Auth | Google OAuth + email, JWT auto-refresh |

### Infrastructure
| | Technology | Why |
|---|---|---|
| **Auth** | Supabase | Managed Postgres Auth, Row Level Security |
| **Payments** | Stripe | Subscriptions, usage-based billing |
| **Email** | Resend | Transactional email |
| **Hosting** | Railway (API) + Vercel (Frontend) | Zero-config deploys from GitHub |
| **Observability** | Logfire (optional) · Langfuse (planned) | Request tracing; LLM latency + cost tracking |
| **CI/CD** | GitHub Actions | Lint → Test → Deploy pipeline |

---

## Getting Started

### Prerequisites
- Python 3.12+ and [`uv`](https://docs.astral.sh/uv/)
- Node.js 22+
- Docker (for PostgreSQL + pgvector and Redis), or local installs of both
- API keys: Anthropic (required), Supabase project (required for sign-in), Tavily / Exa (recommended)

### 1. Configure environment

```bash
git clone https://github.com/VenkataAnilKumar/ParallaxAI.git
cd ParallaxAI

cp .env.example .env                          # backend — read from the repo root or backend/
cp frontend/.env.example frontend/.env.local  # frontend — NEXT_PUBLIC_* values
```

Fill in at least `ANTHROPIC_API_KEY`, the `SUPABASE_*` values (including `SUPABASE_JWT_SECRET`) and `SECRET_KEY`.

### 2. Run locally

```bash
# Infrastructure
docker compose up db redis -d

# Backend API (terminal 1)
cd backend
uv sync --extra dev
uv run alembic upgrade head        # creates the schema + pgvector extension
uv run uvicorn app.main:app --reload --port 8000

# Celery worker (terminal 2)
cd backend
uv run celery -A app.celery_app worker --loglevel=info

# Frontend (terminal 3)
cd frontend
npm install
npm run dev
```

| URL | What |
|---|---|
| http://localhost:3000 | Web app |
| http://localhost:8000/docs | Interactive API docs (disabled when `APP_ENV=production`) |
| http://localhost:8000/health | Health check |

> The API does not create tables on startup — always run `alembic upgrade head` after pulling new migrations.

### Or run the whole stack with Docker

```bash
docker compose up --build   # db, redis, api (runs migrations first), worker, flower (:5555)
```

### Environment Variables

**Backend** (`.env`):

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://parallax:parallax@localhost:5432/parallax
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=...                      # min 64 chars
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_JWT_SECRET=...             # Project Settings → API → JWT Secret

# Search (optional but recommended — agents fall back to model knowledge without them)
TAVILY_API_KEY=tvly-...
EXA_API_KEY=exa-...

# Payments (optional for dev)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Frontend** (`frontend/.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

See [`.env.example`](.env.example) and [`frontend/.env.example`](frontend/.env.example) for the full lists.

---

## API Overview

All REST endpoints require a Supabase access token: `Authorization: Bearer <jwt>`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/me` | Current user (auto-created on first request) |
| `POST` | `/api/v1/research` | Start a research task → `202` + task (`query`, `depth`, optional `agents`) |
| `GET` | `/api/v1/research` | List your tasks (paginated) |
| `GET` | `/api/v1/research/{id}` | Task status + per-agent runs |
| `DELETE` | `/api/v1/research/{id}` | Cancel a task |
| `GET` | `/api/v1/reports/research/{task_id}` | Report for a completed task |
| `POST` | `/api/v1/reports/{id}/share` | Create a share link |
| `GET` | `/api/v1/reports/{id}/export?format=markdown` | Download the report |
| `WS` | `/ws/research/{task_id}` | Live events: `agent.started`, `agent.completed`, `task.completed`, … |

Full reference: [docs/09-api-design.md](docs/09-api-design.md).

---

## Testing

```bash
cd backend
uv run ruff check app tests alembic   # lint
uv run mypy app                       # strict type check
uv run pytest --cov=app               # tests (needs PostgreSQL + Redis)

cd ../frontend
npm run type-check && npm run lint && npm run build
```

Backend tests use a real PostgreSQL database (`parallax_test`, pgvector required) and Redis — the DB is not mocked.
`tests/test_pipeline.py` runs the complete Celery research task with Claude and web search stubbed,
checking that agent runs, reports and token totals are persisted.

CI (`.github/workflows/pr.yml`) runs all of the above on every pull request to `main`.

---

## Project Structure

```
parallax/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── base.py              # BaseResearchAgent with retry logic
│   │   │   ├── orchestrator.py      # Query decomposition (claude-opus-4-6)
│   │   │   ├── validator.py         # Cross-validation (claude-opus-4-6)
│   │   │   ├── synthesizer.py       # Report generation (claude-opus-4-6)
│   │   │   └── research/            # 7 specialist agents
│   │   ├── api/
│   │   │   ├── routes/              # REST endpoints
│   │   │   └── websocket.py         # Real-time progress events
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── services/                # Business logic (billing, usage limits)
│   │   ├── tasks/research.py        # Celery parallel execution task
│   │   ├── core/auth.py             # Supabase JWT middleware
│   │   ├── config.py                # Pydantic Settings
│   │   └── main.py                  # FastAPI app entry point
│   ├── alembic/versions/            # DB migrations (0001 creates pgvector)
│   ├── tests/                       # API, search and end-to-end pipeline tests
│   └── pyproject.toml
│
├── frontend/
│   └── src/
│       ├── app/                     # Next.js App Router pages
│       ├── components/
│       │   ├── research/            # ResearchInput, AgentProgress, ReportViewer
│       │   └── layout/              # Sidebar, Header
│       ├── lib/
│       │   ├── api.ts               # Typed API client
│       │   ├── websocket.ts         # WebSocket client with auto-reconnect
│       │   └── supabase.ts          # Auth client
│       ├── stores/research.ts       # Zustand store
│       └── types/index.ts
│
├── docs/                            # 13 product & technical documents
├── docker-compose.yml               # db, redis, api, worker, flower
└── .github/workflows/               # CI/CD pipelines
```

---

## Documentation

| Document | Description |
|---|---|
| [01 — Product Vision](docs/01-product-vision.md) | What Parallax is, why it exists, 3-year vision |
| [02 — User Personas](docs/02-user-personas.md) | Who uses Parallax and why they pay |
| [03 — PRD](docs/03-prd.md) | Product requirements, user stories, success metrics |
| [04 — User Flow](docs/04-user-flow.md) | Step-by-step user journeys |
| [05 — Monetization](docs/05-monetization.md) | Pricing, unit economics, revenue model |
| [06 — System Architecture](docs/06-system-architecture.md) | End-to-end architecture |
| [07 — Tech Stack](docs/07-tech-stack.md) | Every technology and the rationale |
| [08 — Database Schema](docs/08-database-schema.md) | Full PostgreSQL schema + pgvector |
| [09 — API Design](docs/09-api-design.md) | All endpoints, WebSocket events, error codes |
| [10 — Agent Design](docs/10-agent-design.md) | Each agent's role, prompts, failure handling |
| [11 — Infrastructure](docs/11-infrastructure.md) | Deployment, CI/CD, monitoring, scaling |
| [12 — Competitive Analysis](docs/12-competitive-analysis.md) | Market landscape and positioning |
| [13 — Launch Plan](docs/13-launch-plan.md) | Pre-launch, launch day, 90-day growth plan |

---

## Pricing

| Plan | Price | Tasks/Month | Features |
|---|---|---|---|
| **Free** | $0 | 3 | Standard depth, web access |
| **Starter** | $49/mo | 30 | All depths, PDF + Markdown export |
| **Pro** | $199/mo | 100 | API access, priority queue |
| **Team** | $499/mo | Unlimited | Team workspace, shared history, SSO |

> **Unit economics:** Standard research task costs ~$0.82 in API costs. Pro plan at 100 tasks = $199 revenue vs $82 cost. **59% gross margin.**

---

## Roadmap

- [x] Product documentation (13 docs)
- [x] Backend API — FastAPI + Celery + 10 agents
- [x] Database schema — PostgreSQL + pgvector
- [x] Frontend — Next.js 15 + real-time WebSocket
- [x] Auth — Supabase JWT
- [x] CI/CD — GitHub Actions + Railway + Vercel
- [x] Tavily + Exa search integration (live web data)
- [x] Alembic migrations + end-to-end pipeline tests
- [ ] Supabase project setup + deployment
- [ ] Stripe subscription lifecycle (webhook handlers are stubs)
- [ ] API rate limiting
- [ ] PDF export
- [ ] Langfuse LLM tracing
- [ ] Beta launch
- [ ] Public launch

---

## Key Engineering Decisions

**Parallel execution via `ThreadPoolExecutor`** — All 7 research agents run concurrently in separate threads. A 7-agent Standard research completes in ~60–90s (the slowest agent's time), not 7× that.

**Structured JSON output from every agent** — Each agent returns a typed JSON schema. `parse_response()` handles malformed output gracefully with a confidence-penalized fallback — no silent failures.

**Redis pub/sub for real-time updates** — Celery workers publish agent events to Redis channels. The FastAPI WebSocket handler subscribes and streams them to the frontend in real time.

**pgvector for semantic deduplication** — Research findings are embedded and stored as 1536-dim vectors, enabling semantic similarity search across historical research tasks.

**Fault-tolerant pipeline** — A failing agent is recorded and skipped; the report is built from the agents that succeeded. If the orchestrator's plan fails, every requested agent still runs. The task fails only when no agent succeeds.

**Supabase JWT auto-provisioning** — On first request, the backend auto-creates a User record from the Supabase JWT claims. No separate registration flow needed.

---

## Contributing

Open an issue or a pull request against `main`. Before submitting, run the checks in [Testing](#testing) — CI runs the same ones.

---

<div align="center">

Built by [VenkataAnilKumar](https://github.com/VenkataAnilKumar) · Powered by [Claude API](https://anthropic.com)

</div>
