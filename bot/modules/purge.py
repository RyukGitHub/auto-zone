import logging
import asyncio
from typing import List
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="purge")

@router.channel_post(Command("purge"))
@router.message(Command("purge"))
async def cmd_purge(message: Message):
    """
    Deletes a batch of recent messages.
    Usage 1: /purge 10 -> Deletes the last 10 messages.
    Usage 2: Reply to a message with /purge -> Deletes from the replied message up to the current one.
    """
    chat_id = message.chat.id
    current_id = message.message_id
    sender_id = message.from_user.id if message.from_user else chat_id

    # Must be in a group, supergroup, or channel
    if message.chat.type == "private":
        await message.reply("The `/purge` command is only available in Groups and Channels.", parse_mode="Markdown")
        return

    message_ids_to_delete: List[int] = []

    # 1. Check if the command was sent as a Reply
    if message.reply_to_message:
        start_id = message.reply_to_message.message_id
        # Build the exact mathematical range of IDs between the starting message and the current command
        message_ids_to_delete = list(range(start_id, current_id + 1))
        logger.info(f"{sender_id} initiated a range /purge in {message.chat.type} (IDs {start_id} to {current_id}).")
        
    # 2. Check if a number parameter was provided (e.g., /purge 10)
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            # If nothing was provided, tell them how to use it, then self-delete the warning after 5s
            warning = await message.reply("⚠️ Invalid usage.\nReply to a message with `/purge` or type `/purge 10`.", parse_mode="Markdown")
            await asyncio.sleep(5)
            try:
                await message.delete()
                await warning.delete()
            except TelegramBadRequest:
                pass
            return
            
        count = int(parts[1])
        if count <= 0:
            return
            
        # Build the exact mathematical range stretching backwards `count` times
        limit_id = current_id - count + 1
        message_ids_to_delete = list(range(max(1, limit_id), current_id + 1))
        logger.info(f"{sender_id} initiated a numbered /purge {count} in {message.chat.type}.")

    # Telegram limit: delete_messages can only accept 100 IDs per API call max.
    # Chunk the payload mathematically to prevent crashes on large purges.
    chunk_size = 100
    for i in range(0, len(message_ids_to_delete), chunk_size):
        chunk = message_ids_to_delete[i:i + chunk_size]
        try:
            # We use `bot.delete_messages` which is highly efficient for bulk
            await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk)
        except TelegramBadRequest as e:
            logger.warning(f"Partial failure during bulk purge chunk in {chat_id}. Some messages may have already been deleted. Error: {e}")
            
    logger.info(f"Purge complete for {chat_id}.")
