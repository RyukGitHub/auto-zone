import os
import logging
from aiogram import Bot, Dispatcher

# Import the modular routers
from bot.modules import start, send, purge, logger_module

logger = logging.getLogger(__name__)

async def start_telegram_bot():
    """Initializes and starts the aiogram bot polling with all attached modules."""
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    if not telegram_token:
        logger.warning("TELEGRAM_TOKEN is not set. The bot will not start.")
        return

    bot = Bot(token=telegram_token)
    dp = Dispatcher()
    
    # 1. Register explicit commands first
    dp.include_router(start.router)
    dp.include_router(send.router)
    dp.include_router(purge.router)
    
    # 2. Register wildcard and diagnostic loggers last to avoid swallowing commands
    dp.include_router(logger_module.router)
    
    # Drop any pending updates from while we were offline, then start polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Starting Telegram Bot Polling (Modular Aiogram Event Loop Active)...")
    
    # Disable signal handling since this runs in a background thread inside Flask
    await dp.start_polling(bot, handle_signals=False)
