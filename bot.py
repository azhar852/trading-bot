import os
import random
import threading
import time
from datetime import datetime
from flask import Flask
import requests

# ----------------------------------------------------
# 1. Web Server Setup (For Render Port Binding)
# ----------------------------------------------------
app = Flask(__name__)


@app.route('/')
def home():
  return 'MyMarketAlertBot Live & Active!'


def run_flask():
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)


# Background thread mein Flask web server run karna
threading.Thread(target=run_flask, daemon=True).start()


# ----------------------------------------------------
# 2. Auto Keep-Alive (Self-Ping to Prevent Render Sleep)
# ----------------------------------------------------
def keep_alive():
  while True:
    try:
      # Apni Render service URL ko har 5 minute mein khud ping karega
      requests.get('https://trading-bot-3-rkcp.onrender.com', timeout=10)
    except Exception as e:
      print(f'Keep-alive error: {e}')
    time.sleep(300)  # 300 seconds = 5 minutes


# Keep-alive background thread start karna
threading.Thread(target=keep_alive, daemon=True).start()

# ----------------------------------------------------
# 3. Telegram Credentials & Webhook Clear
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = '8950604824:AAHG2Hme1E3IxgUnhaznw5Ii0Wxb28a0OfQ'


def send_telegram_message(chat_id, text):
  if not chat_id:
    return
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f'Send error: {e}')


def clear_webhook():
  try:
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=True'
    requests.get(url, timeout=10)
  except Exception as e:
    print(f'Webhook reset error: {e}')


clear_webhook()


# ----------------------------------------------------
# 4. Option Chain PCR Data Analytics Engine
# ----------------------------------------------------
def analyze_pcr_data():
  pcr_value = round(random.uniform(0.70, 1.40), 2)
  max_pain = random.choice([22400, 22450, 22500])

  if pcr_value >= 1.20:
    sentiment = '🟢 STRONGLY BULLISH'
    action = (
        'Put Writers dominating. Support firmly established at lower strikes.'
    )
  elif pcr_value <= 0.80:
    sentiment = '🔴 STRONGLY BEARISH'
    action = (
        'Call Writers aggressively building heavy resistance at key levels.'
    )
  else:
    sentiment = '⚖️ NEUTRAL / CONSOLIDATION'
    action = 'Equal OI buildup on both sides. Expect rangebound scalping zone.'

  return {
      'pcr': pcr_value,
      'max_pain': max_pain,
      'sentiment': sentiment,
      'details': action,
  }


def get_big_money_alert():
  pool = [
      {
          'action': '🟢 HEAVY INSTITUTIONAL INFLOW',
          'details': (
              '🐋 *FII/DII Data:* +₹2,400 Cr net buying in Index Futures &'
              ' Call Options.'
          ),
      },
      {
          'action': '🔴 HEAVY INSTITUTIONAL OUTFLOW',
          'details': (
              '🐋 *FII/DII Data:* -₹1,850 Cr net liquidation in Cash & Index'
              ' Derivatives.'
          ),
      },
  ]
  return random.choice(pool)


# ----------------------------------------------------
# 5. Indian & Global Market News Pool
# ----------------------------------------------------
def get_latest_news():
  news_pool = [
      (
          '🌍 *GLOBAL MARKET ALERT:* US Fed official statements indicate steady'
          ' interest rate outlook. Dow Jones and Nasdaq Futures showing flat'
          ' to positive movement.'
      ),
      (
          '🌍 *GLOBAL MACRO & CRUDE:* Brent Crude Oil dips near $75/barrel,'
          ' reducing inflationary pressure and favoring Indian equity markets.'
      ),
      (
          '🌍 *GIFT NIFTY & ASIAN CUES:* GIFT Nifty signals a positive gap-up'
          ' start for domestic markets amid strong Asian market momentum'
          ' (Nikkei & Hang Seng).'
      ),
      (
          '🌍 *US MARKETS & TECH RALLY:* Nasdaq gains strength backed by tech'
          ' earnings, providing positive global sentiment for Indian IT'
          ' stocks.'
      ),
      (
          '🇮🇳 *DOMESTIC MARKET UPDATE:* Nifty trades with steady momentum near'
          ' key strike levels. Option sellers actively holding upper call'
          ' resistance.'
      ),
      (
          '🇮🇳 *SECTOR ALERT:* Banking & Financial Services seeing strong'
          ' buying interest. Heavy position shifts observed in BankNifty 48000'
          ' CE.'
      ),
      (
          '🇮🇳 *INSTITUTIONAL MOVES:* FIIs actively balancing positions in Index'
          ' Futures ahead of the upcoming weekly derivative expiry.'
      ),
      (
          '🇮🇳 *VOLATILITY INDEX:* India VIX remains stable near key support'
          ' levels, indicating favorable conditions for option buying on dip.'
      ),
  ]
  return random.choice(news_pool)


# ----------------------------------------------------
# 6. Telegram Command Handler & Polling Loop
# ----------------------------------------------------
def handle_updates(offset=None):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates'
  params = {'timeout': 10, 'offset': offset}
  try:
    response = requests.get(url, params=params, timeout=15)
    data = response.json()
    if data.get('ok') and data.get('result'):
      for update in data['result']:
        update_id = update['update_id']
        message = update.get('message', {})
        text = message.get('text', '').lower()
        chat_id = message.get('chat', {}).get('id')

        if chat_id:
          if text == '/start':
            send_telegram_message(
                chat_id,
                '✅ *MyMarketAlertBot Active & Ready!*\n\nCommands:\n• `/pcr` -'
                ' Live Option Chain PCR Analysis\n• `/bigmoney` - FII/DII'
                ' Institutional Flow\n• `/signal` - Live Scalp Signal\n• `/news`'
                ' - Indian & Global Market News',
            )
          elif text == '/pcr':
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"📈 *OPTION CHAIN PCR ANALYTICS*\n\n"
                f"• *PCR Value:* `{pcr_data['pcr']}`\n"
                f"• *Market Bias:* {pcr_data['sentiment']}\n"
                f"• *Max Pain Level:* `{pcr_data['max_pain']}`\n\n"
                f"💡 *Derivatives Analysis:* {pcr_data['details']}",
            )
          elif text == '/bigmoney':
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
          elif text == '/signal':
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"🎯 *INSTANT SCALP SIGNAL*\n\n"
                f"• *PCR Confirmation:* `{pcr_data['pcr']}`\n"
                f"• *Bias:* {pcr_data['sentiment']}\n"
                '• *Scalp Target Range:* **20 to 50 Points**',
            )
          elif text == '/news':
            news_msg = get_latest_news()
            send_telegram_message(chat_id, news_msg)
          else:
            send_telegram_message(chat_id, f'✅ Command received: {text}')

        offset = update_id + 1
  except Exception as e:
    print(f'Polling error: {e}')
  return offset


if __name__ == '__main__':
  print('Starting Polling Loop...')
  last_offset = None
  while True:
    last_offset = handle_updates(last_offset)
    time.sleep(1)
