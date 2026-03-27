# Parallax — User Flow

---

## Flow 1 — New User Onboarding

```
Landing Page
    │
    ├── [Try Free] clicked
    │
    ▼
Sign Up Page
    ├── Email + Password
    └── Continue with Google
    │
    ▼
Email Verification (if email signup)
    │
    ▼
Onboarding — Step 1
"What do you research most?"
    ├── Market research
    ├── Competitive intelligence
    ├── Due diligence
    ├── Academic / technical
    └── Other
    │
    ▼
Onboarding — Step 2
"Ask Parallax your first question"
    └── Pre-filled example based on selection above
    │
    ▼
First Research Running
    └── User watches agents work in real time
    │
    ▼
First Report Delivered
    └── Guided tour overlay: explain sections
    │
    ▼
Dashboard (Home)
```

---

## Flow 2 — Core Research Flow

```
Dashboard
    │
    ├── [New Research] clicked
    │
    ▼
Research Input Screen
    ├── Question text area (up to 1000 chars)
    ├── Depth selector: [Quick] [Standard ✓] [Deep]
    ├── Focus areas (optional toggles):
    │   ├── Market & Industry
    │   ├── Competition
    │   ├── Regulatory & Legal
    │   ├── Financial
    │   ├── Sentiment & Opinion
    │   ├── Academic & Research
    │   └── News & Recent Events
    └── [Start Research] button
    │
    ▼
Research In Progress Screen
    ┌─────────────────────────────────────────────┐
    │  Researching: "B2B payments in SE Asia"     │
    │  Estimated: 6 minutes remaining             │
    ├─────────────────────────────────────────────┤
    │  ● Orchestrator          ✓ Complete          │
    │  ● Market Agent          ⟳ Running (2m 14s) │
    │  ● Competitor Agent      ⟳ Running (1m 52s) │
    │  ● Regulatory Agent      ⟳ Running (2m 01s) │
    │  ● News Agent            ✓ Complete (8 src) │
    │  ● Financial Agent       ○ Queued            │
    │  ● Sentiment Agent       ○ Queued            │
    │  ● Cross-Validator       ○ Waiting           │
    │  ● Synthesis Agent       ○ Waiting           │
    └─────────────────────────────────────────────┘
    │
    ▼ (agents complete one by one)
    │
    ▼
Report Ready — Notification (email + in-app)
    │
    ▼
Research Report Screen
    ┌─────────────────────────────────────────────┐
    │  PARALLAX RESEARCH REPORT                   │
    │  B2B Payments in Southeast Asia             │
    │  Generated: March 26, 2026 · 6m 14s        │
    ├─────────────────────────────────────────────┤
    │  EXECUTIVE SUMMARY                          │
    │  • [3-5 key findings]                       │
    ├─────────────────────────────────────────────┤
    │  FINDINGS BY ANGLE                          │
    │  ├── Market & Industry      [High confidence]│
    │  ├── Competitive Landscape  [High confidence]│
    │  ├── Regulatory Environment [Med confidence] │
    │  ├── Financial Benchmarks   [High confidence]│
    │  └── Consumer Sentiment     [Med confidence] │
    ├─────────────────────────────────────────────┤
    │  CONTRADICTIONS FOUND (2)                   │
    │  ├── Market size: $4.2B vs $6.8B            │
    │  └── Regulatory: resolved (old law cited)   │
    ├─────────────────────────────────────────────┤
    │  GAPS (what we couldn't find)               │
    │  └── Proprietary pricing data not available │
    ├─────────────────────────────────────────────┤
    │  SUGGESTED NEXT QUESTIONS (3)               │
    └─────────────────────────────────────────────┘
    │
    ├── [Export PDF]
    ├── [Copy Link]
    ├── [Export Markdown]
    ├── [Run Again]
    └── [Ask Follow-up]
```

---

## Flow 3 — Export Flow

```
Research Report Screen
    │
    ├── [Export PDF] clicked
    │       └── PDF generated → browser download
    │
    ├── [Copy Link] clicked
    │       ├── Link options:
    │       │   ├── Private (only you)
    │       │   └── Public (anyone with link)
    │       └── Link copied to clipboard → toast notification
    │
    └── [Export Markdown] clicked
            └── .md file downloaded
```

---

## Flow 4 — Research History

```
Dashboard → [History] tab
    │
    ▼
History Screen
    ├── Search bar
    ├── Filter: [All] [This Week] [This Month]
    ├── Sort: [Newest] [Oldest] [Most Sources]
    │
    └── Research list:
        ├── [Question text] [Date] [Status] [Depth]
        ├── [Question text] [Date] [Status] [Depth]
        └── ...
    │
    ▼ (click any item)
    │
    Research Report Screen (view past report)
        ├── [Re-run] → runs same question again
        └── [Compare] → select another report to compare
```

---

## Flow 5 — Upgrade / Billing

```
Dashboard → Usage bar hits 80%
    │
    ▼
Usage Alert Banner
"You've used 80% of your monthly research limit"
[View Plans] [Dismiss]
    │
    ├── [View Plans] clicked
    │
    ▼
Pricing Page
    ├── Free:    5 research/mo,  Standard only,  no export
    ├── Starter: 50 research/mo, all depths,     PDF export  ($49/mo)
    ├── Pro:     200 research/mo, all features,  API access  ($199/mo)
    └── Team:    Unlimited,       team workspace, priority    ($499/mo)
    │
    ▼ (select plan)
    │
Stripe Checkout
    └── Card details → confirm
    │
    ▼
Upgrade Confirmation
    └── Plan active immediately
    └── Usage limit updated in dashboard
```

---

## Flow 6 — Team Workspace

```
Dashboard → [Settings] → [Team]
    │
    ▼
Team Management Screen
    ├── [Invite Member] → email input → send invite
    ├── Member list: [Name] [Email] [Role] [Usage]
    ├── Role options: [Admin] [Member] [Viewer]
    └── Per-member usage limits (optional)
    │
Invited User:
    ├── Receives email invite
    ├── Clicks link → account creation or login
    └── Joins workspace → sees shared research history
```

---

## Error States

```
Agent Failure (partial):
    └── Agent marked failed, research continues with remaining agents
        Report delivered with: "Note: [agent] data unavailable"

All Agents Failed:
    └── Error screen: "Research could not be completed"
        [Retry] [Contact Support]
        No credits deducted

Timeout (>15 minutes):
    └── Research marked as timed out
        Partial results shown if available
        No credits deducted

Rate Limit Hit:
    └── "You've reached your monthly limit"
        [Upgrade] [View Usage]
```
