# Parallax — Tech Stack

---

## Stack Overview

```
Layer               Technology              Why
─────────────────────────────────────────────────────────
Frontend            Next.js 14 + TypeScript  SSR, fast, great DX
Styling             Tailwind + shadcn/ui     Production-ready components
State               Zustand                  Lightweight, simple
Real-time           WebSocket (native)       Agent progress updates
Backend             FastAPI (Python)         Async, fast, AI ecosystem
Task Queue          Celery + Redis           Parallel agent execution
Database            PostgreSQL               Reliable, relational, pgvector
ORM                 SQLAlchemy + Alembic     Migrations, type-safe queries
LLM                 Claude API (Anthropic)   Best reasoning for research
Search              Tavily API               Best web search for agents
Auth                Supabase Auth            Fast to integrate, scalable
Payments            Stripe                   Industry standard
Email               Resend                   Simple, reliable
Hosting (API)       Railway                  Easy Python deployment
Hosting (Frontend)  Vercel                   Best Next.js deployment
Monitoring          Langfuse                 Agent observability
Logging             Logfire (Pydantic)       Structured logging
CI/CD               GitHub Actions           Automated testing + deploy
```

---

## Frontend

### Next.js 14 (App Router)
```
Why:
├── Server-side rendering → fast initial load, good SEO
├── App Router → better layouts, loading states, error boundaries
├── API routes → simple BFF pattern
├── TypeScript native → type safety throughout
└── Vercel deployment → zero-config, instant

Key pages:
├── / (landing)
├── /app (dashboard + research input)
├── /app/research/[id] (progress + report view)
├── /app/history (past research)
├── /app/settings (account, billing, team)
└── /login, /signup
```

### Tailwind CSS + shadcn/ui
```
Why shadcn/ui:
├── Copy-paste components (not a dependency)
├── Radix UI underneath (accessible)
├── Tailwind-based (customizable)
└── Production-quality out of the box

Key components needed:
├── Research input (textarea + options)
├── Agent progress cards (animated)
├── Report sections (collapsible, confidence badges)
├── Data tables (history, sources)
└── Pricing table
```

### Zustand (State Management)
```
Why not Redux/Context:
├── 5x less boilerplate
├── No provider wrapping
├── Works perfectly with Next.js App Router
└── Enough for Parallax's state complexity

State stores:
├── researchStore: current task state, agent progress
├── reportStore: current report data
├── userStore: auth state, plan, usage
└── uiStore: modals, toasts, sidebar
```

---

## Backend

### FastAPI (Python)
```
Why Python:
├── Best AI/LLM ecosystem (Anthropic SDK, LangChain, etc.)
├── Celery is Python-native → seamless integration
├── Async support → handles many concurrent requests
└── Type hints → Pydantic models → automatic OpenAPI docs

Why FastAPI over Django/Flask:
├── Async-first (critical for agent workloads)
├── Automatic API docs (Swagger/OpenAPI)
├── Pydantic validation out of the box
└── 3-5x faster than Flask for I/O-bound work

Structure:
parallax-api/
├── app/
│   ├── main.py              ← FastAPI app
│   ├── api/
│   │   ├── research.py      ← research endpoints
│   │   ├── reports.py       ← report endpoints
│   │   ├── auth.py          ← auth endpoints
│   │   └── billing.py       ← Stripe endpoints
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── research/
│   │   │   ├── market.py
│   │   │   ├── competitor.py
│   │   │   ├── regulatory.py
│   │   │   ├── news.py
│   │   │   ├── financial.py
│   │   │   ├── sentiment.py
│   │   │   └── academic.py
│   │   ├── validator.py
│   │   └── synthesizer.py
│   ├── models/              ← SQLAlchemy models
│   ├── schemas/             ← Pydantic schemas
│   ├── services/            ← business logic
│   └── core/                ← config, db, auth
├── celery_worker.py
├── requirements.txt
└── Dockerfile
```

### Celery + Redis
```
Why Celery:
├── Python-native async task queue
├── Parallel task execution (fan-out pattern for agents)
├── Task retry with exponential backoff
├── Task monitoring (Flower dashboard)
└── Integrates perfectly with FastAPI

Task design:
@celery.task
def run_research_task(task_id: str):
    # Orchestrate → fan out to agents → validate → synthesize

@celery.task
def run_agent(agent_type: str, question: str, task_id: str):
    # Individual agent execution

Why Redis (not RabbitMQ):
├── Also used for caching (one service, two uses)
├── Simpler to operate
├── Celery works great with Redis
└── Railway offers managed Redis
```

---

## Database

