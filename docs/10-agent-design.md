# Parallax — Agent Design

---

## Agent Overview

```
10 agents. Two phases. One report.

Phase 1 — Research (parallel):
├── Orchestrator Agent      → analyzes question, creates plan
├── Market Agent            → market size, trends, growth
├── Competitor Agent        → competitive landscape
├── Regulatory Agent        → laws, compliance, licensing
├── News Agent              → recent events, announcements
├── Financial Agent         → unit economics, benchmarks, funding
├── Sentiment Agent         → social media, forums, real opinions
└── Academic Agent          → papers, studies, technical research

Phase 2 — Synthesis (sequential):
├── Cross-Validator Agent   → contradictions, confidence scores
└── Synthesis Agent         → final report assembly
```

---

## Agent 1 — Orchestrator

**Role:** Analyze the research question and create the execution plan.

**Model:** `claude-opus-4-6` (needs best reasoning)

**Input:**
```python
{
  "question": str,           # user's research question
  "depth": str,              # quick | standard | deep
  "selected_agents": list    # which agents to use
}
```

**Output:**
```python
{
  "research_title": str,     # clean title for the report
  "core_intent": str,        # what user really wants to know
  "agent_assignments": [
    {
      "agent": str,          # agent type
      "question": str,       # specific sub-question for this agent
      "priority": int,       # 1 (highest) to 3 (lowest)
      "search_focus": list   # key terms to search for
    }
  ]
}
```

**System Prompt:**
```
You are a research orchestrator. Your job is to analyze a research question
and create a precise research plan for a team of specialist agents.

For each agent, create a specific, focused sub-question that:
1. Is clearly scoped to that agent's specialty
2. Contains the specific geographic, industry, or time context from the original question
3. Will produce actionable, concrete findings (not vague overviews)

Depth guidelines:
- quick: 3-4 agents, top-level questions
- standard: all agents, focused questions
- deep: all agents, exhaustive questions with multiple sub-angles

Return a JSON object with the structure specified.
```

---

## Agent 2 — Market Intelligence Agent

**Role:** Research market size, growth, trends, and industry dynamics.

**Model:** `claude-sonnet-4-6`

**Tools:**
- Tavily search (general web)
- Exa search (reports, whitepapers)

**Search strategy:**
```python
queries = [
  f"{market} market size {year}",
  f"{market} market growth rate CAGR",
  f"{market} industry trends {year}",
  f"{market} market forecast",
  f"{industry} total addressable market"
]
```

**Output structure:**
```python
{
  "findings": [
    {
      "claim": str,          # specific factual claim
      "data_point": str,     # specific number/stat if applicable
      "source_url": str,
      "source_title": str,
      "source_date": str,
      "credibility": str,    # high | medium | low
      "confidence": str      # high | medium | low
    }
  ],
  "key_statistics": {
    "market_size": str,      # e.g. "$4.2B (2024)"
    "growth_rate": str,      # e.g. "18% CAGR (2024-2029)"
    "key_players": list
  }
}
```

**System Prompt:**
```
You are a market intelligence specialist. Research the market described in the question.

Focus on:
1. Total addressable market (TAM) — cite specific figures with year and source
2. Market growth rate (CAGR) — cite specific research reports
3. Key market segments and their relative sizes
4. Major market trends shaping the industry
5. Key incumbents and their market share

Rules:
- Always cite specific numbers with source and year
- Note when data is outdated (>2 years old)
- Flag conflicting data points from different sources
- Mark your confidence: high (multiple sources agree) | medium (one credible source) | low (uncertain)
- Do not speculate — only report what sources say

Return structured JSON with findings and key statistics.
```

---

## Agent 3 — Competitor Intelligence Agent

**Role:** Map the competitive landscape, key players, positioning, and gaps.

**Model:** `claude-sonnet-4-6`

**Search strategy:**
```python
queries = [
  f"{market} competitors {year}",
  f"best {product_type} companies",
  f"{market} startups funding raised",
  f"{competitor_names} product features",
  f"{market} alternatives comparison"
]
```

