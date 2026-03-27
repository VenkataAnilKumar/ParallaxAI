# Parallax — Multi-Agent Research Network

> One question. Ten specialized agents. One complete picture.

Parallax deploys a coordinated team of AI research agents in parallel — each investigating a different angle of your question simultaneously. A cross-validation agent checks for contradictions. A synthesis agent assembles everything into one structured, sourced, confidence-scored research report.

**What used to take 3 days takes 6 minutes.**

---

## The Problem

Research today is slow, shallow, and unverified.

- **Slow** — manual research takes hours or days
- **Shallow** — one person or one AI sees one perspective
- **Unverified** — contradictory sources with no way to resolve them

## The Solution

```
You ask: "Should I build a B2B payments product in Southeast Asia?"

Parallax deploys 10 agents in parallel:
├── Market Agent          → market size, growth, TAM
├── Competitor Agent      → who's in the space, gaps
├── Regulatory Agent      → licensing, compliance per country
├── News Agent            → recent events, funding rounds
├── Financial Agent       → unit economics, benchmarks
├── Sentiment Agent       → what users actually say
├── Academic Agent        → research papers, studies
├── Cross-Validator       → finds contradictions, scores confidence
└── Synthesis Agent       → assembles the final report

Delivered in 6 minutes. Cross-validated. Source-cited. Confidence-scored.
```

---

## Documentation

| Document | Description |
|---|---|
| [Product Vision](docs/01-product-vision.md) | What Parallax is, why it exists, and the 3-year vision |
| [User Personas](docs/02-user-personas.md) | Who uses Parallax and why they pay |
| [PRD](docs/03-prd.md) | Product requirements, user stories, success metrics |
| [User Flow](docs/04-user-flow.md) | Step-by-step user journeys |
| [Monetization](docs/05-monetization.md) | Pricing, unit economics, revenue model |
| [System Architecture](docs/06-system-architecture.md) | How Parallax works end-to-end |
| [Tech Stack](docs/07-tech-stack.md) | Every technology and why we chose it |
| [Database Schema](docs/08-database-schema.md) | Full PostgreSQL schema |
| [API Design](docs/09-api-design.md) | All endpoints, WebSocket events, error codes |
| [Agent Design](docs/10-agent-design.md) | Each agent's role, prompts, and failure handling |
| [Infrastructure](docs/11-infrastructure.md) | Deployment, CI/CD, monitoring, scaling |
| [Competitive Analysis](docs/12-competitive-analysis.md) | Market landscape and positioning |
| [Launch Plan](docs/13-launch-plan.md) | Pre-launch, launch day, and 90-day growth plan |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind + shadcn/ui |
| Backend | FastAPI (Python) |
| Task Queue | Celery + Redis |
| Database | PostgreSQL + pgvector |
| LLM | Claude API (claude-opus-4-6 + claude-sonnet-4-6) |
| Search | Tavily API + Exa API |
| Auth | Supabase Auth |
| Payments | Stripe |
| Email | Resend |
| Hosting | Railway (API) + Vercel (Frontend) |
| Observability | Langfuse + Logfire |

---

## Pricing

| Plan | Price | Research Tasks | Key Features |
|---|---|---|---|
| Free | $0 | 5/month | Standard depth, view only |
| Starter | $49/month | 50/month | All depths, PDF export |
| Pro | $199/month | 200/month | API access, all exports |
| Team | $499/month | Unlimited | Team workspace, shared history |

---

## Project Status

- [x] Product documentation complete
- [ ] Backend API (FastAPI)
- [ ] Agent implementation
- [ ] Frontend (Next.js)
- [ ] Auth + Billing
- [ ] Beta launch
- [ ] Public launch

---

*Built by Venkata · Powered by Claude API*
