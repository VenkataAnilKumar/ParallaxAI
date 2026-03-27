# Parallax — API Design

**Base URL:** `https://api.parallax.app/v1`
**Auth:** Bearer token (JWT from Supabase Auth)
**Format:** JSON request/response
**Versioning:** URL path (`/v1/`)

---

## Authentication

All endpoints require:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## Research Endpoints

### POST /research
Create a new research task.

**Request:**
```json
{
  "question": "Should I build a B2B payments product for SMBs in Southeast Asia?",
  "depth": "standard",
  "agents": ["market", "competitor", "regulatory", "news", "financial", "sentiment", "academic"]
}
```

**Response 202 Accepted:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "estimated_duration_seconds": 360,
  "websocket_url": "wss://api.parallax.app/ws/research/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-03-26T10:00:00Z"
}
```

**Errors:**
```json
// 402 Payment Required
{ "error": "usage_limit_exceeded", "message": "Monthly research limit reached", "upgrade_url": "https://parallax.app/pricing" }

// 422 Validation Error
{ "error": "validation_error", "detail": [{ "field": "question", "message": "Question is required" }] }
```

---

### GET /research/{task_id}
Get task status and agent progress.

**Response 200:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "Should I build a B2B payments product...",
  "depth": "standard",
  "status": "running",
  "created_at": "2026-03-26T10:00:00Z",
  "started_at": "2026-03-26T10:00:05Z",
  "estimated_completion": "2026-03-26T10:06:05Z",
  "agents": [
    {
      "type": "orchestrator",
      "status": "complete",
      "duration_seconds": 12,
      "started_at": "2026-03-26T10:00:05Z",
      "completed_at": "2026-03-26T10:00:17Z"
    },
    {
      "type": "market",
      "status": "running",
      "duration_seconds": 142,
      "started_at": "2026-03-26T10:00:17Z",
      "completed_at": null,
      "searches_performed": 8,
      "findings_count": 0
    },
    {
      "type": "competitor",
      "status": "complete",
      "duration_seconds": 118,
      "started_at": "2026-03-26T10:00:17Z",
      "completed_at": "2026-03-26T10:02:15Z",
      "searches_performed": 12,
      "findings_count": 23
    },
    {
      "type": "news",
      "status": "complete",
      "duration_seconds": 89,
      "started_at": "2026-03-26T10:00:17Z",
      "completed_at": "2026-03-26T10:01:46Z",
      "searches_performed": 6,
      "findings_count": 14
    }
  ]
}
```

---

### GET /research/{task_id}/report
Get the final research report.

**Response 200:**
```json
{
  "report_id": "660e8400-e29b-41d4-a716-446655440001",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "B2B Payments for SE Asia SMBs — Research Report",
  "question": "Should I build a B2B payments product for SMBs in Southeast Asia?",
  "generated_at": "2026-03-26T10:06:19Z",
  "duration_seconds": 374,

  "executive_summary": [
    "The SE Asia B2B payments market is $4.2B and growing at 18% CAGR, with SMBs underserved by existing solutions",
    "GrabPay, PayNow, and Xendit dominate, but none focus exclusively on B2B SMB cross-border payments",
    "Regulatory complexity across 6 countries is the primary barrier — licensing required in each market",
    "SMBs report payment delays (avg 14 days) and high FX fees (2-4%) as top pain points",
    "Recommended entry: Singapore → Malaysia corridor with B2B invoice financing angle"
  ],

  "sections": [
    {
      "agent": "market",
      "title": "Market & Industry",
      "confidence": "high",
      "content": "...",
      "key_findings": [...],
      "sources": [...]
    }
  ],

  "contradictions": [
    {
      "topic": "Market size",
      "claim_a": "Market valued at $4.2B (2024)",
      "source_a": "McKinsey Digital Payments Report",
      "claim_b": "Market valued at $6.8B (2024)",
      "source_b": "Statista Fintech Report",
      "resolution": "McKinsey uses B2B-only definition; Statista includes B2C. Using McKinsey figure.",
      "resolved": true
    }
  ],

  "gaps": [
    {
      "angle": "financial",
      "description": "Proprietary unit economics data not publicly available",
      "recommendation": "Consider reaching out to Xendit or PayFazz directly"
    }
  ],

  "sources": [
    {
      "url": "https://example.com/report",
      "title": "SE Asia Fintech Report 2026",
      "date": "2026-01-15",
      "credibility": "high",
      "cited_by": ["market", "financial"]
    }
  ],

  "suggested_questions": [
    "What is the regulatory process to obtain a payment license in Singapore?",
    "Which SE Asia B2B payment startups have raised Series A in 2025-2026?",
    "What are the typical conversion rates for B2B payment products targeting SMBs?"
  ],

  "metadata": {
    "total_agents": 8,
    "total_sources": 47,
    "total_findings": 142,
    "contradictions_found": 2,
    "gaps_found": 1,
    "overall_confidence": "high",
    "total_cost_usd": 0.82,
    "total_tokens": 68420
  }
}
```

