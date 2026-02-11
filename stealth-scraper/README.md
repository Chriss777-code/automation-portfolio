# Stealth Web Scraper 🥷

**Anti-detection Playwright template for protected websites**

This template implements the 9 core anti-detection techniques documented in the latest 2025 research from Scrapeless, BrightData, and ZenRows.

## Features

- ✅ `navigator.webdriver` disabled
- ✅ Randomized User-Agent pool
- ✅ Realistic mouse movements (bezier-like paths)
- ✅ Human-like typing with speed variations
- ✅ Random delays between actions
- ✅ Cookie persistence across sessions
- ✅ Proxy support
- ✅ Chrome/plugins fingerprint modifications
- ✅ Retry logic with exponential backoff

## Quick Start

```python
from stealth_scraper import StealthScraper
import asyncio

async def main():
    async with StealthScraper(headless=True) as scraper:
        result = await scraper.scrape(
            url="https://example.com",
            selector="#content"
        )
        print(result["content"])

asyncio.run(main())
```

## Anti-Detection Techniques

### 1. WebDriver Flag
```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
```

### 2. User-Agent Rotation
Pool of 5 common 2024 User-Agents (Chrome, Firefox, Safari, Edge).

### 3. Human-Like Behavior
- Mouse movements follow curved paths
- Typing speed varies per character
- Random delays between all actions
- Scrolling to simulate reading

### 4. Cookie Persistence
Save/load cookies to maintain sessions across runs.

### 5. Fingerprint Modifications
- Plugins array populated
- Languages set to realistic values
- Chrome runtime object present
- Permissions API modified

## Configuration

```python
scraper = StealthScraper(
    headless=True,           # False for debugging
    proxy="http://...",      # Optional proxy
    cookies_path="./cookies.json",  # Persistence
    timeout_ms=30000         # Request timeout
)
```

## Multiple URLs

```python
urls = ["https://site.com/page1", "https://site.com/page2"]
results = await scraper.scrape_multiple(
    urls=urls,
    selector=".content",
    delay_between=(2000, 5000)  # 2-5 sec between requests
)
```

## Requirements

```
playwright>=1.40.0
```

Install Playwright browsers:
```bash
playwright install chromium
```

## When to Use This

- Sites that block basic scrapers
- E-commerce price monitoring
- Data extraction from protected pages
- Any site with Cloudflare, PerimeterX, etc.

## When NOT to Use This

- Sites with explicit API access (use their API instead)
- High-volume scraping (use proxy services)
- Sites that allow robots.txt scraping

## Limitations

- Not 100% undetectable (nothing is)
- Some advanced anti-bot systems may still detect
- For enterprise needs, consider Browserless/Scrapeless

## Author

Built by Neo (AI Assistant) during overnight skill building.

## License

MIT
