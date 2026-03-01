import os
import requests
import json
import sys
from dotenv import load_dotenv

# Load TELEGRAM_TOKEN from the .env file explicitly
load_dotenv()
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    print("Error: TELEGRAM_TOKEN environment variable is not set.")
    sys.exit(1)

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

print(f"Fetching latest messages sent to the bot...")
try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get("ok"):
        print(f"Error from Telegram API: {data.get('description')}")
        sys.exit(1)
        
    results = data.get("result", [])
    if not results:
        print("\nNo recent messages found for this bot.")
        print("ACTION REQUIRED: Go to your Telegram channel and send a message right now (e.g. 'test').")
        print("Then, run this script again within 24 hours!")
        sys.exit(0)
        
    print("\n--- FOUND RECENT ACTIVITY ---")
    for update in results:
        # Check for channel_post (messages sent in a channel where the bot is an admin)
        if "channel_post" in update:
            chat = update["channel_post"]["chat"]
            print(f"✅ CHANNEL DETECTED!")
            print(f"Channel Title: {chat.get('title')}")
            print(f"Exact CHAT_ID: {chat.get('id')}")
            print("-" * 30)
            
        # Check for standard message (groups, direct messages)
        elif "message" in update:
            chat = update["message"]["chat"]
            chat_type = chat.get("type", "unknown")
            print(f"✅ {chat_type.upper()} DETECTED!")
            print(f"Name/Title: {chat.get('title') or chat.get('first_name')}")
            print(f"Exact CHAT_ID: {chat.get('id')}")
            print("-" * 30)
            
    print("\nCopy the 'Exact CHAT_ID' above and paste it into GitHub Secrets exactly as written (including any minus signs).")
    
except Exception as e:
    print(f"An error occurred: {e}")
