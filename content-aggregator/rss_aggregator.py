#!/usr/bin/env python3
"""
RSS Content Aggregator

Aggregate content from multiple RSS feeds into a single digest.
Perfect for newsletters, social media content sourcing, and research.

Features:
- Multiple feed support
- Category filtering
- Keyword search
- Deduplication
- Export to multiple formats

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from urllib.request import urlopen, Request
from xml.etree import ElementTree as ET
from html import unescape


@dataclass
class FeedItem:
    """A single feed item/article."""
    title: str
    link: str
    description: str
    published: Optional[str]
    source: str
    category: Optional[str] = None
    author: Optional[str] = None
    content_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.md5(self.link.encode()).hexdigest()[:12]


@dataclass
class Feed:
    """RSS feed configuration."""
    name: str
    url: str
    category: Optional[str] = None
    enabled: bool = True


class RSSAggregator:
    """
    Aggregate content from multiple RSS feeds.
    
    Usage:
        agg = RSSAggregator()
        agg.add_feed(Feed(name="TechCrunch", url="https://techcrunch.com/feed/"))
        agg.add_feed(Feed(name="Hacker News", url="https://hnrss.org/frontpage"))
        
        items = agg.fetch_all()
        digest = agg.create_digest(items, max_items=10)
    """
    
    USER_AGENT = "Mozilla/5.0 (compatible; ContentAggregator/1.0)"
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.feeds: List[Feed] = []
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.seen_hashes: set = set()
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_seen_hashes()
            
    def _load_seen_hashes(self):
        """Load previously seen content hashes."""
        seen_file = self.cache_dir / "seen_hashes.json"
        if seen_file.exists():
            self.seen_hashes = set(json.loads(seen_file.read_text()))
            
    def _save_seen_hashes(self):
        """Save seen content hashes."""
        if self.cache_dir:
            seen_file = self.cache_dir / "seen_hashes.json"
            seen_file.write_text(json.dumps(list(self.seen_hashes)))
            
    def add_feed(self, feed: Feed):
        """Add a feed to aggregate."""
        self.feeds.append(feed)
        
    def add_feeds_from_file(self, filepath: str):
        """Load feeds from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
            for f_data in data.get("feeds", []):
                self.add_feed(Feed(**f_data))
                
    def fetch_feed(self, feed: Feed) -> List[FeedItem]:
        """Fetch items from a single feed."""
        items = []
        
        try:
            req = Request(feed.url, headers={"User-Agent": self.USER_AGENT})
            with urlopen(req, timeout=30) as response:
                content = response.read()
                
            root = ET.fromstring(content)
            
            # Handle RSS 2.0 and Atom
            namespaces = {
                "atom": "http://www.w3.org/2005/Atom",
                "content": "http://purl.org/rss/1.0/modules/content/"
            }
            
            # Try RSS 2.0 format
            for item in root.findall(".//item"):
                items.append(self._parse_rss_item(item, feed))
                
            # Try Atom format
            for entry in root.findall(".//atom:entry", namespaces):
                items.append(self._parse_atom_entry(entry, feed, namespaces))
                
        except Exception as e:
            print(f"Error fetching {feed.name}: {e}")
            
        return items
        
    def _parse_rss_item(self, item: ET.Element, feed: Feed) -> FeedItem:
        """Parse RSS 2.0 item."""
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        description = item.findtext("description", "")
        pub_date = item.findtext("pubDate")
        author = item.findtext("author") or item.findtext("{http://purl.org/dc/elements/1.1/}creator")
        
        # Clean HTML from description
        description = self._strip_html(description)
        
        return FeedItem(
            title=unescape(title.strip()),
            link=link.strip(),
            description=description[:500],
            published=pub_date,
            source=feed.name,
            category=feed.category,
            author=author
        )
        
    def _parse_atom_entry(self, entry: ET.Element, feed: Feed, ns: dict) -> FeedItem:
        """Parse Atom entry."""
        title = entry.findtext("atom:title", "", ns)
        link_elem = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns)
        link = link_elem.get("href", "") if link_elem is not None else ""
        
        summary = entry.findtext("atom:summary", "", ns)
        content = entry.findtext("atom:content", "", ns)
        description = summary or content
        description = self._strip_html(description)
        
        published = entry.findtext("atom:published", "", ns) or entry.findtext("atom:updated", "", ns)
        author_elem = entry.find("atom:author/atom:name", ns)
        author = author_elem.text if author_elem is not None else None
        
        return FeedItem(
            title=unescape(title.strip()),
            link=link.strip(),
            description=description[:500],
            published=published,
            source=feed.name,
            category=feed.category,
            author=author
        )
        
    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = ' '.join(text.split())
        return text.strip()
        
    def fetch_all(self, only_new: bool = False) -> List[FeedItem]:
        """
        Fetch items from all enabled feeds.
        
        Args:
            only_new: Only return items not seen before
            
        Returns:
            List of FeedItems sorted by recency
        """
        all_items = []
        
        for feed in self.feeds:
            if not feed.enabled:
                continue
                
            print(f"Fetching: {feed.name}")
            items = self.fetch_feed(feed)
            all_items.extend(items)
            
        # Deduplicate by content hash
        seen = set()
        unique_items = []
        for item in all_items:
            if item.content_hash not in seen:
                seen.add(item.content_hash)
                unique_items.append(item)
                
        # Filter to only new if requested
        if only_new:
            new_items = [i for i in unique_items if i.content_hash not in self.seen_hashes]
            # Update seen hashes
            for item in new_items:
                self.seen_hashes.add(item.content_hash)
            self._save_seen_hashes()
            return new_items
            
        return unique_items
        
    def search(self, items: List[FeedItem], keywords: List[str]) -> List[FeedItem]:
        """Filter items by keywords."""
        results = []
        for item in items:
            text = f"{item.title} {item.description}".lower()
            if any(kw.lower() in text for kw in keywords):
                results.append(item)
        return results
        
    def filter_by_category(self, items: List[FeedItem], category: str) -> List[FeedItem]:
        """Filter items by category."""
        return [i for i in items if i.category == category]
        
    def create_digest(
        self,
        items: List[FeedItem],
        max_items: int = 10,
        format: str = "markdown"
    ) -> str:
        """
        Create a digest from items.
        
        Args:
            items: Items to include
            max_items: Maximum items in digest
            format: "markdown", "html", or "text"
            
        Returns:
            Formatted digest string
        """
        items = items[:max_items]
        
        if format == "markdown":
            return self._digest_markdown(items)
        elif format == "html":
            return self._digest_html(items)
        else:
            return self._digest_text(items)
            
    def _digest_markdown(self, items: List[FeedItem]) -> str:
        """Create markdown digest."""
        lines = [f"# Content Digest - {datetime.now().strftime('%Y-%m-%d')}\n"]
        
        for i, item in enumerate(items, 1):
            lines.append(f"## {i}. {item.title}")
            lines.append(f"*Source: {item.source}*")
            if item.author:
                lines.append(f"*Author: {item.author}*")
            lines.append(f"\n{item.description}\n")
            lines.append(f"[Read more]({item.link})\n")
            lines.append("---\n")
            
        return "\n".join(lines)
        
    def _digest_html(self, items: List[FeedItem]) -> str:
        """Create HTML digest."""
        html = [f"<h1>Content Digest - {datetime.now().strftime('%Y-%m-%d')}</h1>"]
        
        for i, item in enumerate(items, 1):
            html.append(f"<h2>{i}. {item.title}</h2>")
            html.append(f"<p><em>Source: {item.source}</em></p>")
            html.append(f"<p>{item.description}</p>")
            html.append(f"<p><a href='{item.link}'>Read more</a></p>")
            html.append("<hr>")
            
        return "\n".join(html)
        
    def _digest_text(self, items: List[FeedItem]) -> str:
        """Create plain text digest."""
        lines = [f"CONTENT DIGEST - {datetime.now().strftime('%Y-%m-%d')}\n"]
        lines.append("=" * 50 + "\n")
        
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item.title}")
            lines.append(f"   Source: {item.source}")
            lines.append(f"   {item.description[:200]}...")
            lines.append(f"   Link: {item.link}")
            lines.append("")
            
        return "\n".join(lines)
        
    def export_items(self, items: List[FeedItem], filepath: str):
        """Export items to JSON."""
        data = [asdict(i) for i in items]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Preset feed collections
