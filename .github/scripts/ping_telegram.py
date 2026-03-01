import os
import requests
import sys

def main():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    message = os.environ.get('TEST_MESSAGE', '✅ This is a test ping from GitHub Actions using Python!')

    if not token or not chat_id:
        print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID secret is missing.", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if not data.get("ok"):
            print(f"❌ Telegram API Error: {data.get('description')}", file=sys.stderr)
            sys.exit(1)
            
        print("✅ SUCCESS! Message sent via Python requests.")
    except Exception as e:
        print(f"❌ Request failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
