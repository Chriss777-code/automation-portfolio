# Parallel Stealth Research Tool v2 🔬🥷

**The ultimate research automation: Sub-agents + Stealth Scraping**

Combines three powerful capabilities:
1. **Sub-agents** - Parallel research workers
2. **Stealth browser** - Access protected sites
3. **Content aggregation** - Unified reports

## The Power Combo

```
┌─────────────────────────────────────────────────────────┐
│                    RESEARCH REQUEST                      │
│         "Analyze 5 competitors in 1 hour"               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              SUB-AGENTS (Parallel)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Agent 1 │ │ Agent 2 │ │ Agent 3 │ │ Agent 4 │  ...  │
│  │ Comp A  │ │ Comp B  │ │ Comp C  │ │ Comp D  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│      │           │           │           │              │
│      ▼           ▼           ▼           ▼              │
│   Results stream back as they complete (10-30s each)    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              STEALTH SCRAPE (Optional)                   │
│         Deep scrape protected pages with                │
│         DrissionPage anti-detection                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              UNIFIED REPORT                              │
│         All findings aggregated into                    │
│         markdown/HTML/JSON report                       │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from parallel_researcher_v2 import ParallelStealthResearcher, ResearchTarget

# Define research targets
targets = [
    ResearchTarget(name="Anthropic", query="Anthropic Claude pricing 2025"),
    ResearchTarget(name="OpenAI", query="OpenAI GPT-4 pricing 2025"),
    ResearchTarget(name="Google", query="Google Gemini pricing 2025"),
]

# Generate sub-agent tasks
researcher = ParallelStealthResearcher()
tasks = researcher.generate_subagent_tasks(targets)

# In OpenClaw, spawn all in parallel:
for task in tasks:
    sessions_spawn(**task)  # All run simultaneously!

# Results stream back as they complete
```

## Use Cases

| Use Case | Sub-agents | Stealth | Output |
|----------|------------|---------|--------|
| Competitive Analysis | ✅ 5 parallel | Optional | Report |
| Lead Qualification | ✅ 10 parallel | ✅ LinkedIn | CSV |
| Market Research | ✅ 8 parallel | ✅ Protected sources | Report |
| Price Monitoring | ✅ Discovery | ✅ E-commerce | Alerts |
| Content Curation | ✅ Research | ✅ Paywalled | Digest |

## Why This Is Powerful

### Before (Sequential)
```
Research A → 30s
Research B → 30s  
Research C → 30s
Research D → 30s
Research E → 30s
─────────────────
Total: 2.5 minutes
```

### After (Parallel Sub-agents)
```
Research A ─┐
Research B ─┤
Research C ─┼──→ 30s total
Research D ─┤
Research E ─┘
─────────────────
Total: 30 seconds (5x faster!)
```

## Stealth Scraping

For protected sites, add URLs to targets:

```python
target = ResearchTarget(
    name="Protected Site",
    query="Protected Site features",  # Sub-agent researches
    url="https://protected-site.com/pricing",  # Stealth scrapes
    scrape_selector="#pricing-table"  # Specific element
)
```

## Report Generation

```python
# Markdown (default)
report = researcher.generate_report(format="markdown")

# HTML (for email)
report = researcher.generate_report(format="html")

# JSON (for processing)
report = researcher.generate_report(format="json")

# Save to file
researcher.save_report("competitive_analysis", format="markdown")
```

## Requirements

```bash
# Sub-agents: OpenClaw with sessions_spawn
# Stealth: DrissionPage
pip install DrissionPage
```

## Pricing Advantage

| Model | Cost/1M tokens | Use For |
|-------|----------------|---------|
| Haiku | $0.25 | Simple fact-finding |
| Sonnet | $3.00 | Research (default) |
| Opus | $15.00 | Synthesis only |

**5 parallel Sonnet sub-agents ≈ $0.05 total**

## Author

Built by Neo (AI Assistant) during overnight 80% capability sprint.

## License

MIT
