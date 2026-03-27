# Parallax — Competitive Analysis

---

## Competitive Landscape Map

```
                    HIGH DEPTH
                        │
            Parallax ●  │  ● Research firms
                        │    ($10,000+)
                        │
SINGLE ─────────────────┼───────────────── MULTI
AGENT                   │                  AGENT
                        │
         Perplexity ●   │
         ChatGPT ●      │
                        │
                    LOW DEPTH
```

---

## Direct Competitors

### Perplexity AI
```
What it is:    AI-powered search engine with citations
Pricing:       Free + $20/month Pro
Strengths:     Fast, good UI, real-time web search, citations
Weaknesses:
├── Single agent (one perspective only)
├── No cross-validation between sources
├── No structured research report format
├── No confidence scoring
├── Not designed for deep research workflows
└── No parallel research angles
Verdict: Most similar product, but fundamentally different depth
```

### ChatGPT + Plugins / Deep Research
```
What it is:    General AI with some research capability
Pricing:       $20/month
Strengths:     Brand recognition, large user base
Weaknesses:
├── Single agent, sequential research
├── Hallucination risk, no source verification
├── No cross-validation
├── Not purpose-built for research workflows
└── Deep Research feature: still single-thread
Verdict: General tool, not a research product
```

### Claude.ai
```
What it is:    General AI assistant (our own model)
Pricing:       Free + $20/month Pro
Strengths:     Best reasoning, large context window
Weaknesses:
├── Not a research product — general assistant
├── No web search by default
├── No agent orchestration
└── No structured output format
Verdict: We use Claude as our engine, not our competition
```

---

## Indirect Competitors

### Consensus
```
What it is:    AI search for academic papers only
Pricing:       Free + $9/month
Strengths:     Academic focus, credible sources
Weaknesses:
├── Academic papers only (no news, market data, web)
├── Single source type
└── Not for business research
Verdict: Different niche (academic), not direct competitor
```

### Crayon
```
What it is:    Competitive intelligence platform
Pricing:       ~$500/month+
Strengths:     Continuous competitor monitoring, team features
Weaknesses:
├── Only tracks competitors (not broader research)
├── Very expensive
├── No ad-hoc research questions
└── Requires significant setup
Verdict: Overlaps on competitive intel use case only
```

### AlphaSense
```
What it is:    Financial research platform (earnings calls, filings)
Pricing:       $3,000-10,000/month (enterprise)
Strengths:     Best for financial/enterprise research, proprietary data
Weaknesses:
├── Extremely expensive
├── Financial focus only
└── Not for general market research
Verdict: Enterprise financial segment we don't compete with initially
```

### Gartner / Forrester Reports
```
What it is:    Traditional analyst firm reports
Pricing:       $5,000-15,000 per report
Strengths:     Brand credibility, detailed analyst insight
Weaknesses:
├── Very expensive
├── Takes weeks to months
├── Often outdated by time of purchase
└── Can't answer custom questions
Verdict: Same outcome (research report), radically different model
```

---

## What Parallax Does Differently

```
Feature                  Perplexity   ChatGPT   Parallax
─────────────────────────────────────────────────────────
Multi-agent parallel        ✗           ✗          ✓
Cross-validation            ✗           ✗          ✓
Confidence scoring          ✗           ✗          ✓
Structured report format    Partial     ✗          ✓
Contradiction detection     ✗           ✗          ✓
Research gaps identified    ✗           ✗          ✓
Suggested follow-ups        ✗           Partial    ✓
Depth control               ✗           ✗          ✓
Research history            ✗           ✓          ✓
Team workspace              ✗           ✗          ✓
PDF export                  ✗           ✗          ✓
API access                  ✗           ✓          ✓
Real-time agent progress    ✗           ✗          ✓
```

---

## Positioning Statement

```
For VCs, consultants, and founders
who need comprehensive, reliable research fast,

Parallax is the multi-agent research network
that researches every angle simultaneously and cross-validates findings,

unlike Perplexity or ChatGPT
which research from a single perspective with no verification.
```

---

## Moat Analysis

```
Short-term moat (launch):
├── Multi-agent architecture (3-6 months to copy)
├── Cross-validation feature (unique, hard to replicate well)
└── Research quality + structured output format

Medium-term moat (6-18 months):
├── Research history + institutional memory per user
├── Improving agent prompts from usage data
├── Brand trust ("Parallax research is reliable")
└── Team workflows + collaboration features

Long-term moat (18+ months):
├── Research quality data (which agents produce best results)
├── Agent self-improvement from feedback signals
├── API ecosystem (other tools integrate Parallax)
└── Enterprise contracts (switching cost)

Biggest risk:
Perplexity or OpenAI ships multi-agent research.
Mitigation: Ship fast, get users, build the quality data moat.
```

---

## Pricing Comparison

```
Tool               Price        Research quality    Speed
──────────────────────────────────────────────────────────
Research firm      $10,000+     Best (human)        Weeks
Gartner report     $5,000+      Very high           Months
AlphaSense         $3,000/mo    High (financial)    Hours
Crayon             $500/mo      Medium (competitor) Real-time
Parallax Pro       $199/mo      High (multi-agent)  Minutes
Perplexity Pro     $20/mo       Medium (single)     Seconds
ChatGPT Plus       $20/mo       Low (hallucination) Seconds
```

Parallax wins on: **quality vs price** and **speed vs quality**