**Output structure:**
```python
{
  "findings": [...],
  "competitors": [
    {
      "name": str,
      "website": str,
      "description": str,
      "target_market": str,
      "funding": str,
      "founded": str,
      "key_differentiator": str,
      "weaknesses": list,
      "source": str
    }
  ],
  "market_gaps": list,       # opportunities not covered by existing players
  "competitive_intensity": str  # high | medium | low
}
```

---

## Agent 4 — Regulatory & Legal Agent

**Role:** Research relevant laws, regulations, licensing requirements, and compliance landscape.

**Model:** `claude-sonnet-4-6`

**Search strategy:**
```python
queries = [
  f"{industry} regulations {country/region}",
  f"{product_type} license requirements {jurisdiction}",
  f"{industry} compliance requirements {year}",
  f"recent {industry} regulatory changes",
  f"{industry} legal risks"
]
```

**System Prompt:**
```
You are a regulatory research specialist. Research the legal and regulatory
landscape for the topic described.

Focus on:
1. Key regulations that apply (name the specific law/regulation)
2. Licensing requirements (what licenses needed, which authority grants them)
3. Recent regulatory changes (last 2 years)
4. Regulatory risks and upcoming changes
5. Jurisdiction-specific differences (if multi-country)

Rules:
- Always cite the specific regulation name and jurisdiction
- Note the date of regulations (may be outdated)
- Flag "seek legal counsel" for any interpretation of applicability
- Be specific about which jurisdictions you found information for
- Clearly state what you could NOT find information about

Confidence levels:
- High: Official government source or major law firm publication
- Medium: Legal news, industry publication
- Low: Forum, blog, or unclear source
```

---

## Agent 5 — News Intelligence Agent

**Role:** Find recent news, announcements, funding rounds, and market events.

**Model:** `claude-sonnet-4-6`

**Time focus:** Last 6-12 months only

**Search strategy:**
```python
queries = [
  f"{topic} news {current_year}",
  f"{topic} funding raised {current_year}",
  f"{topic} launched announced {current_year}",
  f"{company_names} news recent",
  f"{industry} merger acquisition {current_year}"
]
```

**Output structure:**
```python
{
  "findings": [...],
  "timeline": [
    {
      "date": str,
      "headline": str,
      "significance": str,   # why this matters
      "source_url": str,
      "event_type": str      # funding | launch | regulation | market_move | other
    }
  ]
}
```

---

## Agent 6 — Financial Intelligence Agent

**Role:** Research financial benchmarks, unit economics, pricing, and funding landscape.

**Model:** `claude-sonnet-4-6`

**Search strategy:**
```python
queries = [
  f"{business_model} unit economics benchmarks",
  f"{industry} revenue model pricing",
  f"{industry} gross margin benchmarks",
  f"{industry} CAC LTV benchmarks",
  f"{industry} Series A metrics typical"
]
```

**System Prompt:**
```
You are a financial intelligence analyst. Research financial benchmarks
and unit economics for the business described.

Focus on:
1. Revenue model options and typical pricing
2. Gross margin benchmarks for this industry
3. Key unit economics (CAC, LTV, payback period) — cite specific data
4. Funding landscape (typical raise amounts, valuations at each stage)
5. Profitability timeline for comparable companies

Rules:
- Always cite specific numbers with source
- Note when benchmarks vary widely — explain why
- Distinguish between B2B and B2C benchmarks
- Flag when data is from a different geography than the question
- Mark estimates clearly as estimates
```

---

## Agent 7 — Sentiment & Opinion Agent

**Role:** Research what real users, customers, and industry practitioners say.

**Model:** `claude-sonnet-4-6`

**Sources:** Reddit, Hacker News, Twitter/X, LinkedIn, G2, Trustpilot, forums

**Search strategy:**
```python
queries = [
  f"{product_type} site:reddit.com",
  f"{pain_point} complaints users site:reddit.com",
  f"{competitor} reviews",
  f"{topic} site:news.ycombinator.com",
  f"problems with {industry} solutions"
]
```

**System Prompt:**
```
You are a consumer sentiment analyst. Research what real users and practitioners
say about the topic — their pain points, preferences, and opinions.

Focus on:
1. Primary pain points users express (quote directly where possible)
2. What solutions people currently use and what they hate about them
3. What features/capabilities people wish existed
4. Recurring complaints about existing products
5. Positive signals — what approaches people love

Rules:
- Quote real user comments where possible (with source)
- Distinguish between professional/expert opinions and general users
- Note the recency of opinions (forum posts age quickly)
- Don't extrapolate one complaint to represent all users
- Flag when opinions are from a specific geography or demographic
```

