"""
Main web service entry point for Render deployment and Telegram integration.
Provides a background keep-alive ping endpoint and an asynchronous Aiogram long-polling loop.
"""

import asyncio
import logging
import os
import subprocess
import threading

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "ACH Automation Bot is Alive and Running!"

@app.route('/ping')
def ping():
    """Endpoint to hit to keep Render awake."""
    return jsonify({"status": "alive", "message": "Hi!"})

@app.route('/run-tests')
def run_tests():
    """Optional endpoint to trigger the bot execution manually over HTTP."""
    def execute_robot():
        # You can pass additional arguments here or pull them from the request args
        subprocess.run(["python", "-m", "robot", "-d", "results", "tests/"])
        
    thread = threading.Thread(target=execute_robot)
    thread.start()
    return jsonify({"status": "started", "message": "Test execution has begun in the background."})

# ==========================================
# Telegram Aiogram Bot Setup
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router(name="start_router")

@router.channel_post(CommandStart())
@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handles the /start command in both direct messages and channels."""
    await message.reply("🤖 ACH Automation Bot is online and ready!")
    sender_id = message.from_user.id if message.from_user else message.chat.id
    logger.info(f"User/Channel {sender_id} initiated /start command.")

async def start_telegram_bot():
    """Initializes and starts the aiogram bot polling."""
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    if not telegram_token:
        logger.warning("TELEGRAM_TOKEN is not set. The bot will not start.")
        return

    bot = Bot(token=telegram_token)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Drop any pending updates from while we were offline, then start polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Starting Telegram Bot Polling (Aiogram event loop active)...")
    # Disable signal handling since this runs in a background thread
    await dp.start_polling(bot, handle_signals=False)

def run_bot_thread():
    """Runs the asyncio event loop natively without colliding with Flask."""
    asyncio.run(start_telegram_bot())

# IMPORTANT: Initialize the thread globally so Gunicorn triggers it when it imports `app.py`.
bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    # Local fallback for `python app.py`
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