### PostgreSQL
```
Why:
├── ACID compliant → reliable for billing/usage data
├── pgvector extension → store embeddings for semantic search
├── JSON columns → flexible agent output storage
├── Full-text search → search research history
└── Excellent Python support (psycopg2, asyncpg)

Managed options:
├── Supabase PostgreSQL (free tier, easy setup)
├── Railway PostgreSQL (same platform as API)
└── Neon (serverless PostgreSQL, good for variable load)
```

### SQLAlchemy + Alembic
```
Why:
├── Type-safe queries
├── Migration management (Alembic)
├── Async support (asyncpg)
└── Industry standard in Python
```

---

## AI & Research

### Claude API (Anthropic)
```
Model routing:
├── claude-opus-4-6:    Orchestrator, Cross-Validator, Synthesis
│                       (complex reasoning, higher cost)
└── claude-sonnet-4-6:  Individual research agents
                        (good reasoning, lower cost)

Why Claude over GPT-4o:
├── Better at following complex structured output instructions
├── Larger context window (handles long research compilations)
├── Better at identifying contradictions
└── More reliable JSON output
```

### Tavily Search API
```
Why Tavily over Google/Bing:
├── Built specifically for AI agents
├── Returns clean, parsed content (not just URLs)
├── Includes content snippets ready for LLM consumption
├── Better relevance for research queries
└── Reasonable pricing ($0.001 per search)

Alternative: Exa.ai (better for academic/technical content)
Use both: Tavily for general, Exa for academic agent
```

---

## Auth, Payments, Email

### Supabase Auth
```
Why:
├── 5-minute setup
├── Email + social (Google, GitHub)
├── JWT tokens compatible with FastAPI
├── Row-level security (RLS) for PostgreSQL
└── Free tier generous enough for launch
```

### Stripe
```
Why: Industry standard, best documentation
Implementation:
├── Stripe Checkout → payment page (hosted)
├── Stripe Webhooks → handle subscription events
├── Stripe Portal → customer self-service billing
└── Stripe Meter → usage-based billing (API tier)
```

### Resend
```
Why: Simple API, great deliverability, generous free tier
Emails sent:
├── Email verification
├── Research complete notification
├── Usage limit warnings (80%, 100%)
├── Team invitations
└── Billing receipts
```

---

## Infrastructure & Deployment

### Railway (API + Workers + Redis + PostgreSQL)
```
Why:
├── Deploy Python apps without Dockerfile complexity
├── Managed PostgreSQL and Redis on same platform
├── Auto-deploy from GitHub
├── Simple environment variable management
└── Reasonable pricing for early-stage

Services on Railway:
├── parallax-api (FastAPI)
├── parallax-worker (Celery)
├── parallax-redis (managed Redis)
└── parallax-db (managed PostgreSQL)
```

### Vercel (Frontend)
```
Why:
├── Best Next.js deployment (made by Next.js creators)
├── Zero-config deployment
├── Edge network (fast globally)
├── Free tier covers early stage
└── Preview deployments for every PR
```

### GitHub Actions (CI/CD)
```
Pipeline:
On PR:
├── Run tests (pytest + vitest)
├── Type check (mypy + tsc)
├── Lint (ruff + eslint)
└── Preview deployment (Vercel)

On merge to main:
├── Run full test suite
├── Build Docker image
├── Deploy to Railway (API + workers)
└── Deploy to Vercel (frontend)
```

---

## Monitoring & Observability

### Langfuse (Agent Observability)
```
Why:
├── Designed specifically for LLM apps
├── Tracks: prompts, completions, costs, latency per agent
├── Identifies which agents are slow or expensive
└── Open source (self-hostable later)

Tracked for each research task:
├── Per-agent: tokens used, cost, latency, output quality
├── Total task: cost, duration, success/failure
└── Aggregated: daily cost, p50/p95 latency, error rate
```

### Logfire (Application Logging)
```
Structured logging for:
├── API requests/responses
├── Task queue events
├── Agent execution logs
├── Error tracking
└── User activity (anonymized)
```

---

## Development Tools

```
Python:
├── uv (package manager — faster than pip)
├── ruff (linting + formatting)
├── mypy (type checking)
├── pytest (testing)
└── pytest-asyncio (async test support)

JavaScript:
├── pnpm (package manager)
├── eslint + prettier (linting + formatting)
├── vitest (unit testing)
└── Playwright (E2E testing)

Development:
├── Docker Compose (local PostgreSQL + Redis)
├── Bruno (API testing — Postman alternative)
└── Cursor / Claude Code (AI-assisted development)
```
