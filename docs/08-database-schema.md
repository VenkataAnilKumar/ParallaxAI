# Parallax — Database Schema

---

## Tables Overview

```
users                  → user accounts
workspaces             → team workspaces
workspace_members      → user ↔ workspace membership
subscriptions          → billing plans
usage_logs             → per-task usage tracking
research_tasks         → research job records
agent_runs             → individual agent execution records
research_findings      → structured findings per agent
cross_validations      → contradiction + confidence reports
reports                → final synthesized reports
report_shares          → public/private share links
```

---

## Schema

### users
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    name            TEXT,
    avatar_url      TEXT,
    auth_provider   TEXT NOT NULL DEFAULT 'email',  -- email | google
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);
```

### workspaces
```sql
CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    owner_id        UUID NOT NULL REFERENCES users(id),
    plan            TEXT NOT NULL DEFAULT 'free',
                    -- free | starter | pro | team | enterprise
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### workspace_members
```sql
CREATE TABLE workspace_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            TEXT NOT NULL DEFAULT 'member',  -- admin | member | viewer
    monthly_limit   INTEGER,  -- NULL = no limit (inherits workspace limit)
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, user_id)
);
```

### subscriptions
```sql
CREATE TABLE subscriptions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    stripe_customer_id  TEXT UNIQUE,
    stripe_sub_id       TEXT UNIQUE,
    plan                TEXT NOT NULL DEFAULT 'free',
    status              TEXT NOT NULL DEFAULT 'active',
                        -- active | past_due | canceled | trialing
    current_period_start TIMESTAMPTZ,
    current_period_end   TIMESTAMPTZ,
    tasks_limit         INTEGER,   -- NULL = unlimited
    api_calls_limit     INTEGER,   -- NULL = unlimited
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### usage_logs
```sql
CREATE TABLE usage_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    task_id         UUID REFERENCES research_tasks(id),
    usage_type      TEXT NOT NULL,  -- research_task | api_call
    depth           TEXT,           -- quick | standard | deep
    tokens_used     INTEGER,
    cost_usd        DECIMAL(10, 6),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_workspace_month
    ON usage_logs (workspace_id, date_trunc('month', created_at));
```

### research_tasks
```sql
CREATE TABLE research_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    user_id         UUID NOT NULL REFERENCES users(id),

    -- Input
    question        TEXT NOT NULL,
    depth           TEXT NOT NULL DEFAULT 'standard',  -- quick | standard | deep
    selected_agents TEXT[] NOT NULL DEFAULT ARRAY[
                    'market', 'competitor', 'regulatory',
                    'news', 'financial', 'sentiment', 'academic'
                    ],

    -- Status
    status          TEXT NOT NULL DEFAULT 'queued',
                    -- queued | planning | running | validating |
                    -- synthesizing | complete | failed | timeout
    error_message   TEXT,

    -- Timing
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_seconds INTEGER,

    -- Celery
    celery_task_id  TEXT,

    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_research_tasks_workspace ON research_tasks (workspace_id);
CREATE INDEX idx_research_tasks_user ON research_tasks (user_id);
CREATE INDEX idx_research_tasks_status ON research_tasks (status);
```

### agent_runs
```sql
CREATE TABLE agent_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,

    -- Agent info
    agent_type      TEXT NOT NULL,
                    -- orchestrator | market | competitor | regulatory |
                    -- news | financial | sentiment | academic |
                    -- cross_validator | synthesizer
    agent_question  TEXT,           -- sub-question assigned to this agent

    -- Status
    status          TEXT NOT NULL DEFAULT 'queued',
                    -- queued | running | complete | failed | timeout
    error_message   TEXT,

    -- Results
    searches_performed INTEGER DEFAULT 0,
    sources_found      INTEGER DEFAULT 0,
    findings_count     INTEGER DEFAULT 0,

    -- Cost tracking
    input_tokens    INTEGER DEFAULT 0,
    output_tokens   INTEGER DEFAULT 0,
    search_calls    INTEGER DEFAULT 0,
    cost_usd        DECIMAL(10, 6) DEFAULT 0,

    -- Timing
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_seconds INTEGER,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_runs_task ON agent_runs (task_id);
```

### research_findings
```sql
CREATE TABLE research_findings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,
    agent_run_id    UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,

    -- Finding content
    claim           TEXT NOT NULL,      -- the factual claim
    context         TEXT,               -- surrounding context
    source_url      TEXT,
    source_title    TEXT,
    source_date     DATE,
    source_credibility TEXT DEFAULT 'medium',  -- high | medium | low

    -- Categorization
    finding_type    TEXT,               -- fact | statistic | opinion | trend
    relevance_score DECIMAL(3, 2),      -- 0.00 to 1.00
    confidence      TEXT DEFAULT 'medium',  -- high | medium | low

    -- Vector embedding for semantic search
    embedding       vector(1536),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_findings_task ON research_findings (task_id);
