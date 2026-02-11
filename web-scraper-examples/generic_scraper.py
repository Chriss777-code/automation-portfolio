"""
Generic Web Scraper
====================
Flexible web scraping template with multiple backend support.

Features:
- Requests + BeautifulSoup for static sites
- Playwright for JavaScript-heavy sites
- Built-in rate limiting
- CSV/JSON export
- Proxy support

Author: Chris S.
"""

import csv
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapedItem:
    """Generic data container for scraped items."""
    title: str
    url: str
    price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    extra_data: Optional[dict] = None


class WebScraper:
    """Configurable web scraper with rate limiting and export options."""
    
    def __init__(
        self,
        base_url: str,
        rate_limit: float = 1.0,  # seconds between requests
        proxy: Optional[str] = None,
        headers: Optional[dict] = None
    ):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.proxy = proxy
        self.session = requests.Session()
        
        # Default headers to look like a browser
        self.session.headers.update(headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        
        self.items: List[ScrapedItem] = []
        self._last_request = 0
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed + random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
        self._last_request = time.time()
    
    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a URL and return parsed BeautifulSoup object."""
        self._rate_limit_wait()
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"⚠ Error fetching {url}: {e}")
            return None
    
    def parse_listing_page(self, soup: BeautifulSoup) -> List[ScrapedItem]:
        """
        Override this method to parse your specific site.
        
        Example implementation:
        ```
        items = []
        for card in soup.select('.product-card'):
            item = ScrapedItem(
                title=card.select_one('.title').text.strip(),
                url=card.select_one('a')['href'],
                price=card.select_one('.price').text.strip(),
            )
            items.append(item)
        return items
        ```
        """
        raise NotImplementedError("Override parse_listing_page() for your site")
    
    def scrape_listings(self, start_url: str, max_pages: int = 10) -> List[ScrapedItem]:
        """Scrape multiple pages of listings."""
        current_url = start_url
        page = 1
        
        while current_url and page <= max_pages:
            print(f"📄 Scraping page {page}: {current_url}")
            
            soup = self.fetch(current_url)
            if not soup:
                break
            
            # Parse items from current page
            page_items = self.parse_listing_page(soup)
            self.items.extend(page_items)
            print(f"   Found {len(page_items)} items")
            
            # Find next page link (customize selector for your site)
            next_link = soup.select_one('a.next-page, a[rel="next"], .pagination a:last-child')
            current_url = next_link['href'] if next_link else None
            
            page += 1
        
        print(f"\n✓ Total items scraped: {len(self.items)}")
        return self.items
    
    def export_csv(self, filename: str = "scraped_data.csv"):
        """Export scraped items to CSV."""
        if not self.items:
            print("⚠ No items to export")
            return
        
        path = Path(filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'url', 'price', 'description', 'image_url'])
            writer.writeheader()
            for item in self.items:
                writer.writerow({k: v for k, v in asdict(item).items() if k != 'extra_data'})
        
        print(f"✓ Exported {len(self.items)} items to {path}")
    
    def export_json(self, filename: str = "scraped_data.json"):
        """Export scraped items to JSON."""
        if not self.items:
            print("⚠ No items to export")
            return
        
        path = Path(filename)
        data = [asdict(item) for item in self.items]
        path.write_text(json.dumps(data, indent=2))
        
        print(f"✓ Exported {len(self.items)} items to {path}")


# Example: E-commerce scraper implementation
class EcommerceScraper(WebScraper):
    """Example implementation for a generic e-commerce site."""
    
    def parse_listing_page(self, soup: BeautifulSoup) -> List[ScrapedItem]:
        items = []
        
        # Customize these selectors for your target site
        for card in soup.select('.product-card, .product-item, [data-product]'):
            try:
                title_el = card.select_one('.product-title, .item-title, h2, h3')
                price_el = card.select_one('.price, .product-price, [data-price]')
                link_el = card.select_one('a[href]')
                img_el = card.select_one('img')
                
                item = ScrapedItem(
                    title=title_el.text.strip() if title_el else "Unknown",
                    url=link_el['href'] if link_el else "",
                    price=price_el.text.strip() if price_el else None,
                    image_url=img_el.get('src') or img_el.get('data-src') if img_el else None,
                )
                items.append(item)
            except Exception as e:
                print(f"⚠ Error parsing card: {e}")
                continue
        
        return items


# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = EcommerceScraper(
        base_url="https://example-shop.com",
        rate_limit=2.0  # 2 seconds between requests
    )
    
    # Scrape listings
    # items = scraper.scrape_listings("https://example-shop.com/products", max_pages=5)
    
    # Export results
    # scraper.export_csv("products.csv")
    # scraper.export_json("products.json")
    
    print("Scraper ready! Customize parse_listing_page() for your target site.")
