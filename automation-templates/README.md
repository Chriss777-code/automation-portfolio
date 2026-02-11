# Automation Templates

Production-ready Playwright templates with stealth capabilities for browser automation.

## Features

- ✅ Anti-detection / stealth mode
- ✅ Session persistence (cookies saved between runs)
- ✅ Human-like typing and delays
- ✅ Error handling and screenshots
- ✅ Configurable timeouts

## Installation

```bash
pip install playwright
playwright install chromium
```

## Quick Start

```python
from playwright_stealth_template import StealthAutomation
import asyncio

async def main():
    async with StealthAutomation(headless=False) as bot:
        await bot.page.goto('https://example.com')
        await bot.human_type('#search', 'query')
        await bot.safe_click('#submit')
        await bot.screenshot('result')

asyncio.run(main())
```

## Key Methods

| Method | Description |
|--------|-------------|
| `human_delay(min, max)` | Random delay in milliseconds |
| `human_type(selector, text)` | Type with realistic keystroke timing |
| `safe_click(selector)` | Click with error handling |
| `save_session()` | Persist cookies for future runs |
| `screenshot(name)` | Capture full page screenshot |

## Use Cases

- E-commerce price monitoring
- Social media automation
- Data extraction from authenticated sites
- Form submission automation
- Account management workflows

## License

MIT
