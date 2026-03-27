# Parallax — System Architecture

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│              Next.js Web App (React + TypeScript)                │
│         REST API calls + WebSocket for real-time updates         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                         API LAYER                                │
│                   FastAPI (Python)                               │
│         Auth │ Research │ Reports │ Users │ Billing              │
└──────┬────────────────────────────────────────┬─────────────────┘
       │                                        │
┌──────▼──────────┐                  ┌──────────▼──────────────┐
│   TASK QUEUE    │                  │      DATABASE            │
│   Redis +       │                  │   PostgreSQL             │
│   Celery        │                  │   + pgvector             │
└──────┬──────────┘                  └─────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                           │
│                   Orchestrator Agent                             │
│   Analyzes question → determines angles → spawns research agents │
└──────┬──────────────────────────────────────────────────────────┘
       │
       │ (spawns in parallel)
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    RESEARCH AGENT LAYER                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Market   │ │Competitor│ │Regulatory│ │  News    │  ...more  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                           │
              (all results collected)
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   VALIDATION LAYER                               │
│                 Cross-Validator Agent                            │
│      Checks contradictions │ Scores confidence │ Fills gaps      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   SYNTHESIS LAYER                                │
│                   Synthesis Agent                                │
│         Assembles report │ Formats output │ Adds citations       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│  Tavily Search API │ Claude API │ Stripe │ Resend (email)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. API Layer (FastAPI)

```python
# Core responsibility: handle HTTP requests, auth, routing

Endpoints:
POST   /api/research          → create research task
GET    /api/research/{id}     → get task status + progress
GET    /api/research/{id}/report → get final report
GET    /api/research          → list user's research history
DELETE /api/research/{id}     → delete research task

WS     /ws/research/{id}      → real-time progress updates

POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

GET    /api/usage             → current plan usage
POST   /api/billing/upgrade   → upgrade plan (Stripe)

GET    /api/reports/{id}/export → export report (PDF/MD)
POST   /api/reports/{id}/share  → create share link
```

### 2. Task Queue (Redis + Celery)

```
Purpose: Async execution of research tasks
         Prevents API timeouts (research takes 5-15 minutes)

Flow:
1. API receives research request
2. API creates task record in PostgreSQL
3. API pushes task to Redis queue
4. API returns task_id immediately to client
5. Celery worker picks up task
6. Worker runs orchestration → research → validation → synthesis
7. Worker updates task status in PostgreSQL at each step
8. WebSocket pushes updates to connected client
9. Worker marks task complete, stores report

Queue configuration:
- research_quick:    priority queue, 4 workers
- research_standard: standard queue, 8 workers
- research_deep:     low-priority queue, 4 workers
```

### 3. WebSocket Layer

```
Purpose: Real-time progress updates to client

Events pushed to client:
{
  "event": "agent_started",
  "agent": "market_agent",
  "timestamp": "2026-03-26T10:00:00Z"
}

{
  "event": "agent_complete",
  "agent": "market_agent",
  "findings_count": 12,
  "duration_seconds": 142,
  "timestamp": "2026-03-26T10:02:22Z"
}

{
  "event": "research_complete",
  "task_id": "abc123",
  "report_ready": true,
  "total_duration_seconds": 374
}
```

### 4. Orchestrator Agent

```
Input:  User's research question + depth setting + selected agents
Output: Research plan (list of angles + assigned agents + prompts)

Process:
1. Analyze question → identify key research dimensions
2. Determine which agents are relevant
3. Generate specific sub-questions for each agent
4. Determine agent execution order (parallel where possible)
5. Return execution plan

Example:
Question: "Should I build a B2B payments product for SE Asia SMBs?"

Plan generated:
[
  { agent: "market", question: "What is the size and growth of B2B payments market in SE Asia? Focus on SMB segment." },
  { agent: "competitor", question: "Who are the main B2B payment providers for SMBs in SE Asia? Include local and global players." },
  { agent: "regulatory", question: "What are the payment regulations and licensing requirements in Singapore, Malaysia, Indonesia, Thailand, Vietnam, Philippines?" },
  { agent: "financial", question: "What are typical revenue models, take rates, and unit economics for B2B payment products?" },
  { agent: "sentiment", question: "What do SE Asian SMB owners say about their payment pain points? What existing solutions do they use and hate?" },
  { agent: "news", question: "What are recent developments in SE Asia fintech, B2B payments, and SMB banking in the last 6 months?" },
  { agent: "academic", question: "Are there research papers on SMB payment adoption in emerging markets?" }
]
```

