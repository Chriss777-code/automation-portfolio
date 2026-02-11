# Parallel Research Tool 🔬

**Leverage AI sub-agents for 5-8x faster research**

This tool demonstrates how to structure work for parallel AI research using OpenClaw's sub-agent feature.

## The Problem

Traditional AI research is sequential:
1. Research topic A → wait → results
2. Research topic B → wait → results  
3. Research topic C → wait → results

Total time: 3x the wait.

## The Solution

Parallel sub-agents:
1. Spawn sub-agent for topic A
2. Spawn sub-agent for topic B
3. Spawn sub-agent for topic C
4. All results stream back simultaneously

Total time: 1x the wait.

## Use Cases

- **Competitive Analysis**: Research 5 competitors in parallel
- **Market Research**: Investigate multiple market aspects simultaneously
- **Lead Qualification**: Qualify 10 leads at once
- **Content Research**: Gather sources for articles in parallel
- **Due Diligence**: Research multiple aspects of a company

## Cost Optimization

```
Model     | Cost/1M tokens | When to use
----------|----------------|---------------------------
Haiku     | $0.25         | Simple fact-finding
Sonnet    | $3.00         | Analysis and synthesis
Opus      | $15.00        | Final synthesis only
```

**Strategy**: Use Haiku for parallel fact-gathering, Sonnet for initial analysis, Opus only for final synthesis.

## Example: Competitor Analysis

```python
from parallel_researcher import research_competitor_landscape

competitors = ["Anthropic", "OpenAI", "Google DeepMind"]
researcher = research_competitor_landscape(competitors)

# Get prompts ready for OpenClaw
prompts = researcher.generate_subagent_prompts()

# In OpenClaw, spawn sub-agents:
for prompt in prompts:
    sessions_spawn(
        task=prompt["task"],
        model=prompt["model"],
        runTimeoutSeconds=prompt["runTimeoutSeconds"]
    )
```

## Output

Each sub-agent returns:
- Key findings (3-5 bullet points)
- Source credibility assessment
- Confidence rating
- Suggested follow-ups

Final synthesis combines all results into a unified report.

## Requirements

- OpenClaw with sub-agent support
- Max 8 concurrent sub-agents (platform limit)

## Author

Built by Neo (AI Assistant) during overnight skill building session.

## License

MIT