CREATE INDEX idx_findings_embedding ON research_findings
    USING ivfflat (embedding vector_cosine_ops);
```

### cross_validations
```sql
CREATE TABLE cross_validations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES research_tasks(id) ON DELETE CASCADE,
    agent_run_id    UUID REFERENCES agent_runs(id),

    -- Contradictions found
    contradictions  JSONB DEFAULT '[]',
    -- [{
    --   "topic": "market size",
    --   "claim_a": "Market is $4.2B",
    --   "source_a": "agent: market",
    --   "claim_b": "Market is $6.8B",
    --   "source_b": "agent: financial",
    --   "resolution": "claim_a uses 2024 data, claim_b uses 2026 projection",
    --   "resolved": true
    -- }]

    -- Gaps found
    gaps            JSONB DEFAULT '[]',
    -- [{
    --   "angle": "regulatory",
    --   "description": "Could not find licensing requirements for Philippines",
    --   "recommendation": "Manual research recommended"
    -- }]

    -- Overall confidence
    overall_confidence TEXT DEFAULT 'medium',  -- high | medium | low
    confidence_by_agent JSONB DEFAULT '{}',
    -- { "market": "high", "regulatory": "medium", ... }

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### reports
```sql
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL UNIQUE REFERENCES research_tasks(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    user_id         UUID NOT NULL REFERENCES users(id),

    -- Report content
    title           TEXT NOT NULL,
    question        TEXT NOT NULL,
    executive_summary TEXT NOT NULL,   -- 3-5 bullet points (markdown)
    full_report     TEXT NOT NULL,     -- complete report (markdown)
    report_json     JSONB NOT NULL,    -- structured report data

    -- Metadata
    total_sources   INTEGER DEFAULT 0,
    total_agents    INTEGER DEFAULT 0,
    contradictions_found INTEGER DEFAULT 0,
    gaps_found      INTEGER DEFAULT 0,
    overall_confidence TEXT DEFAULT 'medium',

    -- Cost
    total_cost_usd  DECIMAL(10, 6),
    total_tokens    INTEGER,

    -- Timing
    research_duration_seconds INTEGER,

    -- Search
    search_vector   tsvector,   -- for full-text search

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_workspace ON reports (workspace_id);
CREATE INDEX idx_reports_user ON reports (user_id);
CREATE INDEX idx_reports_search ON reports USING gin(search_vector);

-- Auto-update search vector
CREATE TRIGGER reports_search_vector_update
    BEFORE INSERT OR UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(search_vector, 'pg_english', question, executive_summary);
```

### report_shares
```sql
CREATE TABLE report_shares (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    created_by      UUID NOT NULL REFERENCES users(id),

    share_token     TEXT UNIQUE NOT NULL DEFAULT gen_random_uuid()::TEXT,
    visibility      TEXT NOT NULL DEFAULT 'private',  -- private | public
    expires_at      TIMESTAMPTZ,    -- NULL = never expires

    view_count      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Key Indexes Summary

```sql
-- Fast workspace + time queries
CREATE INDEX idx_research_tasks_workspace_created
    ON research_tasks (workspace_id, created_at DESC);

-- Fast user history
CREATE INDEX idx_research_tasks_user_created
    ON research_tasks (user_id, created_at DESC);

-- Usage aggregation
CREATE INDEX idx_usage_workspace_month
    ON usage_logs (workspace_id, date_trunc('month', created_at));

-- Active subscriptions lookup
CREATE INDEX idx_subscriptions_workspace
    ON subscriptions (workspace_id) WHERE status = 'active';
```

---

## Migrations Strategy

```
Tool: Alembic (SQLAlchemy migrations)

Convention:
├── One migration file per schema change
├── Always include downgrade() function
├── Test migrations on staging before production
└── Never edit existing migration files

File naming:
YYYY_MM_DD_HHMM_description.py
Example: 2026_03_26_1000_initial_schema.py
```
