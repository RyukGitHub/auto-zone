import os
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="send")

def load_channels():
    """Dynamically parses routing aliases from the CHANNELS_MAP environment variable."""
    try:
        mapping_string = os.environ.get("CHANNELS_MAP", "")
        # Expected format: "nf:-100xx, ml:-100xx"
        channels = {}
        for pair in mapping_string.split(","):
            if ":" in pair:
                alias, chat_id = pair.split(":", 1)
                channels[alias.strip()] = chat_id.strip()
        return channels
    except Exception as e:
        logger.error(f"Error parsing CHANNELS_MAP environment variable: {e}")
        return {}

@router.channel_post(Command("send"))
@router.message(Command("send"))
async def cmd_send(message: Message):
    """Copies a replied-to message into a private channel via alias without a Forward header."""
    sender_id = message.from_user.id if message.from_user else message.chat.id
    
    # 1) Auto-delete the trigger command strictly
    if message.chat.type in ["group", "supergroup", "channel"]:
        try:
            await message.delete()
        except TelegramBadRequest:
            pass

    # 2) Parse the alias (e.g., getting 'nf' from '/send nf')
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        logger.warning(f"No alias provided by {sender_id} for /send.")
        return
    alias = parts[1].strip()

    # 3) Ensure command is deployed as a reply
    if not message.reply_to_message:
        logger.warning(f"{sender_id} tried to /send without Replying to a specific message.")
        return

    # 4) Look up destination mathematically
    channels_map = load_channels()
    dest_id = channels_map.get(alias)
    
    if not dest_id:
        logger.warning(f"Alias '{alias}' not found in channels.json map.")
        return

    # 5) Copy payload blindly to Telegram servers (Anonymous Paste)
    try:
        await message.reply_to_message.copy_to(chat_id=dest_id)
        logger.info(f"Successfully Copied message to '{alias}' ({dest_id}).")
    except Exception as e:
        logger.error(f"Failed to copy message to '{alias}': {e}")
