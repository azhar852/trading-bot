import os
import threading
import time
from datetime import datetime
from flask import Flask
import requests

try:
  import yfinance as yf
except ImportError:
  os.system('pip install yfinance')
  import yfinance as yf

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


threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. Telegram Credentials & Configuration
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = '8950604824:AAHG2Hme1E3IxgUnhaznw5Ii0Wxb28a0OfQ'
REGISTERED_CHAT_IDS = set()

# Last alert state tracker (taaki repeated/late alerts na aayein)
LAST_SIGNAL_STATE = None


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
# 3. Auto Keep-Alive (Self-Ping)
# ----------------------------------------------------
def keep_alive():
  while True:
    try:
      requests.get('https://trading-bot-3-rkcp.onrender.com', timeout=10)
    except Exception as e:
      print(f'Keep-alive error: {e}')
    time.sleep(300)


threading.Thread(target=keep_alive, daemon=True).start()


# ----------------------------------------------------
# 4. Live Price Action & Fresh Entry Engine
# ----------------------------------------------------
def check_fresh_entry_signal(symbol='^NSEI'):
  """Har 1 minute mein check karta hai ki Nayi Live Entry bani hai ya nahi."""
  try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='1d', interval='1m')

    if len(data) >= 5:
      latest_close = round(data['Close'].iloc[-1], 2)
      prev_close = round(data['Close'].iloc[-2], 2)
      open_price = round(data['Open'].iloc[0], 2)

      # Short-term Momentum (Last 5 candles average)
      sma_5 = round(data['Close'].tail(5).mean(), 2)

      # Entry Logic
      if latest_close > sma_5 and prev_close <= sma_5:
        return {
            'type': 'BUY_CALL',
            'price': latest_close,
            'status': '🟢 FRESH BULLISH ENTRY TRIGGERED',
            'action': (
                f'Nifty breaks above 5-min average (`{sma_5}`). Good for CE'
                ' Entry RIGHT NOW.'
            ),
        }
      elif latest_close < sma_5 and prev_close >= sma_5:
        return {
            'type': 'BUY_PUT',
            'price': latest_close,
            'status': '🔴 FRESH BEARISH ENTRY TRIGGERED',
            'action': (
                f'Nifty breaks below 5-min average (`{sma_5}`). Good for PE'
                ' Entry RIGHT NOW.'
            ),
        }
  except Exception as e:
    print(f'Entry Check Error: {e}')

  return None


# ----------------------------------------------------
# 5. REAL-TIME INSTANT ENTRY BROADCASTER
# ----------------------------------------------------
def real_time_entry_scanner():
  """Har 60 seconds mein market scan karta hai aur sirf taaza entry par hi alert bhejta hai."""
  global LAST_SIGNAL_STATE

  while True:
    try:
      signal = check_fresh_entry_signal('^NSEI')

      # Nayi entry mili aur pehle se alag hai toh alert bhejega
      if signal and signal['type'] != LAST_SIGNAL_STATE:
        LAST_SIGNAL_STATE = signal['type']

        if REGISTERED_CHAT_IDS:
          msg = (
              f"⚡ *REAL-TIME LIVE ENTRY ALERT*\n\n"
              f"• *Status:* {signal['status']}\n"
              f"• *Live Price:* `{signal['price']}`\n\n"
              f"💡 *Trading Setup:* {signal['action']}\n"
              f"⏱️ *Entry Validity:* Active Now (Strict Stop-Loss Required)"
          )
          for c_id in list(REGISTERED_CHAT_IDS):
            send_telegram_message(c_id, msg)

      time.sleep(60)  # Har 1 minute par scanning
    except Exception as e:
      print(f'Scanner Error: {e}')
      time.sleep(60)


threading.Thread(target=real_time_entry_scanner, daemon=True).start()


# ----------------------------------------------------
# 6. Telegram Command Handler
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
          REGISTERED_CHAT_IDS.add(chat_id)

          if text in ['/start', 'start']:
            send_telegram_message(
                chat_id,
                '✅ *MyMarketAlertBot Real-Time Entry Scanner Ready!*\n\n'
                'Ab jab bhi fresh Entry trigger hogi, aapko instant alert'
                ' milega.\n\n'
                'Commands:\n'
                '• `/signal` - Instant Scalp Check\n'
                '• `/nifty` - Live Nifty Real Price\n'
                '• `/bigmoney` - Smart Money Flow\n'
                '• `/commodity` - Live MCX Alerts',
            )
          elif text in ['/signal', '/trend']:
            try:
              ticker = yf.Ticker('^NSEI')
              df = ticker.history(period='1d', interval='1m')
              lp = round(df['Close'].iloc[-1], 2)
              send_telegram_message(
                  chat_id,
                  f'🎯 *LIVE SCALP CHECK*\n\n• *Live Nifty Price:* `{lp}`\n•'
                  ' *Scanner:* Continuous 1-min active scanning for fresh'
                  ' breakouts.',
              )
            except Exception:
              send_telegram_message(
                  chat_id, '⚡ Market Scanner active. Waiting for fresh setup.'
              )
          else:
            send_telegram_message(
                chat_id,
                '✅ Command received. Real-time entry scanner active.',
            )

        offset = update_id + 1
  except Exception as e:
    print(f'Polling error: {e}')
  return offset


if __name__ == '__main__':
  print('Starting Real-Time Polling Loop...')
  last_offset = None
  while True:
    last_offset = handle_updates(last_offset)
    time.sleep(1)
      
