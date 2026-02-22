import os
from datetime import datetime
import pytz
import requests
from robot.api import logger
from dotenv import load_dotenv

class DiscordNotifier:
    """Custom Robot Framework Library for sending Discord Webhook Notifications."""
    
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        # Load environment variables from .env file for local testing
        load_dotenv()
        
        # Map full site names to their abbreviated versions for Discord
        self.SITE_MAP = {
            'nfbusty': 'nf',
            'momlover': 'ml',
            'brattysis': 'bs',
            'nubiles-porn': 'np'
        }

    def send_discord_notification(self, test_status, site_name, email, password, ac_no, rt_no):
        """
        Sends a success notification to Discord using the webhook URL stored in the environment.
        Only sends if the test passed.
        """
        if test_status != "PASS":
            logger.info("Test did not pass. Skipping Discord notification.")
            return

        # Check if a webhook URL exists
        webhook_url = os.environ.get('ACH_DISCORD_WEBHOOK_URL')
        if not webhook_url:
            logger.warn("ACH_DISCORD_WEBHOOK_URL environment variable is not set. Skipping notification.")
            return

        # Convert the site name to its mapped abbreviation, fallback to the original if not found
        mapped_site = self.SITE_MAP.get(site_name.lower(), site_name)
        
        # Format the current date (e.g., "22 Feb")
        timezone = pytz.timezone('Asia/Kolkata')
        current_date_formatted = datetime.now(timezone).strftime("%d %b")

        # Handle scenario where email is an empty string in Robot Framework explicitly
        display_email = email if email and email != "${EMPTY}" else "Not Provided"

        # Construct the Discord message payload
        message = (
            f"**✅ Automation Test Passed**\n"
            f"**Site:** {mapped_site}\n"
            f"**Email:** {display_email}\n"
            f"**Password:** {password}\n"
            f"**AC NO:** {ac_no}\n"
            f"**RT NO:** {rt_no}\n"
            f"**Created Date:** {current_date_formatted}"
        )

        payload = {
            "content": message
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully sent Discord notification. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