---

## Agent 8 — Academic Research Agent

**Role:** Find academic papers, technical research, and evidence-based studies.

**Model:** `claude-sonnet-4-6`

**Tools:** Exa search (better for academic content), Semantic Scholar API

**Search strategy:**
```python
queries = [
  f"{topic} academic paper research",
  f"{topic} study findings site:arxiv.org",
  f"{topic} evidence research journal",
  f"{technology} technical analysis paper"
]
```

**Note:** This agent is skipped for market/business research questions where academic sources are unlikely. The orchestrator determines relevance.

---

## Agent 9 — Cross-Validator Agent

**Role:** Check all findings for contradictions, assign confidence scores, identify gaps.

**Model:** `claude-opus-4-6` (needs best reasoning for contradiction detection)

**Input:** All findings from all research agents (combined JSON)

**Process:**
```
1. Extract all quantitative claims (numbers, percentages, dates)
2. Group claims by topic
3. For each topic with multiple claims:
   a. Are they contradictory? (same metric, different values)
   b. If yes: check source credibility + recency → determine resolution
   c. If unresolvable: flag as contradiction with both sides
4. Assign confidence scores per section:
   - High: 3+ independent credible sources agree
   - Medium: 2 sources agree, or 1 highly credible source
   - Low: 1 source, conflicting data, or low-credibility source
5. Identify gaps: topics where insufficient data was found
```

**Output:**
```python
{
  "contradictions": [
    {
      "topic": str,
      "claim_a": str, "source_a": str, "agent_a": str,
      "claim_b": str, "source_b": str, "agent_b": str,
      "resolution": str,
      "resolved": bool
    }
  ],
  "confidence_by_section": {
    "market": "high",
    "competitor": "high",
    "regulatory": "medium",
    ...
  },
  "overall_confidence": str,
  "gaps": [
    {
      "angle": str,
      "description": str,
      "recommendation": str
    }
  ]
}
```

---

## Agent 10 — Synthesis Agent

**Role:** Assemble all validated findings into the final structured report.

**Model:** `claude-opus-4-6` (needs best writing + reasoning)

**Input:** All validated findings + cross-validation report

**Output:** Final report in markdown + structured JSON

**System Prompt:**
```
You are a senior research analyst assembling a final research report.
You have findings from multiple specialist agents, already cross-validated.

Your report must:
1. Executive Summary (3-5 bullet points, each a complete insight — not just a topic label)
2. Findings by Section (use agent sections, write in clear prose, include key data points)
3. Contradictions Found (explain what was contradictory and how it was resolved)
4. Data Gaps (be honest about what couldn't be found)
5. Source List (deduplicated, grouped by agent)
6. Suggested Next Questions (3-5 follow-up questions that would deepen this research)

Tone: Professional, direct, confident where data supports it, appropriately uncertain where it doesn't.
Format: Markdown with clear headers.
Length: Appropriate to depth — Quick: 500 words, Standard: 1500 words, Deep: 3000+ words.

Critical rules:
- Every data point must have a citation [Source Name, Year]
- Mark confidence clearly: **[High Confidence]** | **[Medium Confidence]** | **[Low Confidence]**
- Write for a decision-maker who will act on this research
- The executive summary must be actionable — not just descriptive
```

---

## Agent Failure Handling

```
Each agent has 3 retry attempts with exponential backoff.
If agent fails after retries:
├── Mark agent as failed in database
├── Push WebSocket event: agent_failed
├── Continue with remaining agents
├── Note in final report: "[Agent type] data unavailable due to error"
└── Do not charge user if >50% of agents failed

Timeout settings:
├── Quick depth:    agent timeout = 90 seconds
├── Standard depth: agent timeout = 3 minutes
└── Deep depth:     agent timeout = 8 minutes

If ALL agents fail:
├── Mark task as failed
├── Send error notification to user
├── Do not charge credits
└── Alert engineering team (PagerDuty)
```
