#!/usr/bin/env python3
"""
Parallel Research Tool - Uses AI sub-agents for parallel research

This tool demonstrates how to structure work for OpenClaw's sub-agent feature.
Instead of sequential research, spawn multiple sub-agents to research in parallel.

Usage in OpenClaw:
- Each research topic becomes a sub-agent task
- Up to 8 concurrent sub-agents
- Results automatically reported back to main session

Example:
>>> topics = ["competitor analysis", "market trends", "pricing research"]
>>> for topic in topics:
...     sessions_spawn(task=f"Research: {topic}", model="sonnet")
>>> # Results stream back as sub-agents complete

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ResearchTask:
    """A single research task for a sub-agent."""
    topic: str
    scope: str  # "narrow", "broad", "deep"
    sources: List[str]  # ["web", "academic", "social", "news"]
    max_results: int = 5
    model: str = "sonnet"  # or "haiku" for cheaper
    timeout_seconds: int = 120


@dataclass
class ResearchResult:
    """Result from a sub-agent research task."""
    topic: str
    findings: List[str]
    sources_used: List[str]
    confidence: float  # 0-1
    tokens_used: int
    duration_seconds: float
    timestamp: str


class ParallelResearcher:
    """
    Orchestrates parallel research using OpenClaw sub-agents.
    
    Design Pattern:
    1. Break complex research into independent tasks
    2. Spawn sub-agents for each task (up to 8 concurrent)
    3. Collect and synthesize results
    4. Generate unified report
    
    Cost Optimization:
    - Use Haiku for simple fact-finding
    - Use Sonnet for analysis
    - Reserve Opus for synthesis only
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = min(max_concurrent, 8)  # OpenClaw limit
        self.tasks: List[ResearchTask] = []
        self.results: List[ResearchResult] = []
    
    def add_task(self, topic: str, scope: str = "narrow", 
                 sources: Optional[List[str]] = None, 
                 model: str = "sonnet") -> None:
        """Add a research task to the queue."""
        task = ResearchTask(
            topic=topic,
            scope=scope,
            sources=sources or ["web"],
            model=model
        )
        self.tasks.append(task)
    
    def generate_subagent_prompts(self) -> List[dict]:
        """Generate prompts ready for sessions_spawn."""
        prompts = []
        for task in self.tasks:
            prompt = f"""Research Task: {task.topic}
            
Scope: {task.scope}
Sources to check: {', '.join(task.sources)}
Max results: {task.max_results}

Instructions:
1. Search for current, relevant information
2. Extract key facts and insights
3. Note credibility of sources
4. Summarize in 3-5 bullet points
5. Rate your confidence (low/medium/high)

Return your findings in a clear, structured format."""
            
            prompts.append({
                "task": prompt,
                "model": task.model,
                "runTimeoutSeconds": task.timeout_seconds
            })
        return prompts
    
    def create_synthesis_prompt(self, results: List[dict]) -> str:
        """Create prompt for final synthesis (use with Opus)."""
        results_text = json.dumps(results, indent=2)
        return f"""Synthesize these research results into a cohesive report:

Results:
{results_text}

Create a unified analysis that:
1. Identifies common themes
2. Highlights contradictions
3. Notes confidence levels
4. Provides actionable insights
5. Suggests follow-up questions"""
    
    def estimate_cost(self) -> dict:
        """Estimate token cost for all tasks."""
        costs = {
            "haiku": 0.25,   # per 1M tokens
            "sonnet": 3.0,   # per 1M tokens
            "opus": 15.0     # per 1M tokens
        }
        
        estimated_tokens = len(self.tasks) * 3000  # ~3k per task
        total_cost = 0
        
        for task in self.tasks:
            model_cost = costs.get(task.model, costs["sonnet"])
            total_cost += (3000 / 1_000_000) * model_cost
        
        return {
            "estimated_tokens": estimated_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "tasks": len(self.tasks)
        }


# Example usage patterns for Upwork jobs:

def research_competitor_landscape(competitors: List[str]) -> ParallelResearcher:
    """Parallel competitive analysis."""
    researcher = ParallelResearcher()
    for competitor in competitors:
        researcher.add_task(
            topic=f"Analyze {competitor}: products, pricing, reviews, market position",
            scope="broad",
            sources=["web", "social", "news"],
            model="sonnet"
        )
    return researcher


def research_market_trends(industry: str, aspects: List[str]) -> ParallelResearcher:
    """Parallel market research."""
    researcher = ParallelResearcher()
    for aspect in aspects:
        researcher.add_task(
            topic=f"{industry} {aspect} trends 2025-2026",
            scope="deep",
            sources=["web", "academic", "news"],
            model="haiku"  # Use cheaper model for fact-finding
        )
    return researcher


def research_lead_qualification(leads: List[dict]) -> ParallelResearcher:
    """Parallel lead research for sales teams."""
    researcher = ParallelResearcher()
    for lead in leads:
        researcher.add_task(
            topic=f"Research {lead['company']}: size, funding, tech stack, decision makers",
            scope="narrow",
            sources=["web", "social"],
            model="haiku"
        )
    return researcher


if __name__ == "__main__":
    # Demo: Set up a competitor analysis
    competitors = ["Anthropic", "OpenAI", "Google DeepMind"]
    researcher = research_competitor_landscape(competitors)
    
    print("=== Parallel Research Tool ===\n")
    print(f"Tasks queued: {len(researcher.tasks)}")
    print(f"Cost estimate: {researcher.estimate_cost()}")
    print("\nSub-agent prompts ready for sessions_spawn:")
    
    for i, prompt in enumerate(researcher.generate_subagent_prompts()):
        print(f"\n--- Task {i+1} ---")
        print(f"Model: {prompt['model']}")
        print(f"Timeout: {prompt['runTimeoutSeconds']}s")
        print(f"Task preview: {prompt['task'][:200]}...")
