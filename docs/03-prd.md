# Parallax — Product Requirements Document (PRD)

## Overview
Parallax is a multi-agent research network that deploys specialized AI agents in parallel to research any question, cross-validates findings, and delivers a comprehensive, sourced, confidence-scored report.

---

## Goals

### Product Goals
- Deliver research reports 10x faster than manual research
- Cover more angles than any single researcher or agent
- Provide cross-validated, sourced, confidence-scored output
- Make professional-grade research accessible to individuals

### Business Goals
- Reach 500 paying users within 6 months of launch
- Achieve $50k MRR within 12 months
- Maintain <2% monthly churn
- NPS > 50

---

## User Stories

### Core Research Flow

**US-001: Submit Research Question**
```
As a user
I want to submit a research question in plain English
So that Parallax understands what I need researched

Acceptance Criteria:
- Text input accepts up to 1000 characters
- User can specify research depth (Quick / Standard / Deep)
- User can select focus areas (optional)
- Submission triggers immediate confirmation
- User sees estimated completion time
```

**US-002: Real-Time Agent Progress**
```
As a user
I want to see each agent's progress in real time
So that I know research is happening and how long it will take

Acceptance Criteria:
- Each agent shown with status: Queued / Running / Complete / Failed
- Progress updates via WebSocket (no page refresh needed)
- Each agent shows: name, angle, status, findings count
- Estimated time remaining updates dynamically
- If agent fails: shown as failed with reason, research continues
```

**US-003: Receive Research Report**
```
As a user
I want to receive a structured research report when complete
So that I can immediately use the findings

Acceptance Criteria:
- Executive summary (3-5 bullets, plain language)
- Findings organized by research angle
- Every claim has a source citation
- Confidence score (High/Medium/Low) per section
- Contradictions section: what agents disagreed on and resolution
- Gaps section: what couldn't be found
- Suggested follow-up questions
- Total research time shown
```

**US-004: Export Report**
```
As a user
I want to export my research report
So that I can share it or use it in other tools

Acceptance Criteria:
- Export to PDF (formatted, professional)
- Export to Markdown
- Export to Notion (direct integration)
- Copy shareable link (public or private)
- Download raw JSON (for API users)
```

**US-005: Research History**
```
As a user
I want to see all my past research
So that I can revisit and build on previous work

Acceptance Criteria:
- List of all research tasks with: question, date, status, depth
- Search and filter history
- Re-run any past research question
- Compare two reports on same topic
- Delete research (with confirmation)
```

---

### Agent Configuration

**US-006: Select Research Agents**
```
As a user
I want to choose which research agents run on my question
So that I can focus research on what matters most

Acceptance Criteria:
- Default: all agents auto-selected based on question type
- Manual: user can toggle agents on/off
- Preset configurations: "Quick Scan" / "Deep Dive" / "Competitive Intel"
- Saved configurations for reuse
```

**US-007: Research Depth Settings**
```
As a user
I want to control research depth
So that I can balance speed vs comprehensiveness

Acceptance Criteria:
- Quick (2-3 min): 3-4 agents, top-level findings
- Standard (5-8 min): all agents, standard depth
- Deep (15-20 min): all agents, exhaustive, more sources per agent
- Cost shown before running (credits/tokens)
```

---

### Account & Billing

**US-008: User Registration**
```
As a new user
I want to create an account
So that I can start using Parallax

Acceptance Criteria:
- Email + password signup
- Google OAuth
- Email verification required
- Free tier starts immediately on verification
- Onboarding: first research question guided
```

**US-009: Subscription Management**
```
As a user
I want to manage my subscription
So that I can upgrade, downgrade, or cancel

Acceptance Criteria:
- Current plan shown with usage
- One-click upgrade / downgrade
- Cancel anytime (no lock-in)
- Billing history downloadable
- Usage alerts at 80% and 100% of plan limits
```

**US-010: Team Workspace**
```
As a team admin
I want to manage a shared workspace
So that my team can collaborate on research

Acceptance Criteria:
- Invite team members by email
- Shared research history visible to team
- Individual usage tracking per member
- Admin can set per-member limits
- Centralized billing
```

---

## Feature Prioritization

### P0 — Launch Blockers
```
- Research question submission
- Agent orchestration (parallel execution)
- Real-time progress via WebSocket
- Report generation (structured output)
- PDF export
- User auth (email + Google)
- Stripe billing
- Free tier + paid plans
```

### P1 — Launch Week
```
- Research history
- Report sharing (link)
- Agent selection (manual toggle)
- Depth settings (Quick/Standard/Deep)
- Markdown export
```

### P2 — Month 1 Post-Launch
```
- Team workspaces
- Notion export
- Saved agent configurations
- Research comparison
- Usage analytics dashboard
- API access (for developers)
```

### P3 — Quarter 2
```
- Standing research (scheduled / event-triggered)
- Slack integration
- Custom agents (user-defined)
- Research templates library
- White-label (enterprise)
```

---

## Out of Scope (v1)
```
- Mobile app (web responsive only)
- Real-time collaboration (multiple users editing same report)
- Integration with paid data sources (Bloomberg, PitchBook)
- Voice input
- Agent marketplace
- Self-improving agents
```

---

## Success Metrics

### Activation
- User runs first research within 10 minutes of signup: >60%
- User runs 3+ research tasks in first week: >30%

### Engagement
- Weekly active users / Monthly active users: >40%
- Research tasks per active user per week: >5
- Report export rate: >50% of completed reports

### Retention
- Day 7 retention: >50%
- Day 30 retention: >30%
- Monthly churn (paid): <3%

### Quality
- User satisfaction score (post-report): >4.2/5
- Report re-run rate (indicator of quality issues): <10%
- Support tickets per 100 research tasks: <2

---

## Constraints

### Technical
- Report generation must complete within 10 minutes (Standard depth)
- System must handle 100 concurrent research tasks at launch
- Agent failures must not block report delivery (graceful degradation)
- All data encrypted at rest and in transit

### Legal
- Research output must include source citations (copyright compliance)
- No storage of personally identifiable information beyond account data
- GDPR compliant (EU users)
- Terms of service must limit use for harmful research

### Business
- Free tier must not exceed $2 in API costs per user per month
- Paid plans must maintain >60% gross margin
