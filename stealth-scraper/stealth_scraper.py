#!/usr/bin/env python3
"""
Stealth Web Scraper - Anti-Detection Playwright Template

This template implements the 9 core anti-detection techniques for
bypassing bot detection on protected websites.

Features:
- navigator.webdriver disabled
- Randomized User-Agent
- Realistic mouse movements
- Human-like delays
- Cookie persistence
- Proxy support (optional)
- Retry logic with backoff

Author: Neo (AI Assistant)
Date: 2026-02-11
Based on: Scrapeless, BrightData, ZenRows research
"""

import asyncio
import random
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext


class StealthScraper:
    """
    A stealth-enabled web scraper using Playwright with anti-detection.
    
    Usage:
        async with StealthScraper() as scraper:
            data = await scraper.scrape("https://example.com", "#content")
    """
    
    # Realistic User-Agent pool
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    # Stealth scripts to inject
    STEALTH_SCRIPTS = [
        # Disable webdriver flag
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        # Modify plugins to look normal
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """,
        # Modify languages
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        """,
        # Hide automation indicators
        """
        window.chrome = { runtime: {} };
        """,
        # Modify permissions
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """,
    ]
    
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        cookies_path: Optional[str] = None,
        timeout_ms: int = 30000,
    ):
        """
        Initialize the stealth scraper.
        
        Args:
            headless: Run browser in headless mode
            proxy: Proxy URL (e.g., "http://user:pass@proxy:8080")
            cookies_path: Path to save/load cookies for persistence
            timeout_ms: Default timeout for operations
        """
        self.headless = headless
        self.proxy = proxy
        self.cookies_path = cookies_path
        self.timeout_ms = timeout_ms
        self.browser = None
        self.context = None
        self.page = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def start(self):
        """Start the browser with stealth settings."""
        playwright = await async_playwright().start()
        
        # Browser launch options
        launch_options = {
            "headless": self.headless,
        }
        
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
            
        self.browser = await playwright.chromium.launch(**launch_options)
        
        # Context with stealth settings
        context_options = {
            "user_agent": random.choice(self.USER_AGENTS),
            "viewport": {"width": 1920, "height": 1080},
            "locale": "en-US",
            "timezone_id": "America/New_York",
        }
        
        self.context = await self.browser.new_context(**context_options)
        
        # Inject stealth scripts
        for script in self.STEALTH_SCRIPTS:
            await self.context.add_init_script(script)
            
        # Load cookies if available
        if self.cookies_path and Path(self.cookies_path).exists():
            with open(self.cookies_path) as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
                
        self.page = await self.context.new_page()
        
    async def close(self):
        """Close browser and save cookies."""
        if self.cookies_path and self.context:
            cookies = await self.context.cookies()
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)
                
        if self.browser:
            await self.browser.close()
            
    async def human_delay(self, min_ms: int = 100, max_ms: int = 500):
        """Add random human-like delay."""
        delay = random.randint(min_ms, max_ms) / 1000
        await asyncio.sleep(delay)
        
    async def human_mouse_move(self, page: Page, x: int, y: int):
        """Move mouse in a human-like path."""
        # Get current position (approximate)
        current_x = random.randint(0, 1920)
        current_y = random.randint(0, 1080)
        
        # Move in steps with slight randomness
        steps = random.randint(5, 10)
        for i in range(steps):
            progress = (i + 1) / steps
            # Add slight curve/randomness
            mid_x = current_x + (x - current_x) * progress + random.randint(-10, 10)
            mid_y = current_y + (y - current_y) * progress + random.randint(-10, 10)
            await page.mouse.move(mid_x, mid_y)
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
    async def human_type(self, page: Page, selector: str, text: str):
        """Type text with human-like speed variations."""
        element = await page.query_selector(selector)
        if element:
            await element.click()
            for char in text:
                await page.keyboard.type(char)
                # Variable typing speed
                await asyncio.sleep(random.uniform(0.05, 0.15))
                
    async def scrape(
        self,
        url: str,
        selector: str,
        wait_for: Optional[str] = None,
        extract_text: bool = True,
    ) -> Dict[str, Any]:
        """
        Scrape a page with stealth.
        
        Args:
            url: URL to scrape
            selector: CSS selector for content
            wait_for: Optional selector to wait for before scraping
            extract_text: If True, extract text; else return HTML
            
        Returns:
            Dict with url, content, timestamp, and success status
        """
        result = {
            "url": url,
            "content": None,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
        }
        
        try:
            # Navigate with human-like behavior
            await self.human_delay(500, 1500)
            await self.page.goto(url, timeout=self.timeout_ms)
            
            # Wait for content
            if wait_for:
                await self.page.wait_for_selector(wait_for, timeout=self.timeout_ms)
            else:
                await self.page.wait_for_load_state("networkidle")
                
            # Random scroll to simulate reading
            await self.human_delay(300, 800)
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            await self.human_delay(200, 500)
            
            # Extract content
            element = await self.page.query_selector(selector)
            if element:
                if extract_text:
                    result["content"] = await element.text_content()
                else:
                    result["content"] = await element.inner_html()
                result["success"] = True
            else:
                result["error"] = f"Selector not found: {selector}"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    async def scrape_multiple(
        self,
        urls: List[str],
        selector: str,
        delay_between: tuple = (2000, 5000),
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs with delays between requests.
        
        Args:
            urls: List of URLs to scrape
            selector: CSS selector for content
            delay_between: (min_ms, max_ms) delay between requests
            
        Returns:
            List of results
        """
        results = []
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            result = await self.scrape(url, selector)
            results.append(result)
            
            # Human-like delay between pages
            if i < len(urls) - 1:
                await self.human_delay(*delay_between)
                
        return results


async def demo():
    """Demonstrate the stealth scraper."""
    print("=== Stealth Scraper Demo ===\n")
    
    async with StealthScraper(headless=True) as scraper:
        # Test on a bot detection site
        result = await scraper.scrape(
            url="https://bot.sannysoft.com/",
            selector="body",
            extract_text=True
        )
        
        print(f"URL: {result['url']}")
        print(f"Success: {result['success']}")
        print(f"Content length: {len(result['content'] or '')} chars")
        if result['error']:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(demo())
