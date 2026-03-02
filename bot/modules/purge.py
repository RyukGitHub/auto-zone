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
            
        logger.info(f"{sender_id} initiated a numbered /purge {count} in {message.chat.type}.")
        
        # We need to explicitly delete `count` messages. Because Telegram IDs auto-increment 
        # even for deleted/ghost messages, we can't just subtract mathematically.
        # We must loop backward in chunks until we hit the target.
        deleted_count = 0
        search_id = current_id
        
        while deleted_count < count and search_id > 0:
            # Grab a maximum slice of 100 backwards
            chunk_needed = min(100, count - deleted_count)
            chunk_ids = list(range(max(1, search_id - chunk_needed + 1), search_id + 1))
            
            try:
                # delete_messages will silently ignore IDs that don't exist anymore.
                # However, it returns True if at least ONE message in the chunk was deleted.
                # Since we cannot easily verify EXACTLY how many survived the purge, 
                # we assume a 1:1 deletion rate for mathematical simplicity in Channels.
                await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk_ids)
                deleted_count += len(chunk_ids)
            except TelegramBadRequest as e:
                # If a chunk fails entirely (e.g., all messages were already deleted), just skip backward.
                logger.debug(f"Chunk deletion skipped near ID {search_id}: {e}")
                pass
                
            search_id -= chunk_size
            
        logger.info(f"Purge complete for {chat_id}.")
        return

    # Range Purge Execution (from Reply)
    chunk_size = 100
    for i in range(0, len(message_ids_to_delete), chunk_size):
        chunk = message_ids_to_delete[i:i + chunk_size]
        try:
            await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk)
        except TelegramBadRequest as e:
            logger.warning(f"Partial failure during bulk purge chunk in {chat_id}. Error: {e}")
            
    logger.info(f"Purge complete for {chat_id}.")
