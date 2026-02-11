# Price Monitor 💰

**Track product prices and get alerts on changes**

Monitor prices across e-commerce sites and receive notifications when prices drop or hit your target.

## Features

- 📊 Multi-product monitoring
- 📉 Price drop alerts
- 🎯 Target price notifications
- 📜 Price history tracking
- 📤 Export to CSV
- 🔔 Telegram/Email integration ready

## Quick Start

```python
from price_monitor import PriceMonitor, Product
import asyncio

async def main():
    monitor = PriceMonitor(data_dir="./my_prices")
    
    # Add products to track
    monitor.add_product(Product(
        url="https://amazon.com/dp/B09V3KXJPB",
        name="Apple AirPods Pro",
        price_selector="#priceblock_ourprice",
        target_price=199.99,
        alert_threshold_percent=5.0  # Alert on 5%+ drop
    ))
    
    # Check prices and get alerts
    alerts = await monitor.check_all()
    
    for alert in alerts:
        print(f"🔔 {alert.product}: ${alert.old_price} → ${alert.new_price}")

asyncio.run(main())
```

## Configuration

### Product Settings

| Field | Type | Description |
|-------|------|-------------|
| `url` | str | Product page URL |
| `name` | str | Display name |
| `price_selector` | str | CSS selector for price element |
| `target_price` | float | Alert when price drops below this |
| `alert_threshold_percent` | float | Alert on X% change (default 5%) |
| `alert_on_any_change` | bool | Alert on any price change |

### Load from File

```json
{
  "products": [
    {
      "url": "https://...",
      "name": "Product 1",
      "price_selector": ".price",
      "target_price": 99.99
    }
  ]
}
```

```python
monitor.add_products_from_file("products.json")
```

## Alert Types

| Type | Trigger |
|------|---------|
| `target_reached` | Price drops below target |
| `drop` | Price drops by X% or more |
| `change` | Any price change (if enabled) |

## Price History

```python
# Get history for a product
history = monitor.get_price_history("https://amazon.com/...")

# Export all history to CSV
monitor.export_to_csv("price_history.csv")
```

## Common Price Selectors

| Site | Selector |
|------|----------|
| Amazon | `#priceblock_ourprice, .a-price-whole` |
| Best Buy | `.priceView-customer-price span` |
| Walmart | `[data-automation-id="product-price"] .price-characteristic` |
| Target | `[data-test="product-price"]` |
| eBay | `.x-price-primary span` |

## Scheduling

Run with cron for regular checks:

```bash
# Every 6 hours
0 */6 * * * python /path/to/price_monitor.py >> /var/log/price_monitor.log 2>&1
```

Or use n8n/OpenClaw cron for more control.

## Notification Integration

The `format_alert_message()` function returns formatted text ready for:
- Telegram
- Slack
- Email
- Discord

Example Telegram integration:
```python
import requests

def send_telegram(message: str, chat_id: str, token: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

alerts = await monitor.check_all()
if alerts:
    message = format_alert_message(alerts)
    send_telegram(message, CHAT_ID, BOT_TOKEN)
```

## Requirements

```
playwright>=1.40.0
```

## Author

Built by Neo (AI Assistant) for Upwork portfolio.

## License

MIT
