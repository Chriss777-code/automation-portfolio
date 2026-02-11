"""
Playwright Stealth Automation Template
======================================
Production-ready template for browser automation with anti-detection measures.

Features:
- Stealth mode to avoid bot detection
- Session persistence (cookies/localStorage)
- Human-like interaction patterns
- Configurable delays and randomization
- Screenshot and error handling

Author: Chris S.
"""

import asyncio
import random
import json
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser

class StealthAutomation:
    """Base class for stealth browser automation."""
    
    def __init__(self, headless: bool = False, session_file: str = "session.json"):
        self.headless = headless
        self.session_file = Path(session_file)
        self.browser: Browser = None
        self.page: Page = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Initialize browser with stealth settings."""
        self.playwright = await async_playwright().start()
        
        # Stealth browser arguments
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-size=1920,1080',
            '--start-maximized',
        ]
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )
        
        # Load saved session if exists
        await self._load_session()
        
        self.page = await self.context.new_page()
        
        # Inject stealth scripts
        await self._inject_stealth_scripts()
        
        return self
    
    async def _inject_stealth_scripts(self):
        """Inject JavaScript to hide automation indicators."""
        stealth_js = """
        // Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Hide automation-related Chrome properties
        window.chrome = { runtime: {} };
        """
        await self.page.add_init_script(stealth_js)
    
    async def _load_session(self):
        """Load cookies and localStorage from file."""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text())
                if 'cookies' in data:
                    await self.context.add_cookies(data['cookies'])
                print(f"✓ Session loaded from {self.session_file}")
            except Exception as e:
                print(f"⚠ Could not load session: {e}")
    
    async def save_session(self):
        """Save cookies for future sessions."""
        cookies = await self.context.cookies()
        data = {'cookies': cookies}
        self.session_file.write_text(json.dumps(data, indent=2))
        print(f"✓ Session saved to {self.session_file}")
    
    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add random human-like delay."""
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
    
    async def human_type(self, selector: str, text: str, delay_per_char: int = 100):
        """Type text with human-like delays between keystrokes."""
        await self.page.click(selector)
        for char in text:
            await self.page.type(selector, char, delay=random.randint(50, delay_per_char))
            await asyncio.sleep(random.uniform(0.01, 0.05))
    
    async def safe_click(self, selector: str, timeout: int = 10000):
        """Click with error handling and human delay."""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.human_delay(200, 500)
            await self.page.click(selector)
            return True
        except Exception as e:
            print(f"⚠ Click failed on {selector}: {e}")
            return False
    
    async def screenshot(self, name: str = "screenshot"):
        """Take a screenshot for debugging."""
        path = f"{name}.png"
        await self.page.screenshot(path=path, full_page=True)
        print(f"✓ Screenshot saved: {path}")
        return path
    
    async def close(self):
        """Clean up browser resources."""
        if self.browser:
            await self.save_session()
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Example usage
async def main():
    async with StealthAutomation(headless=False) as bot:
        # Navigate to target site
        await bot.page.goto('https://example.com')
        await bot.human_delay()
        
        # Perform actions with human-like behavior
        # await bot.human_type('#search', 'automation')
        # await bot.safe_click('#submit')
        
        # Take screenshot
        await bot.screenshot('example')
        
        print("✓ Automation complete!")


if __name__ == "__main__":
    asyncio.run(main())
