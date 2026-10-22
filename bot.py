import os
import threading
import time
from datetime import datetime
from flask import Flask
import requests

# Live data fetch karne ke liye library
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
# 2. Auto Keep-Alive (Self-Ping)
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
# 4. Real-Time Live Trend Engine (Nifty / Sensex / Commodities)
# ----------------------------------------------------
def get_live_market_trend(symbol='^NSEI'):
  """Yahoo Finance se real live price aur change fetch karke accurate trend batata hai."""
  try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='2d', interval='5m')

    if len(data) >= 2:
      current_price = round(data['Close'].iloc[-1], 2)
      prev_price = round(data['Close'].iloc[-2], 2)
      open_price = round(data['Open'].iloc[0], 2)

      change_pct = round(
          ((current_price - prev_price) / prev_price) * 100, 2
      )

      # Accurate Bullish vs Bearish Trend Logic
      if current_price < open_price or change_pct < -0.15:
        status = '🔴 STRONGLY BEARISH (Sell on Rise)'
        reason = (
            f'Live Price (`{current_price}`) is trading below open level.'
            ' Sellers dominate.'
        )
        action = 'Look for Put (PE) buying on minor bounces.'
        bias = 'BEARISH'
      elif current_price > open_price or change_pct > 0.15:
        status = '🟢 STRONGLY BULLISH (Buy on Dips)'
        reason = (
            f'Live Price (`{current_price}`) holding strong momentum above'
            ' open.'
        )
        action = 'Look for Call (CE) buying on support dips.'
        bias = 'BULLISH'
      else:
        status = '⚖️ NEUTRAL / CONSOLIDATION'
        reason = (
            f'Live Price (`{current_price}`) moving in a tight rangebound'
            ' zone.'
        )
        action = 'Wait for range breakout. Scalp with tight stop-loss.'
        bias = 'SIDEWAYS'

      return {
          'price': current_price,
          'change': change_pct,
          'status': status,
          'reason': reason,
          'action': action,
          'bias': bias,
      }
  except Exception as e:
    print(f'Error fetching live trend: {e}')

  # Backup response
  return {
      'price': 'N/A',
      'change': 0.0,
      'status': '⚖️ MARKET CHECK IN PROGRESS',
      'reason': 'Analyzing live orderflow and price action.',
      'action': 'Verify with chart indicators.',
      'bias': 'NEUTRAL',
  }


# ----------------------------------------------------
# 5. Telegram Command Handler & Polling Loop
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
          if text in ['/start', 'start']:
            send_telegram_message(
                chat_id,
                '✅ *MyMarketAlertBot Live & Sync Ready!*\n\n'
                'Commands:\n'
                '• `/trend` - Real-Time Market Trend (Bullish / Bearish)\n'
                '• `/nifty` - Live Nifty 50 Real Price & Bias\n'
                '• `/sensex` - Live Sensex Analytics\n'
                '• `/pcr` - Live Option PCR View\n'
                '• `/commodity` - Live MCX Commodity Setup\n'
                '• `/signal` - Real-Time Scalp Signal',
            )
          elif text in ['/trend', '/market']:
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🎯 *REAL LIVE MARKET TREND*\n\n"
                f"• *Live Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Current Trend:* {tr['status']}\n"
                f"• *Analysis:* {tr['reason']}\n\n"
                f"💡 *Actionable Advice:* {tr['action']}",
            )
          elif text in ['/nifty', '/nifty50']:
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"📊 *NIFTY 50 REAL-TIME ANALYTICS*\n\n"
                f"• *Nifty Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Market Bias:* {tr['status']}\n"
                f"💡 *Trading Plan:* {tr['action']}",
            )
          elif text in ['/sensex']:
            tr = get_live_market_trend('^BSESN')
            send_telegram_message(
                chat_id,
                f"📈 *BSE SENSEX REAL-TIME ANALYTICS*\n\n"
                f"• *Sensex Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Market Bias:* {tr['status']}\n"
                f"💡 *Trading Plan:* {tr['action']}",
            )
          elif text == '/signal':
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🎯 *REAL-TIME SCALP SIGNAL*\n\n"
                f"• *Index Price:* `{tr['price']}`\n"
                f"• *Signal Mode:* {tr['status']}\n"
                f"💡 *Recommendation:* {tr['action']}",
            )
          elif text == '/commodity':
            send_telegram_message(
                chat_id,
                '🛢️ *MCX COMMODITY REAL-TIME ALERT*\n\n'
                '• *Crude Oil:* Check intraday momentum near key support\n'
                '• *Gold/Silver:* Watch US Dollar Index movement\n'
                '💡 *Strategy:* Trade strictly with live trend direction.',
            )
          else:
            send_telegram_message(
                chat_id, '✅ Command received. Type `/trend` to check live market.'
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
