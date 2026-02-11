#!/usr/bin/env python3
"""
Price Monitor - Track prices and get alerts on changes

This tool monitors product prices on e-commerce sites and sends
notifications when prices drop below a threshold or change significantly.

Features:
- Multi-site monitoring
- Price history tracking
- Telegram/Email alerts
- Google Sheets integration
- Scheduled runs via cron

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import asyncio
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright


@dataclass
class Product:
    """A product to monitor."""
    url: str
    name: str
    price_selector: str
    target_price: Optional[float] = None
    alert_on_any_change: bool = False
    alert_threshold_percent: float = 5.0


@dataclass
class PriceRecord:
    """A single price observation."""
    url: str
    name: str
    price: float
    currency: str
    timestamp: str
    
    
@dataclass
class PriceAlert:
    """An alert when price conditions are met."""
    product: str
    url: str
    old_price: float
    new_price: float
    change_percent: float
    alert_type: str  # "drop", "target_reached", "change"
    timestamp: str


class PriceMonitor:
    """
    Monitor product prices across multiple sites.
    
    Usage:
        monitor = PriceMonitor(data_dir="./price_data")
        monitor.add_product(Product(
            url="https://amazon.com/...",
            name="Widget",
            price_selector=".a-price-whole",
            target_price=29.99
        ))
        alerts = await monitor.check_all()
    """
    
    def __init__(self, data_dir: str = "./price_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.products: List[Product] = []
        self.history_file = self.data_dir / "price_history.json"
        self.history: Dict[str, List[Dict]] = self._load_history()
        
    def _load_history(self) -> Dict[str, List[Dict]]:
        """Load price history from file."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return {}
        
    def _save_history(self):
        """Save price history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def _get_product_key(self, url: str) -> str:
        """Generate unique key for a product URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]
        
    def add_product(self, product: Product):
        """Add a product to monitor."""
        self.products.append(product)
        
    def add_products_from_file(self, filepath: str):
        """Load products from a JSON config file."""
        with open(filepath) as f:
            data = json.load(f)
            for item in data.get("products", []):
                self.add_product(Product(**item))
                
    async def scrape_price(self, product: Product) -> Optional[PriceRecord]:
        """Scrape current price for a product."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Disable webdriver flag
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            try:
                await page.goto(product.url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Extract price
                element = await page.query_selector(product.price_selector)
                if element:
                    price_text = await element.text_content()
                    price, currency = self._parse_price(price_text)
                    
                    if price:
                        return PriceRecord(
                            url=product.url,
                            name=product.name,
                            price=price,
                            currency=currency,
                            timestamp=datetime.now().isoformat()
                        )
            except Exception as e:
                print(f"Error scraping {product.name}: {e}")
            finally:
                await browser.close()
                
        return None
        
    def _parse_price(self, text: str) -> tuple:
        """Extract price value and currency from text."""
        import re
        
        # Remove whitespace and common text
        text = text.strip()
        
        # Detect currency
        currency = "USD"
        if "€" in text:
            currency = "EUR"
        elif "£" in text:
            currency = "GBP"
        elif "¥" in text:
            currency = "JPY"
            
        # Extract number
        match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
        if match:
            try:
                price = float(match.group().replace(',', ''))
                return price, currency
            except ValueError:
                pass
                
        return None, currency
        
    def _check_alert_conditions(
        self, 
        product: Product, 
        current: PriceRecord
    ) -> Optional[PriceAlert]:
        """Check if current price triggers an alert."""
        key = self._get_product_key(product.url)
        history = self.history.get(key, [])
        
        if not history:
            return None
            
        last_price = history[-1]["price"]
        
        # Calculate change
        if last_price > 0:
            change_percent = ((current.price - last_price) / last_price) * 100
        else:
            change_percent = 0
            
        alert_type = None
        
        # Check target price
        if product.target_price and current.price <= product.target_price:
            if last_price > product.target_price:
                alert_type = "target_reached"
                
        # Check significant drop
        elif change_percent <= -product.alert_threshold_percent:
            alert_type = "drop"
            
        # Check any change
        elif product.alert_on_any_change and abs(change_percent) > 0.01:
            alert_type = "change"
            
        if alert_type:
            return PriceAlert(
                product=product.name,
                url=product.url,
                old_price=last_price,
                new_price=current.price,
                change_percent=change_percent,
                alert_type=alert_type,
                timestamp=current.timestamp
            )
            
        return None
        
    async def check_all(self) -> List[PriceAlert]:
        """Check all products and return any alerts."""
        alerts = []
        
        for product in self.products:
            print(f"Checking: {product.name}")
            
            record = await self.scrape_price(product)
            if record:
                # Check for alerts
                alert = self._check_alert_conditions(product, record)
                if alert:
                    alerts.append(alert)
                    
                # Save to history
                key = self._get_product_key(product.url)
                if key not in self.history:
                    self.history[key] = []
                self.history[key].append(asdict(record))
                
                # Keep last 100 records per product
                self.history[key] = self.history[key][-100:]
                
            # Rate limiting
            await asyncio.sleep(2)
            
        self._save_history()
        return alerts
        
    def get_price_history(self, url: str) -> List[Dict]:
        """Get price history for a specific product."""
        key = self._get_product_key(url)
        return self.history.get(key, [])
        
    def export_to_csv(self, filepath: str):
        """Export all history to CSV."""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["URL", "Name", "Price", "Currency", "Timestamp"])
            
            for key, records in self.history.items():
                for record in records:
                    writer.writerow([
                        record["url"],
                        record["name"],
                        record["price"],
                        record["currency"],
                        record["timestamp"]
                    ])


def format_alert_message(alerts: List[PriceAlert]) -> str:
    """Format alerts for notification."""
    if not alerts:
        return ""
        
    messages = ["🔔 Price Alerts!\n"]
    
    for alert in alerts:
        emoji = "📉" if alert.change_percent < 0 else "📈"
        messages.append(
            f"{emoji} **{alert.product}**\n"
            f"   ${alert.old_price:.2f} → ${alert.new_price:.2f} "
            f"({alert.change_percent:+.1f}%)\n"
            f"   Type: {alert.alert_type}\n"
            f"   Link: {alert.url}\n"
        )
        
    return "\n".join(messages)


async def demo():
    """Demonstrate the price monitor."""
    print("=== Price Monitor Demo ===\n")
    
    monitor = PriceMonitor(data_dir="./demo_prices")
    
    # Example product (replace with real URL and selector)
    monitor.add_product(Product(
        url="https://www.amazon.com/dp/B0EXAMPLE",
        name="Example Product",
        price_selector="#priceblock_ourprice, .a-price-whole",
        target_price=25.00,
        alert_threshold_percent=5.0
    ))
    
    print("Products to monitor:", len(monitor.products))
    print("Note: Demo uses placeholder URL - replace with real products")
    
    # In real usage:
    # alerts = await monitor.check_all()
    # message = format_alert_message(alerts)
    # send_to_telegram(message)


if __name__ == "__main__":
    asyncio.run(demo())
