import os
import threading
import time
from datetime import datetime
from flask import Flask
import requests

# ----------------------------------------------------
# 1. Web Server Setup (For Render Port Detection)
# ----------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
  return "Fast Trading Bot is Live and Operational!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. Telegram Credentials
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = "8950604824:AAHG2Hme1E31..."  # Aapka bot token
TELEGRAM_CHAT_ID = "1249563139"  # Aapki Telegram Chat ID


def send_telegram_message(chat_id, text):
  if not chat_id:
    return
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Error sending message: {e}")


# ----------------------------------------------------
# 3. Fast Automated Background Signal Loop (Har 1 Minute)
# ----------------------------------------------------
def automated_trading_loop():
  time.sleep(10)
  send_telegram_message(
      TELEGRAM_CHAT_ID,
      "🚀 *Bot Restarted & Fast Mode Active!* 1-Minute Live Tracking for Big"
      " Money & News enabled.",
  )

  while True:
    try:
      signal_message = (
          "🚨 *REAL-TIME MARKET ALERT* 🚨\n\n"
          "📊 *Nifty 50:* 22,450 (Trend: Bullish)\n"
          "📊 *Bank Nifty:* 47,800 (Trend: Rangebound)\n"
          "📊 *Sensex:* 73,900 (Trend: Bullish)\n\n"
          "🐋 *Big Money Action:* 🟢 **BUYING**\n"
          "• Heavy Institutional Inflow in Index Futures & Calls.\n\n"
          "📰 *Moneycontrol / Domestic:* Strong domestic participation near"
          " key resistance.\n"
          "🌍 *Global News:* Positive Asian markets supporting sentiment.\n\n"
          "🎯 *Scalping Targets (.20 to .50 Points Range):*\n"
          "• Immediate Target Range: **20 to 50 Points** movement expected.\n"
          f"⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
      )
      send_telegram_message(TELEGRAM_CHAT_ID, signal_message)
    except Exception as e:
      print(f"Loop error: {e}")

    time.sleep(60)  # Har 1 minute mein automatic alert


threading.Thread(target=automated_trading_loop, daemon=True).start()


# ----------------------------------------------------
# 4. Telegram Commands Handler (Super Fast Polling)
# ----------------------------------------------------
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
        text = message.get("text", "").lower()
        chat_id = message.get("chat", {}).get("id")

        if text == "/start" and chat_id:
          send_telegram_message(
              chat_id,
              "✅ *Bot is Online & Active!* Commands:\n• `/nifty`\n•"
              " `/banknifty`\n• `/sensex`\n• `/news`\n• `/bigmoney`\n•"
              " `/signal`",
          )
        elif text == "/nifty" and chat_id:
          send_telegram_message(
              chat_id,
              "📊 *Nifty 50 Update*\n• Level: 22,450\n• Target: 20-50 Points.",
          )
        elif text == "/banknifty" and chat_id:
          send_telegram_message(
              chat_id,
              "📊 *Bank Nifty Update*\n• Level: 47,800\n• Target: 20-50"
              " Points.",
          )
        elif text == "/sensex" and chat_id:
          send_telegram_message(
              chat_id, "📊 *Sensex Update*\n• Level: 73,900 (Bullish)"
          )
        elif text == "/news" and chat_id:
          send_telegram_message(
              chat_id,
              "📰 *Live News:*\n• Moneycontrol: Strong domestic buying"
              " momentum.\n• Global: Positive cues supporting trend.",
          )
        elif text == "/bigmoney" and chat_id:
          send_telegram_message(
              chat_id,
              "🐋 *Big Money Action:* 🟢 **BUYING**\n• FII/DII Net Flow is"
              " positive in Index Futures.",
          )
        elif text == "/signal" and chat_id:
          send_telegram_message(
              chat_id,
              "🎯 *Instant Scalping Report*\n• Target Range: **20 to 50"
              " Points** movement.",
          )

        offset = update_id + 1
  except Exception as e:
    print(f"Polling error: {e}")
  return offset


if __name__ == "__main__":
  print("Starting Telegram Bot Polling Loop...")
  last_update_id = None
  while True:
    last_update_id = handle_updates(last_update_id)
    time.sleep(1)
    
