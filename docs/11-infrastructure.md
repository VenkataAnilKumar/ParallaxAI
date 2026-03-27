# Parallax — Infrastructure

---

## Environments

```
Local Development  → Docker Compose (PostgreSQL + Redis)
Staging            → Railway (mirrors production)
Production         → Railway (API + Workers) + Vercel (Frontend)
```

---

## Production Infrastructure

```
┌─────────────────────────────────────────────────┐
│                   VERCEL                         │
│           Next.js Frontend (CDN)                 │
│      parallax.app + edge network (global)        │
└────────────────────────┬────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────┐
│                  RAILWAY                         │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │   parallax-api (FastAPI)                 │   │
│  │   2 instances minimum                    │   │
│  │   Auto-scale up to 10 on load           │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │   parallax-worker (Celery)               │   │
│  │   4 workers minimum                      │   │
│  │   Auto-scale up to 20 on queue depth    │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌────────────────┐  ┌───────────────────────┐  │
│  │ PostgreSQL 15  │  │  Redis 7              │  │
│  │ 2 vCPU 4GB RAM │  │  1 vCPU 2GB RAM      │  │
│  │ Daily backups  │  │  Task queue + cache   │  │
│  └────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Deployment Pipeline

### On Pull Request
```yaml
# .github/workflows/pr.yml
jobs:
  test:
    - Install dependencies (uv + pnpm)
    - Run Python tests (pytest)
    - Run TypeScript tests (vitest)
    - Type check (mypy + tsc)
    - Lint (ruff + eslint)
    - Check migrations don't break schema

  preview:
    - Deploy frontend to Vercel preview URL
    - Post preview URL as PR comment
```

### On Merge to Main
```yaml
# .github/workflows/deploy.yml
jobs:
  deploy-api:
    - Build Docker image
    - Push to Railway container registry
    - Deploy to Railway (zero-downtime rolling deploy)
    - Run post-deploy smoke tests
    - Notify Slack on success/failure

  deploy-frontend:
    - Vercel auto-deploys on push to main
    - No additional configuration needed

  run-migrations:
    - After API deployment
    - Alembic upgrade head
    - Verify migration success
```

---

## Docker Setup

### API Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies
COPY pyproject.toml .
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Local Dev)
```yaml
version: '3.9'
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: parallax
      POSTGRES_USER: parallax
      POSTGRES_PASSWORD: parallax
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://parallax:parallax@db:5432/parallax
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app  # hot reload in dev

  worker:
    build: .
    command: uv run celery -A app.celery worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://parallax:parallax@db:5432/parallax
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## Environment Variables

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
EXA_API_KEY=exa-...

# Database
DATABASE_URL=postgresql://user:pass@host:5432/parallax
REDIS_URL=redis://host:6379/0

# Auth
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Payments
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
RESEND_API_KEY=re_...
FROM_EMAIL=research@parallax.app

# Observability
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LOGFIRE_TOKEN=...

# App
APP_ENV=production
API_URL=https://api.parallax.app
FRONTEND_URL=https://parallax.app
SECRET_KEY=<random-64-char-string>
```

---

## Monitoring & Alerting

### Health Checks
```python
# GET /health
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "celery_workers": 4,
  "queue_depth": 12,
  "version": "1.2.0"
}
```

### Key Metrics to Monitor
```
API:
├── Response time p50, p95, p99
├── Error rate (5xx)
├── Request rate
└── Active WebSocket connections

Worker:
├── Queue depth (alert if >50)
├── Task success rate
├── Task duration p50, p95
└── Worker count

Agent:
├── Per-agent success rate
├── Per-agent duration
├── Per-agent cost
└── LLM API error rate

Business:
├── Research tasks per hour
├── Cost per task (must stay <$1.50)
├── New signups per day
└── Plan upgrades per day
```

### Alerts (PagerDuty / Slack)
```
CRITICAL (page on-call):
├── API error rate > 5%
├── All Celery workers down
├── Database connection failed
└── Queue depth > 100 for >5 minutes

WARNING (Slack alert):
├── API response time p95 > 2s
├── Single agent failure rate > 20%
├── Cost per task > $2.00
├── Queue depth > 50
└── LLM API rate limit hit
```

---

## Backup Strategy

```
PostgreSQL:
├── Railway automated daily backups (7 day retention)
├── Manual weekly backup to S3 (30 day retention)
└── Point-in-time recovery available (Railway Pro)

Redis:
├── Persistence: RDB snapshots every 15 minutes
└── AOF logging enabled

Reports (markdown + JSON):
├── Stored in PostgreSQL (backed up with DB)
└── Consider S3 if reports grow large
```

---

## Scaling Plan

```
Stage 1 (0-500 users):
├── API: 2 instances (Railway Hobby)
├── Workers: 4 Celery workers
├── DB: PostgreSQL 2vCPU/4GB
├── Cost: ~$100-200/month infrastructure

Stage 2 (500-2000 users):
├── API: 4-8 instances (auto-scale)
├── Workers: 8-20 Celery workers (auto-scale)
├── DB: PostgreSQL 4vCPU/8GB + read replica
├── Cost: ~$400-800/month infrastructure

Stage 3 (2000+ users):
├── API: Kubernetes on AWS EKS
├── Workers: Separate scaling group
├── DB: RDS PostgreSQL Multi-AZ
├── Cache: ElastiCache Redis Cluster
├── CDN: CloudFront for API responses
└── Cost: $2000+/month infrastructure
```
