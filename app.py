"""
Main web service entry point for Render deployment and Telegram integration.
Provides a background keep-alive ping endpoint and an asynchronous Aiogram long-polling loop.
"""

import asyncio
import logging
import os
import subprocess
import threading

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "ACH Automation Bot is Alive and Running!"

@app.route('/health')
def health():
    """Endpoint to check service health."""
    return jsonify({"status": "ok", "message": "Service is healthy"})

@app.route('/run-tests')
def run_tests():
    """Optional endpoint to trigger the bot execution manually over HTTP."""
    def execute_robot():
        # You can pass additional arguments here or pull them from the request args
        subprocess.run(["python", "-m", "robot", "-d", "results", "tests/"])
        
    thread = threading.Thread(target=execute_robot)
    thread.start()
    return jsonify({"status": "started", "message": "Test execution has begun in the background."})

from bot.main import start_telegram_bot

# ==========================================
# Application Background Thread
# ==========================================
def run_bot_thread():
    """Runs the asyncio event loop natively without colliding with Flask."""
    asyncio.run(start_telegram_bot())

# IMPORTANT: Initialize the thread globally so Gunicorn triggers it when it imports `app.py`.
bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    # Local fallback for `python app.py`
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