### 5. Research Agents (Parallel Execution)

```
Each agent follows the same pattern:

Input:  Specific research sub-question + depth setting
Output: Structured findings { claims[], sources[], confidence }

Internal process:
1. Decompose sub-question into search queries (3-10 queries)
2. Execute searches via Tavily API (parallel)
3. Process search results (filter, deduplicate, rank)
4. Extract key claims from results
5. Verify claims across multiple sources
6. Structure findings with citations
7. Return structured output

Execution: All agents run in parallel via Celery
           Standard depth: 5-8 minutes total
           Quick depth: 2-3 minutes total
           Deep depth: 15-20 minutes total
```

### 6. Cross-Validator Agent

```
Input:  All research agent outputs (combined)
Output: Validated findings + contradiction report + confidence scores

Process:
1. Extract all claims across all agents
2. Group similar/related claims
3. Identify contradictions (same topic, different data)
4. For each contradiction:
   a. Check source credibility
   b. Check recency of sources
   c. Determine most likely truth or flag as unresolved
5. Assign confidence scores:
   - High: 3+ independent sources agree
   - Medium: 2 sources agree, or 1 highly credible source
   - Low: 1 source, unverified, or conflicting data
6. Identify gaps: research angles with insufficient findings
```

### 7. Synthesis Agent

```
Input:  Validated findings + contradiction report + confidence scores
Output: Final structured report (markdown)

Report structure:
- Executive Summary (3-5 bullet points)
- Key Findings by Angle (with confidence)
- Contradictions & Resolutions
- Data Gaps
- Source List (deduplicated, ranked by credibility)
- Suggested Follow-up Questions

Model: claude-opus-4-6 (best reasoning for synthesis)
```

---

## Data Flow Diagram

```
User Input
    │
    ▼
[API] Create Task → PostgreSQL (status: queued)
    │
    ├── Return task_id → Client
    │
    ▼
[Redis] Task queued
    │
    ▼
[Celery Worker] Pick up task
    │
    ▼
[Orchestrator] Analyze question → Generate agent plan
    │         Update PostgreSQL (status: planning)
    │
    ▼
[Celery] Spawn N agent tasks (parallel)
    │
    ├── [Market Agent]     ──┐
    ├── [Competitor Agent] ──┤
    ├── [Regulatory Agent] ──┤→ Each writes findings to PostgreSQL
    ├── [News Agent]       ──┤   Each pushes WebSocket event on complete
    ├── [Financial Agent]  ──┤
    ├── [Sentiment Agent]  ──┤
    └── [Academic Agent]   ──┘
    │
    ▼ (all agents complete or timeout)
    │
[Cross-Validator] Read all findings → Validate → Write validation report
    │         Push WebSocket: "Validating findings..."
    │
    ▼
[Synthesis Agent] Read validated findings → Generate report
    │         Push WebSocket: "Generating report..."
    │
    ▼
[PostgreSQL] Store final report (status: complete)
[Redis] Invalidate any relevant caches
[WebSocket] Push: "Research complete"
[Resend] Send email notification to user
    │
    ▼
Client fetches report via GET /api/research/{id}/report
```

---

## Scalability Design

```
Horizontal scaling:
├── API servers: stateless → scale with load balancer
├── Celery workers: add workers as queue grows
├── Redis: Redis Cluster for high availability
└── PostgreSQL: read replicas for report queries

Bottlenecks and mitigations:
├── Claude API rate limits → request queuing + exponential backoff
├── Tavily API limits → multiple API keys + caching
├── DB write contention → agent results use upsert, not insert
└── WebSocket connections → use Redis pub/sub across API instances

Caching strategy:
├── Identical questions (same hash) → return cached report (24hr TTL)
├── Similar questions → surface related past reports
└── Source content → cache fetched URLs (1hr TTL)
```
