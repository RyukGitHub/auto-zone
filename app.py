from flask import Flask, jsonify, request
import os
import subprocess
import threading
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "ACH Automation Bot is Alive and Running!"

@app.route('/ping')
def ping():
    """Endpoint to hit to keep Render awake."""
    return jsonify({"status": "alive", "message": "Hi!"})

@app.route('/run-tests')
def run_tests():
    """Optional endpoint to trigger the bot execution manually over HTTP."""
    def execute_robot():
        # You can pass additional arguments here or pull them from the request args
        subprocess.run(["python", "-m", "robot", "-d", "results", "tests/"])
        
    thread = threading.Thread(target=execute_robot)
    thread.start()
    return jsonify({"status": "started", "message": "Test execution has begun in the background."})

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Endpoint to receive updates from Telegram."""
    data = request.json
    if not data:
        return "OK", 200
        
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        
        if text.startswith("/start"):
            telegram_token = os.environ.get('TELEGRAM_TOKEN')
            if telegram_token:
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "🤖 ACH Automation Bot is online and ready! Render is running fine."
                }
                try:
                    requests.post(url, json=payload, timeout=5)
                except Exception as e:
                    print(f"Error sending message: {e}")
                
    return "OK", 200

@app.route('/set-webhook')
def set_webhook():
    """Helper endpoint to register the webhook with Telegram."""
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    
    # Render provides RENDER_EXTERNAL_URL in the environment automatically!
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    
    if not telegram_token or not render_url:
        return jsonify({
            "status": "error", 
            "message": "Missing TELEGRAM_TOKEN or RENDER_EXTERNAL_URL environment variable."
        }), 400
        
    webhook_url = f"{render_url}/telegram-webhook"
    url = f"https://api.telegram.org/bot{telegram_token}/setWebhook?url={webhook_url}"
    
    try:
        response = requests.get(url, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Render binds the port to the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
