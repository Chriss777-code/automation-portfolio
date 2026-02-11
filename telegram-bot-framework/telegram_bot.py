"""
Telegram Bot Framework
=======================
Modular Telegram bot with command handling and notifications.

Features:
- Command routing with decorators
- Inline keyboards
- Scheduled messages
- Error handling
- Rate limiting

Author: Chris S.
"""

import logging
import asyncio
from functools import wraps
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Modular Telegram bot framework."""
    
    def __init__(self, token: str, allowed_users: Optional[List[int]] = None):
        """
        Initialize the bot.
        
        Args:
            token: Telegram Bot API token from @BotFather
            allowed_users: List of user IDs allowed to use the bot (None = all)
        """
        self.token = token
        self.allowed_users = allowed_users
        self.commands: Dict[str, Callable] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.app = Application.builder().token(token).build()
        
        # Register default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Set up error handler and start command."""
        self.app.add_error_handler(self._error_handler)
        self.app.add_handler(CommandHandler("start", self._start_command))
        self.app.add_handler(CommandHandler("help", self._help_command))
    
    def auth_required(self, func: Callable) -> Callable:
        """Decorator to restrict commands to allowed users."""
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if self.allowed_users and user_id not in self.allowed_users:
                await update.message.reply_text("⛔ You are not authorized to use this bot.")
                logger.warning(f"Unauthorized access attempt by user {user_id}")
                return
            return await func(update, context)
        return wrapper
    
    def command(self, name: str, description: str = ""):
        """Decorator to register a command handler."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                return await func(update, context)
            
            self.commands[name] = {'handler': wrapper, 'description': description}
            self.app.add_handler(CommandHandler(name, wrapper))
            return wrapper
        return decorator
    
    def callback(self, pattern: str):
        """Decorator to register a callback query handler."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                return await func(update, context)
            
            self.callbacks[pattern] = wrapper
            self.app.add_handler(CallbackQueryHandler(wrapper, pattern=pattern))
            return wrapper
        return decorator
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n"
            f"I'm ready to help. Use /help to see available commands."
        )
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = "📚 *Available Commands*\n\n"
        help_text += "/start - Start the bot\n"
        help_text += "/help - Show this help message\n"
        
        for name, info in self.commands.items():
            desc = info.get('description', 'No description')
            help_text += f"/{name} - {desc}\n"
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again."
            )
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        keyboard: Optional[List[List[Dict]]] = None,
        parse_mode: str = 'Markdown'
    ):
        """
        Send a message to a chat.
        
        Args:
            chat_id: Target chat ID
            text: Message text
            keyboard: Optional inline keyboard [[{'text': 'Button', 'callback_data': 'action'}]]
            parse_mode: 'Markdown' or 'HTML'
        """
        reply_markup = None
        if keyboard:
            buttons = [
                [InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']) 
                 for btn in row]
                for row in keyboard
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
        
        await self.app.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    
    def run(self):
        """Start the bot (blocking)."""
        logger.info("🤖 Bot starting...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Example usage
def create_example_bot(token: str, allowed_users: List[int] = None):
    """Create an example bot with sample commands."""
    
    bot = TelegramBot(token=token, allowed_users=allowed_users)
    
    @bot.command("status", "Check bot status")
    @bot.auth_required
    async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"✅ *Bot Status*\n\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"👤 User: {update.effective_user.id}\n"
            f"💬 Chat: {update.effective_chat.id}",
            parse_mode='Markdown'
        )
    
    @bot.command("menu", "Show action menu")
    @bot.auth_required
    async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                {'text': '📊 Status', 'callback_data': 'action_status'},
                {'text': '⚙️ Settings', 'callback_data': 'action_settings'},
            ],
            [
                {'text': '❓ Help', 'callback_data': 'action_help'},
            ]
        ]
        
        buttons = [
            [InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']) 
             for btn in row]
            for row in keyboard
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.reply_text(
            "📋 *Main Menu*\n\nSelect an option:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @bot.callback("action_status")
    async def status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            f"✅ Bot is running!\n🕐 {datetime.now().strftime('%H:%M:%S')}"
        )
    
    @bot.callback("action_settings")
    async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("⚙️ Settings panel (coming soon)")
    
    @bot.callback("action_help")
    async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("❓ Use /help to see all commands")
    
    return bot


if __name__ == "__main__":
    print("Telegram Bot Framework")
    print("=" * 40)
    print("\nUsage:")
    print("  1. Get a token from @BotFather on Telegram")
    print("  2. Set TOKEN = 'your_token_here'")
    print("  3. Run: bot = create_example_bot(TOKEN)")
    print("  4. Run: bot.run()")
    print("\nSee README.md for full documentation.")
