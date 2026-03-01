from flask import Flask, jsonify
import os
import subprocess
import threading

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

if __name__ == '__main__':
    # Render binds the port to the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
