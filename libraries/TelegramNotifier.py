import os
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv
from robot.api import logger


class TelegramNotifier:
    """Custom Robot Framework Library for sending Telegram Bot Notifications."""
    
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        # Load environment variables from .env file for local testing
        load_dotenv()
        
        # Map full site names to their abbreviated versions for Telegram
        self.SITE_MAP = {
            'nfbusty': 'nf',
            'momlover': 'ml',
            'brattysis': 'bs',
            'nubiles-porn': 'np',
            'anilos': 'an',
            'thepovgod': 'tpg',
            'deeplush': 'dl'
        }

    def send_telegram_notification(self, test_status, site_name, email, password, ac_no, rt_no):
        """
        Sends a success notification to Telegram using the bot token stored in the environment.
        Only sends if the test passed.
        """
        if test_status != "PASS":
            logger.info("Test did not pass. Skipping Telegram notification.")
            return

        # Check if a bot token and chat ID exist
        telegram_token = os.environ.get('TELEGRAM_TOKEN')
        telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not telegram_token or not telegram_chat_id:
            logger.warn("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variable is not set. Skipping notification.")
            return

        # Convert the site name to its mapped abbreviation, fallback to the original if not found
        mapped_site = self.SITE_MAP.get(site_name.lower(), site_name)
        
        # Format the current date (e.g., "22 Feb")
        timezone = pytz.timezone('Asia/Kolkata')
        current_date_formatted = datetime.now(timezone).strftime("%d %b")

        # Handle scenario where email is an empty string in Robot Framework explicitly
        display_email = email if email and email != "${EMPTY}" else "Not Provided"

        # Construct the Telegram message payload (using MarkdownV2 or HTML, we'll use HTML for simplicity and robust parsing, or basic Markdown)
        message = (
            f"✅ *Automation Test Passed*\n"
            f"*Site:* #{mapped_site}\n"
            f"*Email:* `{display_email}`\n"
            f"*Password:* `{password}`\n"
            f"*AC NO:* `{ac_no}`\n"
            f"*RT NO:* `{rt_no}`\n"
            f"*Created Date:* {current_date_formatted}"
        )

        payload = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully sent Telegram notification. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Telegram API response: {e.response.text}")
