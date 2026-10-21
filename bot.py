import os
import threading
import time
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask
import requests
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# ----------------------------------------------------
# 1. Web Server Setup (For Render Port Detection)
# ----------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
  return "Trading Bot is Live and Operational!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# Start Flask server in background thread
threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. AI Model Setup (FinBERT)
# ----------------------------------------------------
print("Loading AI Brain (FinBERT Model)... Please wait...")
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print("✅ Master AI Brain & All Advanced Features Loaded Successfully!")

# ----------------------------------------------------
# 3. Telegram Credentials & Global Variables
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = "8950604824:AAHG2Hme1E31..."  # Aapka bot token
TELEGRAM_CHAT_ID = ""  # Chat ID agar zaroorat ho


# ----------------------------------------------------
# 4. Telegram Polling / Logic Setup
# ----------------------------------------------------
def send_telegram_message(chat_id, text):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Error sending message: {e}")


def handle_updates(offset=None):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
  params = {"timeout": 30, "offset": offset}
  try:
    response = requests.get(url, params=params, timeout=35)
    data = response.json()
    if data.get("ok") and data.get("result"):
      for update in data["result"]:
        update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if text == "/start" and chat_id:
          send_telegram_message(
              chat_id,
              "✅ Scalping Bot Active Hai! Market Time (9:15 AM - 3:30 PM)"
              " Mein Automated Signals Milenge.",
          )

        offset = update_id + 1
  except Exception as e:
    print(f"Polling error: {e}")
  return offset


# ----------------------------------------------------
# 5. Main Execution Loop
# ----------------------------------------------------
if __name__ == "__main__":
  print("Starting Telegram Bot Polling Loop...")
  last_update_id = None
  while True:
    last_update_id = handle_updates(last_update_id)
    time.sleep(1)
      
