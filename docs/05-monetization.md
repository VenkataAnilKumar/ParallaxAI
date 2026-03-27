# Parallax — Monetization

---

## Pricing Tiers

### Free
**Target:** Individuals trying Parallax for the first time
```
Price:        $0/month
Research:     5 tasks/month
Depth:        Standard only
Agents:       All agents (limited sources per agent)
Export:       None (view only)
History:      Last 5 reports
Support:      Community only
```

### Starter — $49/month
**Target:** Founders, journalists, individual analysts
```
Price:        $49/month ($39/month annual)
Research:     50 tasks/month
Depth:        Quick + Standard + Deep
Agents:       All agents, full sources
Export:       PDF + Markdown
History:      Unlimited
Report share: Public links
Support:      Email (48hr response)
```

### Pro — $199/month
**Target:** VCs, consultants, senior analysts
```
Price:        $199/month ($159/month annual)
Research:     200 tasks/month
Depth:        All depths
Agents:       All agents + priority queue
Export:       PDF + Markdown + Notion + JSON
History:      Unlimited + search
API access:   1,000 API calls/month
Report share: Public + private links
Support:      Email (24hr response)
Custom:       Save agent configurations
```

### Team — $499/month
**Target:** Strategy teams, VC firms, consulting teams
```
Price:        $499/month ($399/month annual)
Seats:        Up to 10 members
Research:     Unlimited tasks
Depth:        All depths, priority queue
Agents:       All agents
Export:       All formats
History:      Shared team workspace
API access:   10,000 API calls/month
Report share: Team + public + private
Support:      Dedicated Slack channel
Admin:        Usage analytics, per-member limits
SSO:          SAML/OKTA (enterprise add-on)
```

### Enterprise — Custom
**Target:** Large enterprises, financial institutions
```
Price:        Custom (starting $2,000/month)
Seats:        Unlimited
Research:     Unlimited
Deployment:   Cloud or on-premise
Data:         Private data sources integration
Compliance:   SOC 2, custom DPA
Support:      Dedicated customer success
SLA:          99.9% uptime guarantee
```

---

## Unit Economics

### API Cost per Research Task

```
Standard Depth Research:

Orchestrator (claude-opus-4-6):
    Input:  ~2,000 tokens  = $0.030
    Output: ~1,000 tokens  = $0.045

8 Research Agents (claude-sonnet-4-6 each):
    Input:  ~3,000 tokens  = $0.009 each
    Output: ~2,000 tokens  = $0.012 each
    Per agent: $0.021 × 8 = $0.168

Cross-Validator (claude-opus-4-6):
    Input:  ~8,000 tokens  = $0.120
    Output: ~2,000 tokens  = $0.090

Synthesis (claude-opus-4-6):
    Input:  ~10,000 tokens = $0.150
    Output: ~4,000 tokens  = $0.180

Web Search API (Tavily):
    ~40 searches total     = $0.040

Total cost per Standard task: ~$0.823
```

### Margin by Plan

```
Free (5 tasks):
    Revenue:    $0
    Cost:       5 × $0.82 = $4.10
    Margin:     -$4.10 (acquisition cost)

Starter ($49, 50 tasks):
    Revenue:    $49
    Cost:       50 × $0.82 = $41.00
    Gross margin: $8 (16%) ← need to optimize

Pro ($199, 200 tasks):
    Revenue:    $199
    Cost:       200 × $0.82 = $164.00
    Gross margin: $35 (18%)

Team ($499, unlimited):
    Revenue:    $499
    Cost:       ~300 tasks avg × $0.82 = $246
    Gross margin: $253 (51%) ← profitable
```

### Cost Optimization Strategy

```
1. Model routing:
   Simple research angles → claude-sonnet-4-6 (75% cheaper than opus)
   Complex synthesis only → claude-opus-4-6
   Saves: ~35% on model costs

2. Caching:
   Same/similar questions → serve cached results
   Cache hit rate target: 20%
   Saves: ~20% on repeat research

3. Prompt optimization:
   Reduce tokens per agent by 30% through prompt engineering
   Saves: ~30% on input costs

4. Search API negotiation:
   Volume discount at 1M+ searches/month
   Saves: ~25% on search costs

Target gross margin after optimization:
   Starter: 45%
   Pro: 60%
   Team: 70%
```

---

## Revenue Model

### Primary: Subscriptions (80% of revenue)
Monthly recurring revenue from Starter, Pro, Team plans.

### Secondary: API (15% of revenue)
Developers and enterprises using Parallax programmatically.
```
API pricing:
    Pay-as-you-go:  $1.50 per research task
    API bundles:    $99/mo = 100 tasks, $299/mo = 400 tasks
```

### Tertiary: Enterprise (5% → growing)
Custom contracts for large organizations.

---

## Growth Strategy

### Month 1-3: Validation
```
Target: 100 paying users
Channel: Direct outreach to VCs, consultants, founders
Goal: Find what users love + what's broken
Pricing: Offer 50% discount to first 100 users
```

### Month 4-6: Growth
```
Target: 500 paying users, $25k MRR
Channel: Content marketing, Product Hunt launch, referrals
Goal: Find repeatable acquisition channel
Referral: Give 1 free month for each referred paying user
```

### Month 7-12: Scale
```
Target: 2,000 paying users, $100k MRR
Channel: SEO, partnerships, sales (Team + Enterprise)
Goal: Predictable growth engine
```

---

## Competitive Pricing Context

```
Perplexity Pro:    $20/month  (no multi-agent, no cross-validation)
ChatGPT Plus:      $20/month  (no research focus, no agents)
Consensus (AI):    $9/month   (academic only)
Crayon (intel):    $500/month (competitor tracking only)
Gartner reports:   $5,000+    (static, outdated)
Research firms:    $10,000+   (slow, manual)

Parallax Starter:  $49/month  → 10x cheaper than research firms
Parallax Pro:      $199/month → still 50x cheaper than research firms
```

Parallax is priced as a **professional tool**, not a consumer app.
The comparison is not ChatGPT — it's a research analyst.
