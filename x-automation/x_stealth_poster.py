#!/usr/bin/env python3
"""
X (Twitter) Stealth Automation

Stealth posting and engagement for X/Twitter using DrissionPage.
Designed to avoid bot detection with session persistence.

WARNING: Use responsibly. Respect X's Terms of Service.
This is for educational purposes.

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    HAS_DRISSION = True
except ImportError:
    HAS_DRISSION = False
    print("DrissionPage not installed. Run: pip install DrissionPage")


@dataclass
class Tweet:
    """A tweet to post."""
    text: str
    media_paths: Optional[List[str]] = None
    reply_to: Optional[str] = None  # Tweet URL to reply to
    quote: Optional[str] = None  # Tweet URL to quote


@dataclass
class EngagementAction:
    """An engagement action to perform."""
    action: str  # "like", "retweet", "reply", "follow"
    target: str  # Tweet URL or username
    reply_text: Optional[str] = None


class XStealthClient:
    """
    Stealth X/Twitter automation client.
    
    Usage:
        client = XStealthClient(session_name="my_account")
        
        # First time: Manual login
        await client.manual_login()
        
        # Later: Use saved session
        client.load_session()
        client.post_tweet(Tweet(text="Hello world!"))
    """
    
    SESSION_DIR = Path.home() / ".clawdbot" / "browser-sessions"
    
    def __init__(
        self,
        session_name: str = "x_default",
        headless: bool = False,
        slow_mode: bool = True,
    ):
        """
        Initialize the X client.
        
        Args:
            session_name: Name for session storage
            headless: Run without visible browser (requires saved session)
            slow_mode: Add random delays (recommended for stealth)
        """
        if not HAS_DRISSION:
            raise ImportError("DrissionPage required. Run: pip install DrissionPage")
            
        self.session_name = session_name
        self.headless = headless
        self.slow_mode = slow_mode
        self.page = None
        
        # Ensure session directory exists
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        
    @property
    def cookies_path(self) -> Path:
        return self.SESSION_DIR / f"{self.session_name}_cookies.json"
        
    @property
    def storage_path(self) -> Path:
        return self.SESSION_DIR / f"{self.session_name}_storage.json"
        
    def _get_options(self) -> ChromiumOptions:
        """Get browser options with stealth settings."""
        options = ChromiumOptions()
        
        # Stealth arguments
        options.set_argument('--disable-blink-features=AutomationControlled')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-infobars')
        options.set_argument('--disable-extensions')
        
        # User agent
        options.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        if self.headless:
            options.headless()
            
        return options
        
    def _random_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """Add random delay for human-like behavior."""
        if self.slow_mode:
            time.sleep(random.uniform(min_sec, max_sec))
            
    def start(self):
        """Start the browser."""
        self.page = ChromiumPage(self._get_options())
        
    def close(self):
        """Close the browser."""
        if self.page:
            self.page.quit()
            self.page = None
            
    def manual_login(self, timeout_seconds: int = 120):
        """
        Open X login page for manual login.
        
        After calling, log in manually. Session will be saved.
        """
        if self.headless:
            print("Cannot do manual login in headless mode. Set headless=False.")
            return False
            
        if not self.page:
            self.start()
            
        print("Opening X login page...")
        print("Please log in manually in the browser window.")
        print(f"Waiting up to {timeout_seconds} seconds...")
        
        self.page.get("https://x.com/login")
        
        # Wait for redirect to home (indicates login)
        start = time.time()
        while time.time() - start < timeout_seconds:
            if "home" in self.page.url:
                print("Login detected! Saving session...")
                self.save_session()
                return True
            time.sleep(2)
            
        print("Timeout. Login not detected.")
        return False
        
    def save_session(self):
        """Save cookies and localStorage."""
        if not self.page:
            return False
            
        # Save cookies
        cookies = self.page.cookies()
        self.cookies_path.write_text(json.dumps(cookies, indent=2))
        
        # Save localStorage
        try:
            storage = self.page.run_js("JSON.stringify(localStorage)")
            self.storage_path.write_text(storage)
        except:
            pass
            
        print(f"Session saved to: {self.SESSION_DIR}")
        return True
        
    def load_session(self) -> bool:
        """Load saved session."""
        if not self.page:
            self.start()
            
        # Navigate to X first
        self.page.get("https://x.com")
        self._random_delay(1, 2)
        
        # Load cookies
        if self.cookies_path.exists():
            cookies = json.loads(self.cookies_path.read_text())
            for cookie in cookies:
                try:
                    self.page.set.cookies(cookie)
                except:
                    pass
                    
        # Load localStorage
        if self.storage_path.exists():
            storage = self.storage_path.read_text()
            try:
                self.page.run_js(f"""
                    Object.entries(JSON.parse({repr(storage)})).forEach(
                        ([k,v]) => localStorage.setItem(k,v)
                    )
                """)
            except:
                pass
                
        # Refresh to apply session
        self.page.refresh()
        self._random_delay(2, 4)
        
        return self.is_logged_in()
        
    def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        if not self.page:
            return False
            
        # Check for compose button (indicates logged in)
        try:
            compose = self.page.ele('@data-testid=SideNav_NewTweet_Button', timeout=5)
            return compose is not None
        except:
            return False
            
    def post_tweet(self, tweet: Tweet) -> bool:
        """
        Post a tweet.
        
        Args:
            tweet: Tweet object with text and optional media
            
        Returns:
            True if successful
        """
        if not self.page or not self.is_logged_in():
            print("Not logged in")
            return False
            
        try:
            # Navigate to compose
            self.page.get("https://x.com/compose/post")
            self._random_delay(1, 2)
            
            # Find text input
            text_input = self.page.ele('@data-testid=tweetTextarea_0', timeout=10)
            if not text_input:
                print("Could not find tweet input")
                return False
                
            # Type tweet with human-like speed
            for char in tweet.text:
                text_input.input(char, clear=False)
                if self.slow_mode:
                    time.sleep(random.uniform(0.02, 0.1))
                    
            self._random_delay(0.5, 1.5)
            
            # Click post button
            post_btn = self.page.ele('@data-testid=tweetButton')
            if post_btn:
                post_btn.click()
                self._random_delay(2, 3)
                print(f"Posted: {tweet.text[:50]}...")
                return True
            else:
                print("Could not find post button")
                return False
                
        except Exception as e:
            print(f"Error posting: {e}")
            return False
            
    def like_tweet(self, tweet_url: str) -> bool:
        """Like a tweet."""
        if not self.page or not self.is_logged_in():
            return False
            
        try:
            self.page.get(tweet_url)
            self._random_delay(1, 2)
            
            like_btn = self.page.ele('@data-testid=like', timeout=10)
            if like_btn:
                like_btn.click()
                self._random_delay(0.5, 1.5)
                return True
        except:
            pass
        return False
        
    def reply_to_tweet(self, tweet_url: str, reply_text: str) -> bool:
        """Reply to a tweet."""
        if not self.page or not self.is_logged_in():
            return False
            
        try:
            self.page.get(tweet_url)
            self._random_delay(1, 2)
            
            # Click reply button
            reply_btn = self.page.ele('@data-testid=reply', timeout=10)
            if reply_btn:
                reply_btn.click()
                self._random_delay(0.5, 1)
                
                # Type reply
                text_input = self.page.ele('@data-testid=tweetTextarea_0', timeout=5)
                if text_input:
                    for char in reply_text:
                        text_input.input(char, clear=False)
                        if self.slow_mode:
                            time.sleep(random.uniform(0.02, 0.1))
                            
                    self._random_delay(0.5, 1)
                    
                    # Submit
                    post_btn = self.page.ele('@data-testid=tweetButton')
                    if post_btn:
                        post_btn.click()
                        self._random_delay(1, 2)
                        return True
        except:
            pass
        return False
        
    def follow_user(self, username: str) -> bool:
        """Follow a user."""
        if not self.page or not self.is_logged_in():
            return False
            
        try:
            self.page.get(f"https://x.com/{username}")
            self._random_delay(1, 2)
            
            follow_btn = self.page.ele('@data-testid=follow', timeout=10)
            if follow_btn:
                follow_btn.click()
                self._random_delay(0.5, 1.5)
                return True
        except:
            pass
        return False


def demo():
    """Demo the X stealth client."""
    print("=== X Stealth Automation Demo ===\n")
    
    if not HAS_DRISSION:
        print("Install DrissionPage first: pip install DrissionPage")
        return
        
    print("Usage:\n")
    print("""
    from x_stealth_poster import XStealthClient, Tweet
    
    # Initialize (headed mode for first login)
    client = XStealthClient(session_name="my_account", headless=False)
    client.start()
    
    # First time: Manual login
    client.manual_login()  # Log in manually, session saved
    
    # Later: Use saved session (can be headless)
    client = XStealthClient(session_name="my_account", headless=True)
    client.load_session()
    
    # Post a tweet
    client.post_tweet(Tweet(text="Hello from stealth automation!"))
    
    # Engage with tweets
    client.like_tweet("https://x.com/user/status/123...")
    client.reply_to_tweet("https://x.com/user/status/123...", "Great post!")
    client.follow_user("elonmusk")
    
    client.close()
    """)


if __name__ == "__main__":
    demo()
