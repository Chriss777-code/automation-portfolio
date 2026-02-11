# RSS Content Aggregator 📰

**Aggregate content from multiple RSS feeds into digestible formats**

Perfect for newsletters, social media content sourcing, and research.

## Features

- 📚 Multi-feed support (RSS 2.0 + Atom)
- 🏷️ Category filtering
- 🔍 Keyword search
- 🔄 Deduplication
- 🆕 New content detection
- 📤 Multiple export formats

## Quick Start

```python
from rss_aggregator import RSSAggregator, Feed

# Create aggregator
agg = RSSAggregator()

# Add feeds
agg.add_feed(Feed(name="TechCrunch", url="https://techcrunch.com/feed/"))
agg.add_feed(Feed(name="Hacker News", url="https://hnrss.org/frontpage"))

# Fetch all items
items = agg.fetch_all()

# Create digest
digest = agg.create_digest(items, max_items=10, format="markdown")
print(digest)
```

## Feed Configuration

```python
Feed(
    name="TechCrunch",           # Display name
    url="https://..../feed/",   # RSS/Atom URL
    category="tech",            # Optional category
    enabled=True                # Enable/disable
)
```

## Load Feeds from JSON

```json
{
  "feeds": [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "tech"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "category": "tech"}
  ]
}
```

```python
agg.add_feeds_from_file("feeds.json")
```

## Only New Content

```python
# Enable caching
agg = RSSAggregator(cache_dir="./cache")

# Fetch only new items (not seen before)
new_items = agg.fetch_all(only_new=True)
```

## Search & Filter

```python
# Search by keywords
results = agg.search(items, ["AI", "automation", "scraping"])

# Filter by category
tech_items = agg.filter_by_category(items, "tech")
```

## Digest Formats

```python
# Markdown (default)
digest = agg.create_digest(items, format="markdown")

# HTML (for emails)
digest = agg.create_digest(items, format="html")

# Plain text
digest = agg.create_digest(items, format="text")
```

## Export to JSON

```python
agg.export_items(items, "content.json")
```

## Preset Feed Collections

```python
from rss_aggregator import TECH_FEEDS, FINANCE_FEEDS, AI_FEEDS

for feed in TECH_FEEDS:
    agg.add_feed(feed)
```

**Included presets:**
- `TECH_FEEDS`: TechCrunch, Hacker News, The Verge, Ars Technica
- `FINANCE_FEEDS`: Bloomberg, CNBC
- `AI_FEEDS`: OpenAI Blog, AI News

## Use Cases

1. **Daily Newsletter** - Aggregate + digest → email
2. **Social Media Sourcing** - Find trending content to share
3. **Competitive Intelligence** - Monitor industry news
4. **Research** - Collect articles on specific topics
5. **Content Curation** - Build curated feed for clients

## Requirements

```
# No external dependencies - uses Python stdlib
```

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT
