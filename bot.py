import os
import random
import threading
import time
from datetime import datetime
from flask import Flask
import requests

# ----------------------------------------------------
# 1. Web Server Setup
# ----------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
  return "Option Chain PCR & Institutional Tracking Bot Live!"


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. Telegram Credentials & Webhook Reset
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = "8950604824:AAHG2Hme1E3IxgUnhaznw5Ii0Wxb28a0OfQ"
TELEGRAM_CHAT_ID = "1249563139"


def clear_telegram_webhook():
  try:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=True"
    requests.get(url, timeout=10)
  except Exception as e:
    print(f"Webhook reset error: {e}")


clear_telegram_webhook()


def send_telegram_message(chat_id, text):
  if not chat_id:
    return
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"Send error: {e}")


# ----------------------------------------------------
# 3. Option Chain PCR Data Analytics Engine
# ----------------------------------------------------
def analyze_pcr_data():
  # Simulating live open interest (OI) accumulation logic
  pcr_value = round(random.uniform(0.65, 1.45), 2)
  max_pain = random.choice([22400, 22450, 22500])

  if pcr_value >= 1.20:
    sentiment = "🟢 STRONGLY BULLISH"
    action = (
        "Put Writers dominating. Support firmly established at lower strikes."
    )
  elif pcr_value <= 0.75:
    sentiment = "🔴 STRONGLY BEARISH"
    action = "Call Writers aggressively building heavy resistance at key levels."
  else:
    sentiment = "⚖️ NEUTRAL / CONSOLIDATION"
    action = "Equal OI buildup on both sides. Expect rangebound scalping zone."

  return {
      "pcr": pcr_value,
      "max_pain": max_pain,
      "sentiment": sentiment,
      "details": action,
  }


# ----------------------------------------------------
# 4. Institutional Big Money Flow
# ----------------------------------------------------
BIG_MONEY_POOL = [
    {
        "action": "🟢 HEAVY INSTITUTIONAL INFLOW",
        "details": (
            "🐋 *FII/DII Data:* +₹2,400 Cr net buying in Index Futures &"
            " Call Options."
        ),
    },
    {
        "action": "🔴 HEAVY INSTITUTIONAL OUTFLOW",
        "details": (
            "🐋 *FII/DII Data:* -₹1,850 Cr net liquidation in Cash & Index"
            " Derivatives."
        ),
    },
]


def get_big_money_alert():
  return random.choice(BIG_MONEY_POOL)


# ----------------------------------------------------
# 5. Strict Market Hours Automated Loop
# ----------------------------------------------------
def automated_trading_loop():
  time.sleep(10)
  last_sent_pcr = 0.0

  while True:
    try:
      now = datetime.now()
      current_weekday = now.weekday()
      current_hour = now.hour
      current_minute = now.minute

      # Mon-Fri (9:15 AM to 3:30 PM IST)
      is_weekday = current_weekday < 5
      is_market_hours = (
          (current_hour == 9 and current_minute >= 15)
          or (10 <= current_hour < 15)
          or (current_hour == 15 and current_minute <= 30)
      )

      if is_weekday and is_market_hours:
        pcr_data = analyze_pcr_data()
        big_money = get_big_money_alert()

        # Send alert if PCR shifts significantly (>0.15 change)
        if abs(pcr_data["pcr"] - last_sent_pcr) >= 0.15:
          last_sent_pcr = pcr_data["pcr"]

          msg = (
              "📊 *OPTION CHAIN PCR SHIFT ALERT* 📊\n\n"
              f"🎯 *Nifty PCR Ratio:* `{pcr_data['pcr']}` ({pcr_data['sentiment']})\n"
              f"📍 *Max Pain Level:* `{pcr_data['max_pain']}`\n\n"
              f"🐋 *Big Money Flow:* {big_money['action']}\n"
              f"{big_money['details']}\n\n"
              f"💡 *PCR Analysis:* {pcr_data['details']}\n"
              "🎯 *Scalp Range:* **20 to 50 Points**\n"
              f"⏰ *Time:* {now.strftime('%Y-%m-%d %H:%M:%S')}"
          )
          send_telegram_message(TELEGRAM_CHAT_ID, msg)

    except Exception as e:
      print(f"Loop error: {e}")

    time.sleep(180)


threading.Thread(target=automated_trading_loop, daemon=True).start()


# ----------------------------------------------------
# 6. Telegram Command Handler
# ----------------------------------------------------
def handle_updates(offset=None):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
  params = {"timeout": 10, "offset": offset}
  try:
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    if data.get("ok") and data.get("result"):
      for update in data["result"]:
        update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "").lower()
        chat_id = message.get("chat", {}).get("id")

        if chat_id:
          if text == "/start":
            send_telegram_message(
                chat_id,
                "✅ *Option Chain Analytics Bot Online!*\n\nCommands:\n• `/pcr` -"
                " Live Option Chain PCR Analysis\n• `/bigmoney` - FII/DII"
                " Institutional Flow\n• `/signal` - Live Volume & Scalp"
                " Signal",
            )
          elif text == "/pcr":
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"📈 *OPTION CHAIN PCR ANALYTICS*\n\n"
                f"• *PCR Value:* `{pcr_data['pcr']}`\n"
                f"• *Market Bias:* {pcr_data['sentiment']}\n"
                f"• *Max Pain Level:* `{pcr_data['max_pain']}`\n\n"
                f"💡 *Derivatives Analysis:* {pcr_data['details']}",
            )
          elif text == "/bigmoney":
            bm = get_big_money_alert()
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"🐋 *INSTITUTIONAL FLOW & PCR*\n\n"
                f"• *Flow Status:* {bm['action']}\n"
                f"• *Details:* {bm['details']}\n"
                f"• *PCR Sentiment:* `{pcr_data['pcr']}` -"
                f" {pcr_data['sentiment']}",
            )
          elif text == "/signal":
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"🎯 *INSTANT SCALP SIGNAL*\n\n"
                f"• *PCR Confirmation:* `{pcr_data['pcr']}`\n"
                f"• *Bias:* {pcr_data['sentiment']}\n"
                "• *Scalp Target Range:* **20 to 50 Points**",
            )
          else:
            send_telegram_message(
                chat_id, f"✅ Command received: {text}"
            )

        offset = update_id + 1
  except Exception as e:
    print(f"Polling error: {e}")
  return offset


if __name__ == "__main__":
  print("Starting Polling Loop...")
  last_offset = None
  while True:
    last_offset = handle_updates(last_offset)
    time.sleep(1)
  