**Response 202 (still processing):**
```json
{
  "status": "running",
  "message": "Research still in progress",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET /research
List research history.

**Query params:**
- `limit` (default: 20, max: 100)
- `offset` (default: 0)
- `status` (filter by status)
- `search` (full-text search on question)

**Response 200:**
```json
{
  "total": 47,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "task_id": "550e8400-...",
      "question": "Should I build a B2B payments product...",
      "status": "complete",
      "depth": "standard",
      "created_at": "2026-03-26T10:00:00Z",
      "duration_seconds": 374,
      "overall_confidence": "high"
    }
  ]
}
```

---

### DELETE /research/{task_id}
Delete a research task and its report.

**Response 204 No Content**

---

## Report Endpoints

### POST /reports/{report_id}/share
Create a share link.

**Request:**
```json
{
  "visibility": "public",
  "expires_in_days": 30
}
```

**Response 201:**
```json
{
  "share_url": "https://parallax.app/share/abc123xyz",
  "token": "abc123xyz",
  "visibility": "public",
  "expires_at": "2026-04-25T10:00:00Z"
}
```

---

### GET /reports/{report_id}/export
Export report in specified format.

**Query params:** `format` = `pdf` | `markdown` | `json`

**Response:** File download with appropriate Content-Type

---

## User & Account Endpoints

### GET /me
Get current user info.

**Response 200:**
```json
{
  "user_id": "abc123",
  "email": "venkata@example.com",
  "name": "Venkata",
  "workspace": {
    "id": "ws_123",
    "name": "Personal",
    "plan": "pro"
  },
  "usage": {
    "period_start": "2026-03-01",
    "period_end": "2026-03-31",
    "tasks_used": 47,
    "tasks_limit": 200,
    "api_calls_used": 120,
    "api_calls_limit": 1000
  }
}
```

---

## WebSocket

### WS /ws/research/{task_id}
Real-time research progress.

**Connection:**
```
wss://api.parallax.app/ws/research/{task_id}?token={jwt_token}
```

**Events received:**

```json
// Agent started
{
  "event": "agent_started",
  "agent": "market",
  "timestamp": "2026-03-26T10:00:17Z"
}

// Agent progress update
{
  "event": "agent_progress",
  "agent": "competitor",
  "searches_performed": 5,
  "timestamp": "2026-03-26T10:01:00Z"
}

// Agent complete
{
  "event": "agent_complete",
  "agent": "news",
  "findings_count": 14,
  "duration_seconds": 89,
  "timestamp": "2026-03-26T10:01:46Z"
}

// Agent failed (non-blocking)
{
  "event": "agent_failed",
  "agent": "academic",
  "error": "Search API timeout",
  "timestamp": "2026-03-26T10:03:00Z"
}

// Validation started
{
  "event": "validation_started",
  "timestamp": "2026-03-26T10:05:00Z"
}

// Synthesis started
{
  "event": "synthesis_started",
  "timestamp": "2026-03-26T10:05:45Z"
}

// Research complete
{
  "event": "research_complete",
  "task_id": "550e8400-...",
  "report_id": "660e8400-...",
  "duration_seconds": 374,
  "timestamp": "2026-03-26T10:06:14Z"
}

// Research failed
{
  "event": "research_failed",
  "task_id": "550e8400-...",
  "error": "All agents failed",
  "timestamp": "2026-03-26T10:06:14Z"
}
```

---

## Error Codes

```
400 Bad Request         → Invalid request body
401 Unauthorized        → Missing or invalid JWT
402 Payment Required    → Usage limit exceeded
403 Forbidden           → Not authorized for this resource
404 Not Found           → Resource doesn't exist
422 Unprocessable       → Validation error
429 Too Many Requests   → Rate limit hit
500 Internal Error      → Server error (we get alerted)
503 Service Unavailable → Maintenance or overload
```

---

## Rate Limits

```
Free:    10 requests/minute
Starter: 60 requests/minute
Pro:     300 requests/minute
Team:    600 requests/minute

Research creation specifically:
Free:    1 concurrent task
Starter: 3 concurrent tasks
Pro:     10 concurrent tasks
Team:    30 concurrent tasks
```
