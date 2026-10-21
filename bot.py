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
  return "Real-time AI Trading Bot is Live and Operational!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. AI Model Setup (FinBERT)
# ----------------------------------------------------
print("Loading AI Brain (FinBERT Model)...")
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
print("✅ FinBERT AI Brain Loaded Successfully!")

# ----------------------------------------------------
# 3. Telegram Credentials
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
# 4. Market Data, Global, Moneycontrol & Big Money Buy/Sell
# ----------------------------------------------------
def get_market_data():
  # Example simulation for Big Money Buy/Sell detection
  big_money_action = "🟢 BUYING"  # Status: "🟢 BUYING" ya "🔴 SELLING"

  return {
      "nifty": "Nifty 50: 22,450 (Trend: Bullish)",
      "banknifty": "Bank Nifty: 47,800 (Trend: Rangebound)",
      "sensex": "Sensex: 73,900 (Trend: Bullish)",
      "big_money_status": big_money_action,
      "smart_money_details": (
          f"🐋 *Big Money Action:* **{big_money_action}**\n"
          "• FIIs/DIIs Net Flow: Heavy Institutional Inflow in Index Futures &"
          " Calls.\n"
          "• Action Suggestion: Look for Long/Call Scalping Opportunities."
      ),
      "domestic_news": (
          "Moneycontrol Breaking: Strong domestic participation pushing indices"
          " near key resistance."
      ),
      "global_news": (
          "Global Breaking: Positive Asian markets and stable US futures"
          " supporting sentiment."
      ),
  }


def analyze_market_sentiment(text):
  inputs = tokenizer(
      text, return_tensors="pt", padding=True, truncation=True, max_length=512
  )
  outputs = model(**inputs)
  probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
  sentiment_idx = torch.argmax(probs).item()
  labels = ["📈 BULLISH (Positive)", "📉 BEARISH (Negative)", "⚖️ NEUTRAL"]
  return labels[sentiment_idx]


# ----------------------------------------------------
# 5. Fast Automated Background Signal Loop (Har 1 Min)
# ----------------------------------------------------
def automated_trading_loop():
  time.sleep(15)
  send_telegram_message(
      TELEGRAM_CHAT_ID,
      "🚀 *Real-Time AI Bot Active!* 1-Minute Live Tracking for Big Money"
      " BUY/SELL & Breaking News Enabled.",
  )

  while True:
    try:
      data = get_market_data()
      combined_news = f"{data['domestic_news']} {data['global_news']}"
      sentiment = analyze_market_sentiment(combined_news)

      signal_message = (
          "🚨 *REAL-TIME BREAKING MARKET ALERT* 🚨\n\n"
          f"📊 *{data['nifty']}*\n"
          f"📊 *{data['banknifty']}*\n"
          f"📊 *{data['sensex']}*\n\n"
          f"{data['smart_money_details']}\n\n"
          f"📰 *Moneycontrol / Domestic:* {data['domestic_news']}\n"
          f"🌍 *Global News:* {data['global_news']}\n"
          f"🧠 *AI Sentiment:* {sentiment}\n\n"
          "🎯 *Scalping Targets (.20 to .50 Points Range):*\n"
          "• Scalp Range: **20 to 50 Points** target active on breakout.\n"
          f"⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
      )

      send_telegram_message(TELEGRAM_CHAT_ID, signal_message)

    except Exception as e:
      print(f"Loop error: {e}")

    # Har 60 seconds (1 min) mein fast check
    time.sleep(60)


threading.Thread(target=automated_trading_loop, daemon=True).start()


# ----------------------------------------------------
# 6. Telegram Commands Handler
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
              "✅ *Bot Active! Available Commands:*\n\n"
              "• `/nifty` - Nifty 50 Status\n"
              "• `/banknifty` - Bank Nifty Status\n"
              "• `/sensex` - Sensex Status\n"
              "• `/news` - Live News & AI Sentiment\n"
              "• `/bigmoney` - Big Money BUY/SELL Alert\n"
              "• `/signal` - Complete Scalping Report",
          )
        elif text == "/nifty" and chat_id:
          send_telegram_message(
              chat_id,
              "📊 *Nifty 50 Analysis*\n• Level: 22,450\n• Scalp Target: 20-50"
              " Points.",
          )
        elif text == "/banknifty" and chat_id:
          send_telegram_message(
              chat_id,
              "📊 *Bank Nifty Analysis*\n• Level: 47,800\n• Breakout Target:"
              " 20-50 Points.",
          )
        elif text == "/sensex" and chat_id:
          send_telegram_message(
              chat_id, "📊 *Sensex Analysis*\n• Level: 73,900"
          )
        elif text == "/news" and chat_id:
          m_data = get_market_data()
          sent = analyze_market_sentiment(
              f"{m_data['domestic_news']} {m_data['global_news']}"
          )
          send_telegram_message(
              chat_id,
              f"📰 *Moneycontrol:*\n{m_data['domestic_news']}\n\n🌍"
              f" *Global:*\n{m_data['global_news']}\n\n🧠"
              f" *Sentiment:* {sent}",
          )
        elif text == "/bigmoney" and chat_id:
          m_data = get_market_data()
          send_telegram_message(chat_id, m_data["smart_money_details"])
        elif text == "/signal" and chat_id:
          m_data = get_market_data()
          sent = analyze_market_sentiment(
              f"{m_data['domestic_news']} {m_data['global_news']}"
          )
          send_telegram_message(
              chat_id,
              "🎯 *Instant Scalping Report*\n\n"
              f"🐋 Big Money Action: **{m_data['big_money_status']}**\n"
              f"🧠 AI Sentiment: {sent}\n"
              f"🎯 Target Range: **20 to 50 Points**.",
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
    
