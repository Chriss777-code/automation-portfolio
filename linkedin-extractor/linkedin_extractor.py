#!/usr/bin/env python3
"""
LinkedIn Profile Extractor - Stealth data extraction from LinkedIn

This tool extracts structured data from LinkedIn profiles using
stealth techniques to avoid detection.

IMPORTANT: This is for educational purposes. Respect LinkedIn's ToS
and rate limits. Use responsibly.

Features:
- Stealth mode (anti-detection)
- Session persistence (stay logged in)
- Structured data output
- Rate limiting built-in
- Export to JSON/CSV

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import asyncio
import json
import re
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright, Page


@dataclass
class LinkedInProfile:
    """Structured LinkedIn profile data."""
    url: str
    name: str
    headline: str
    location: str
    about: str
    current_company: str
    current_title: str
    connections: str
    experience: List[Dict[str, str]]
    education: List[Dict[str, str]]
    skills: List[str]
    extracted_at: str


class LinkedInExtractor:
    """
    Extract data from LinkedIn profiles with stealth.
    
    Usage:
        async with LinkedInExtractor(session_dir="./linkedin_session") as extractor:
            # First time: Manual login required
            await extractor.login_manual()
            
            # Then extract profiles
            profile = await extractor.extract_profile("https://linkedin.com/in/...")
    """
    
    STEALTH_SCRIPTS = [
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        """
        window.chrome = { runtime: {} };
        """,
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """,
    ]
    
    def __init__(
        self,
        session_dir: str = "./linkedin_session",
        headless: bool = False,
        slow_mode: int = 100,  # ms between actions
    ):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.slow_mode = slow_mode
        self.browser = None
        self.context = None
        self.page = None
        self.cookies_file = self.session_dir / "cookies.json"
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Start browser with stealth settings."""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mode
        )
        
        # Use persistent context for session storage
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        
        # Inject stealth scripts
        for script in self.STEALTH_SCRIPTS:
            await self.context.add_init_script(script)
            
        # Load saved cookies if available
        if self.cookies_file.exists():
            with open(self.cookies_file) as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
                
        self.page = await self.context.new_page()
        
    async def close(self):
        """Save session and close browser."""
        if self.context:
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
                
        if self.browser:
            await self.browser.close()
            
    async def login_manual(self, timeout_seconds: int = 120):
        """
        Navigate to LinkedIn login and wait for manual login.
        
        After calling this, log in manually in the browser window.
        The session will be saved for future runs.
        """
        print("🔐 Opening LinkedIn login page...")
        print("   Please log in manually in the browser window.")
        print(f"   Waiting up to {timeout_seconds} seconds...")
        
        await self.page.goto("https://www.linkedin.com/login")
        
        # Wait for redirect to feed (indicates successful login)
        try:
            await self.page.wait_for_url(
                "**/feed/**",
                timeout=timeout_seconds * 1000
            )
            print("✅ Login successful! Session saved.")
            
            # Save cookies immediately
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
                
            return True
        except:
            print("❌ Login timeout. Try again.")
            return False
            
    async def is_logged_in(self) -> bool:
        """Check if we're currently logged in."""
        await self.page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(2)
        
        # Check for login elements vs feed elements
        url = self.page.url
        return "feed" in url and "login" not in url
        
    async def _human_scroll(self):
        """Scroll like a human to load lazy content."""
        for _ in range(3):
            await self.page.evaluate(
                "window.scrollBy(0, window.innerHeight * 0.7)"
            )
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
        # Scroll back up
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        
    async def extract_profile(self, url: str) -> Optional[LinkedInProfile]:
        """
        Extract data from a LinkedIn profile.
        
        Args:
            url: LinkedIn profile URL (e.g., https://linkedin.com/in/username)
            
        Returns:
            LinkedInProfile with extracted data, or None on failure
        """
        try:
            # Navigate to profile
            await self.page.goto(url, timeout=30000)
            await asyncio.sleep(2)
            
            # Scroll to load all content
            await self._human_scroll()
            
            # Extract basic info
            name = await self._safe_text(".text-heading-xlarge")
            headline = await self._safe_text(".text-body-medium")
            location = await self._safe_text(".text-body-small.inline.t-black--light")
            
            # About section
            about = await self._safe_text("#about ~ div .inline-show-more-text")
            
            # Current position
            current_company = await self._safe_text(
                ".pv-text-details__right-panel .inline-show-more-text"
            )
            current_title = await self._safe_text(
                "#experience ~ div .pvs-entity .t-bold span"
            )
            
            # Connections
            connections = await self._safe_text(".pv-top-card--list-bullet li:first-child")
            
            # Experience (simplified)
            experience = await self._extract_experience()
            
            # Education (simplified)
            education = await self._extract_education()
            
            # Skills
            skills = await self._extract_skills()
            
            return LinkedInProfile(
                url=url,
                name=name or "Unknown",
                headline=headline or "",
                location=location or "",
                about=about or "",
                current_company=current_company or "",
                current_title=current_title or "",
                connections=connections or "",
                experience=experience,
                education=education,
                skills=skills,
                extracted_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Error extracting profile: {e}")
            return None
            
    async def _safe_text(self, selector: str) -> str:
        """Safely extract text from selector."""
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else ""
        except:
            pass
        return ""
        
    async def _extract_experience(self) -> List[Dict[str, str]]:
        """Extract work experience entries."""
        experience = []
        try:
            items = await self.page.query_selector_all(
                "#experience ~ div .pvs-entity"
            )
            for item in items[:5]:  # Limit to 5
                title = await self._element_text(item, ".t-bold span")
                company = await self._element_text(item, ".t-normal span")
                dates = await self._element_text(item, ".pvs-entity__caption-wrapper")
                
                if title or company:
                    experience.append({
                        "title": title,
                        "company": company,
                        "dates": dates
                    })
        except:
            pass
        return experience
        
    async def _extract_education(self) -> List[Dict[str, str]]:
        """Extract education entries."""
        education = []
        try:
            items = await self.page.query_selector_all(
                "#education ~ div .pvs-entity"
            )
            for item in items[:3]:  # Limit to 3
                school = await self._element_text(item, ".t-bold span")
                degree = await self._element_text(item, ".t-normal span")
                dates = await self._element_text(item, ".pvs-entity__caption-wrapper")
                
                if school:
                    education.append({
                        "school": school,
                        "degree": degree,
                        "dates": dates
                    })
        except:
            pass
        return education
        
    async def _extract_skills(self) -> List[str]:
        """Extract skills list."""
        skills = []
        try:
            items = await self.page.query_selector_all(
                "#skills ~ div .pvs-entity .t-bold span"
            )
            for item in items[:10]:  # Limit to 10
                text = await item.text_content()
                if text:
                    skills.append(text.strip())
        except:
            pass
        return skills
        
    async def _element_text(self, parent, selector: str) -> str:
        """Get text from child element."""
        try:
            element = await parent.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else ""
        except:
            pass
        return ""
        
    async def extract_multiple(
        self,
        urls: List[str],
        delay_seconds: tuple = (5, 10)
    ) -> List[LinkedInProfile]:
        """
        Extract multiple profiles with rate limiting.
        
        LinkedIn is strict about automation. Use generous delays.
        Recommended: max 30 profiles per hour.
        """
        profiles = []
        
        for i, url in enumerate(urls):
            print(f"Extracting {i+1}/{len(urls)}: {url}")
            
            profile = await self.extract_profile(url)
            if profile:
                profiles.append(profile)
                
            # Random delay between profiles
            if i < len(urls) - 1:
                delay = random.uniform(*delay_seconds)
                print(f"   Waiting {delay:.1f}s...")
                await asyncio.sleep(delay)
                
        return profiles


def export_to_json(profiles: List[LinkedInProfile], filepath: str):
    """Export profiles to JSON."""
    data = [asdict(p) for p in profiles]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_csv(profiles: List[LinkedInProfile], filepath: str):
    """Export profiles to CSV (flattened)."""
    import csv
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "URL", "Name", "Headline", "Location", "Current Title",
            "Current Company", "Connections", "Skills", "Extracted At"
        ])
        
        for p in profiles:
            writer.writerow([
                p.url,
                p.name,
                p.headline,
                p.location,
                p.current_title,
                p.current_company,
                p.connections,
                ", ".join(p.skills),
                p.extracted_at
            ])


async def demo():
    """Demo the extractor."""
    print("=== LinkedIn Extractor Demo ===\n")
    print("Note: This requires manual login on first run.")
    print("Use headless=False to see the browser.")
    print("\nExample usage:")
    print("""
    async with LinkedInExtractor(headless=False) as extractor:
        # First time only:
        await extractor.login_manual()
        
        # Then extract:
        profile = await extractor.extract_profile(
            "https://www.linkedin.com/in/satyanadella/"
        )
        print(profile.name, "-", profile.headline)
    """)


if __name__ == "__main__":
    asyncio.run(demo())
