import json
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router(name="registry")

DB_FILE = "registered_chats.json"

def load_registry():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Error loading {DB_FILE}: {e}")
        return {}

def save_registry(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving {DB_FILE}: {e}")

@router.channel_post(Command("getall"))
@router.message(Command("getall"))
async def cmd_getall(message: Message):
    """
    Retrieves the list of all autonomously cached Channel and Group IDs.
    """
    # Only allow fetching from private chats or public groups/channels if permitted
    registry = load_registry()
    
    if not registry:
        await message.reply("The chat registry is currently empty. The bot hasn't observed any messages in other channels yet.")
        return

    response = "🕷️ **Chat Registry:**\n\n"
    for chat_id, data in registry.items():
        title = data.get("title", "Unknown Chat")
        ctype = data.get("type", "unknown")
        response += f"• **{title}** (`{ctype}`)\n  ID: `{chat_id}`\n\n"

    try:
        await message.reply(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send /getall response: {e}")

@router.channel_post()
@router.message()
async def spider_logger(message: Message):
    """
    Wildcard listener! Silently caches the ID and Title of ANY chat it observes.
    This bypasses Telegram's inability to list bot chats natively.
    """
    # Skip private DMs between user and bot to prevent clutter
    if message.chat.type == "private":
        return

    chat_id = str(message.chat.id)
    chat_title = message.chat.title or "Unnamed Chat"
    chat_type = message.chat.type

    registry = load_registry()

    # If the chat is new or its title changed, update the database
    if chat_id not in registry or registry[chat_id].get("title") != chat_title:
        registry[chat_id] = {
            "title": chat_title,
            "type": chat_type
        }
        save_registry(registry)
        logger.info(f"[SPIDER] Successfully cached new/updated chat footprint: '{chat_title}' ({chat_id})")
