#!/usr/bin/env python3
"""
Parallel Stealth Research Tool v2

Combines the power of:
1. Sub-agents for parallel research
2. Stealth browser for protected site access
3. Content aggregation for unified output

This is the ultimate research automation tool.

Author: Neo (AI Assistant)
Date: 2026-02-11
Built during overnight 80% capability sprint
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

# Stealth browser (if available)
try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False


@dataclass
class ResearchTarget:
    """A target to research."""
    name: str
    query: str  # For sub-agent web search
    url: Optional[str] = None  # For stealth scraping
    scrape_selector: Optional[str] = None


@dataclass
class ResearchResult:
    """Result from research."""
    target_name: str
    source: str  # "subagent" or "stealth_scrape"
    content: str
    metadata: Dict[str, Any]
    timestamp: str


class ParallelStealthResearcher:
    """
    Research multiple targets in parallel using sub-agents,
    then optionally scrape detailed data with stealth browser.
    
    This combines:
    - OpenClaw sub-agents for parallel web research
    - DrissionPage for stealth scraping of protected sites
    - Content aggregation for unified reports
    
    Usage (in OpenClaw context):
        researcher = ParallelStealthResearcher()
        
        # Define targets
        targets = [
            ResearchTarget(name="Competitor A", query="Competitor A pricing features"),
            ResearchTarget(name="Competitor B", query="Competitor B pricing features"),
        ]
        
        # Research (sub-agents run in parallel)
        # In real usage, this would call sessions_spawn for each target
        results = researcher.research_parallel(targets)
        
        # Optional: Deep scrape specific URLs with stealth
        if HAS_STEALTH:
            for target in targets:
                if target.url:
                    scrape_result = researcher.stealth_scrape(target)
                    results.append(scrape_result)
        
        # Generate report
        report = researcher.generate_report(results)
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("./research_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ResearchResult] = []
        
    def generate_subagent_tasks(self, targets: List[ResearchTarget]) -> List[Dict]:
        """
        Generate task definitions for sub-agents.
        
        Returns list of dicts ready for sessions_spawn.
        """
        tasks = []
        for target in targets:
            task = {
                "task": f"""Research: {target.name}

Search query: "{target.query}"

Instructions:
1. Search for current, relevant information
2. Extract key facts, features, pricing if available
3. Note credibility of sources
4. Summarize in 3-5 bullet points
5. Include source URLs

Return findings in a structured format.""",
                "model": "sonnet",  # Cost-effective for research
                "runTimeoutSeconds": 120
            }
            tasks.append(task)
        return tasks
        
    def stealth_scrape(self, target: ResearchTarget) -> Optional[ResearchResult]:
        """
        Scrape a URL using stealth browser.
        
        Requires DrissionPage installed.
        """
        if not HAS_STEALTH:
            print("DrissionPage not installed - skipping stealth scrape")
            return None
            
        if not target.url:
            return None
            
        try:
            options = ChromiumOptions()
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-dev-shm-usage')
            options.headless()
            
            page = ChromiumPage(options)
            page.get(target.url)
            page.wait.doc_loaded()
            
            # Extract content
            if target.scrape_selector:
                element = page.ele(target.scrape_selector, timeout=10)
                content = element.text if element else ""
            else:
                content = page.html[:5000]  # First 5000 chars
                
            page.quit()
            
            return ResearchResult(
                target_name=target.name,
                source="stealth_scrape",
                content=content,
                metadata={"url": target.url, "selector": target.scrape_selector},
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Stealth scrape failed for {target.name}: {e}")
            return None
            
    def add_result(self, result: ResearchResult):
        """Add a research result."""
        self.results.append(result)
        
    def generate_report(
        self,
        results: Optional[List[ResearchResult]] = None,
        format: str = "markdown"
    ) -> str:
        """
        Generate a unified research report.
        
        Args:
            results: Results to include (uses self.results if None)
            format: "markdown", "html", or "json"
        """
        results = results or self.results
        
        if format == "json":
            return json.dumps([asdict(r) for r in results], indent=2)
            
        # Markdown report
        lines = [
            f"# Research Report",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*Targets: {len(results)}*",
            "",
            "---",
            ""
        ]
        
        for result in results:
            lines.append(f"## {result.target_name}")
            lines.append(f"*Source: {result.source}*")
            lines.append("")
            lines.append(result.content)
            lines.append("")
            lines.append("---")
            lines.append("")
            
        return "\n".join(lines)
        
    def save_report(self, filename: str, format: str = "markdown"):
        """Save report to file."""
        report = self.generate_report(format=format)
        ext = {"markdown": ".md", "html": ".html", "json": ".json"}.get(format, ".txt")
        filepath = self.output_dir / f"{filename}{ext}"
        filepath.write_text(report)
        return filepath


# Example workflow for competitive analysis
def competitive_analysis_workflow():
    """
    Example: Research 5 competitors in parallel.
    
    This shows how to structure the workflow in OpenClaw.
    """
    targets = [
        ResearchTarget(
            name="Anthropic",
            query="Anthropic Claude pricing features capabilities 2025"
        ),
        ResearchTarget(
            name="OpenAI",
            query="OpenAI GPT-4 API pricing features 2025"
        ),
        ResearchTarget(
            name="Google",
            query="Google Gemini API pricing features 2025"
        ),
        ResearchTarget(
            name="Mistral",
            query="Mistral AI API pricing features 2025"
        ),
        ResearchTarget(
            name="Cohere",
            query="Cohere API pricing features 2025"
        ),
    ]
    
    researcher = ParallelStealthResearcher()
    tasks = researcher.generate_subagent_tasks(targets)
    
    print("=== Competitive Analysis Workflow ===\n")
    print(f"Targets: {len(targets)}")
    print("\nSub-agent tasks to spawn:")
    for i, task in enumerate(tasks, 1):
        print(f"\n--- Task {i} ---")
        print(f"Model: {task['model']}")
        print(f"Timeout: {task['runTimeoutSeconds']}s")
        print(f"Task preview: {task['task'][:100]}...")
    
    print("\n\nIn OpenClaw, spawn these with:")
    print("sessions_spawn(task=..., model='sonnet', runTimeoutSeconds=120)")
    print("\nAll 5 run in parallel, results stream back as they complete.")


if __name__ == "__main__":
    competitive_analysis_workflow()
