# Telegram Bot Framework

Modular, production-ready Telegram bot framework with command routing and notifications.

## Features

- ✅ Command decorators for clean code
- ✅ Inline keyboard support
- ✅ User authentication/whitelist
- ✅ Callback query handling
- ✅ Error handling built-in

## Installation

```bash
pip install python-telegram-bot
```

## Quick Start

```python
from telegram_bot import TelegramBot
from telegram import Update
from telegram.ext import ContextTypes

# Initialize
bot = TelegramBot(
    token='YOUR_BOT_TOKEN',
    allowed_users=[123456789]  # Optional whitelist
)

# Register command
@bot.command("ping", "Check if bot is alive")
@bot.auth_required
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")

# Handle button callbacks
@bot.callback("action_confirm")
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Confirmed!")

# Run
bot.run()
```

## Sending Messages Programmatically

```python
# Send with inline keyboard
await bot.send_message(
    chat_id=123456789,
    text="Choose an option:",
    keyboard=[
        [{'text': 'Yes', 'callback_data': 'yes'}],
        [{'text': 'No', 'callback_data': 'no'}]
    ]
)
```

## Use Cases

- Notification bots
- Trading alerts
- Task automation
- Status monitoring
- Interactive menus

## License

MIT
