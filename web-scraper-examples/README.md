# Web Scraper Examples

Flexible, production-ready web scraping templates.

## Features

- ✅ Requests + BeautifulSoup for static sites
- ✅ Built-in rate limiting (be a good citizen)
- ✅ Proxy support
- ✅ CSV and JSON export
- ✅ Easy to customize for any site

## Installation

```bash
pip install requests beautifulsoup4
```

## Quick Start

```python
from generic_scraper import WebScraper, ScrapedItem

class MyScraper(WebScraper):
    def parse_listing_page(self, soup):
        items = []
        for card in soup.select('.product'):
            items.append(ScrapedItem(
                title=card.select_one('h2').text,
                url=card.select_one('a')['href'],
                price=card.select_one('.price').text
            ))
        return items

scraper = MyScraper(base_url="https://example.com", rate_limit=2.0)
scraper.scrape_listings("/products", max_pages=5)
scraper.export_csv("output.csv")
```

## Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `rate_limit` | Seconds between requests | 1.0 |
| `proxy` | Proxy URL (http://...) | None |
| `headers` | Custom request headers | Browser-like |

## Use Cases

- Price monitoring
- Lead generation
- Content aggregation
- Market research
- Competitor analysis

## License

MIT
