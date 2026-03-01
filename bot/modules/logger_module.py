import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="logger")

@router.channel_post(F.text.startswith('/'))
@router.message(F.text.startswith('/'))
async def fallback_delete_commands(message: Message):
    """Deletes any unhandled commands in public channels to keep the feed clean."""
    if message.chat.type in ["group", "supergroup", "channel"]:
        try:
            await message.delete()
            logger.info(f"Deleted unhandled command '{message.text}' from {message.chat.type}.")
        except TelegramBadRequest as e:
            logger.warning(f"Failed to delete unhandled command. Error: {e}")

@router.channel_post()
@router.message()
async def diagnostic_logger(message: Message):
    """Invisibly logs all raw messages to diagnose if Group/Channel routing restricts bot visibility."""
    chat_title = message.chat.title or message.chat.id
    text = message.text or "<No Text/Media>"
    logger.info(f"[DIAGNOSTIC] Event received in {message.chat.type} '{chat_title}': {text}")