TECH_FEEDS = [
    Feed(name="TechCrunch", url="https://techcrunch.com/feed/", category="tech"),
    Feed(name="Hacker News", url="https://hnrss.org/frontpage", category="tech"),
    Feed(name="The Verge", url="https://www.theverge.com/rss/index.xml", category="tech"),
    Feed(name="Ars Technica", url="https://feeds.arstechnica.com/arstechnica/technology-lab", category="tech"),
]

FINANCE_FEEDS = [
    Feed(name="Bloomberg Markets", url="https://www.bloomberg.com/feed/podcast/bloomberg-surveillance.xml", category="finance"),
    Feed(name="CNBC", url="https://www.cnbc.com/id/100727362/device/rss/rss.html", category="finance"),
]

AI_FEEDS = [
    Feed(name="OpenAI Blog", url="https://openai.com/blog/rss.xml", category="ai"),
    Feed(name="AI News", url="https://www.artificialintelligence-news.com/feed/", category="ai"),
]


def demo():
    """Demo the RSS aggregator."""
    print("=== RSS Content Aggregator Demo ===\n")
    
    # Create aggregator with tech feeds
    agg = RSSAggregator()
    for feed in TECH_FEEDS[:2]:  # Just first 2 for demo
        agg.add_feed(feed)
        
    # Fetch all items
    print("Fetching feeds...\n")
    items = agg.fetch_all()
    print(f"\nFound {len(items)} items\n")
    
    # Create digest
    if items:
        digest = agg.create_digest(items, max_items=5, format="text")
        print(digest)


if __name__ == "__main__":
    demo()
