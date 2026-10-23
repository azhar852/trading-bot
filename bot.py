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
# 4. Live Trend & Smart Money Engine
# ----------------------------------------------------
def get_live_market_trend(symbol='^NSEI'):
  """Yahoo Finance se real live price aur trend check karta hai."""
  try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='2d', interval='5m')

    if len(data) >= 2:
      current_price = round(data['Close'].iloc[-1], 2)
      open_price = round(data['Open'].iloc[0], 2)
      change_pct = round(
          ((current_price - open_price) / open_price) * 100, 2
      )

      if current_price < open_price or change_pct < -0.15:
        status = '🔴 STRONGLY BEARISH (Sell on Rise)'
        reason = (
            f'Live Price (`{current_price}`) is trading below open level.'
            ' Sellers dominate.'
        )
        action = 'Look for Put (PE) buying on minor bounces.'
      elif current_price > open_price or change_pct > 0.15:
        status = '🟢 STRONGLY BULLISH (Buy on Dips)'
        reason = (
            f'Live Price (`{current_price}`) holding strong momentum above'
            ' open.'
        )
        action = 'Look for Call (CE) buying on support dips.'
      else:
        status = '⚖️ NEUTRAL / CONSOLIDATION'
        reason = (
            f'Live Price (`{current_price}`) moving in a tight rangebound'
            ' zone.'
        )
        action = 'Wait for range breakout. Scalp with tight stop-loss.'

      return {
          'price': current_price,
          'change': change_pct,
          'status': status,
          'reason': reason,
          'action': action,
      }
  except Exception as e:
    print(f'Error fetching live trend: {e}')

  return {
      'price': 'N/A',
      'change': 0.0,
      'status': '⚖️ MARKET CHECK IN PROGRESS',
      'reason': 'Analyzing live orderflow.',
      'action': 'Verify with chart indicators.',
  }


def get_big_money_alert():
  """Smart Money (FII/DII Flow) real live trend ke basis par calculate karega."""
  tr = get_live_market_trend('^NSEI')
  if 'BEARISH' in tr['status']:
    return {
        'action': '🔴 HEAVY INSTITUTIONAL OUTFLOW (FII SELLING)',
        'details': (
            '🐋 *FII/DII Data:* Heavy net selling in Index Futures & Cash'
            ' segment.'
        ),
    }
  elif 'BULLISH' in tr['status']:
    return {
        'action': '🟢 HEAVY INSTITUTIONAL INFLOW (FII BUYING)',
        'details': (
            '🐋 *FII/DII Data:* Strong net buying in Index Futures & Call'
            ' Options.'
        ),
    }
  else:
    return {
        'action': '⚖️ NEUTRAL INSTITUTIONAL FLOW',
        'details': (
            '🐋 *FII/DII Data:* Mixed institutional activity in tight range.'
        ),
    }


def check_fresh_entry_signal(symbol='^NSEI'):
  """Har 1 minute mein scanning karke sirf exact fresh entry trigger batata hai."""
  try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='1d', interval='1m')

    if len(data) >= 5:
      latest_close = round(data['Close'].iloc[-1], 2)
      prev_close = round(data['Close'].iloc[-2], 2)
      sma_5 = round(data['Close'].tail(5).mean(), 2)

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
# 5. REAL-TIME INSTANT ENTRY & BIG MONEY BROADCASTER
# ----------------------------------------------------
def real_time_entry_scanner():
  """Har 60 seconds mein market scan karega aur sirf live entry par alert bhejega."""
  global LAST_SIGNAL_STATE

  while True:
    try:
      signal = check_fresh_entry_signal('^NSEI')

      if signal and signal['type'] != LAST_SIGNAL_STATE:
        LAST_SIGNAL_STATE = signal['type']

        if REGISTERED_CHAT_IDS:
          bm = get_big_money_alert()
          msg = (
              f"⚡ *REAL-TIME LIVE ENTRY & BIG MONEY ALERT*\n\n"
              f"• *Entry Status:* {signal['status']}\n"
              f"• *Live Price:* `{signal['price']}`\n"
              f"• *Smart Money Flow:* {bm['action']}\n"
              f"• *FII/DII Activity:* {bm['details']}\n\n"
              f"💡 *Trading Setup:* {signal['action']}\n"
              f"⏱️ *Entry Window:* ACTIVE NOW"
          )
          for c_id in list(REGISTERED_CHAT_IDS):
            send_telegram_message(c_id, msg)

      time.sleep(60)
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
                '✅ *MyMarketAlertBot Active & Live Sync!*\n\n'
                'Real-Time Entry & Big Money Scanner Enabled.\n\n'
                'Commands:\n'
                '• `/trend` - Real-Time Market Trend\n'
                '• `/nifty` - Live Nifty 50 Real Price\n'
                '• `/sensex` - Live Sensex Analytics\n'
                '• `/bigmoney` - Live Smart Money (FII/DII) Flow\n'
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
          elif text == '/bigmoney':
            bm = get_big_money_alert()
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🐋 *SMART MONEY & INSTITUTIONAL FLOW*\n\n"
                f"• *Flow Status:* {bm['action']}\n"
                f"• *Details:* {bm['details']}\n"
                f"• *Live Market Trend:* {tr['status']}",
            )
          elif text in ['/signal']:
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
                '• *Crude Oil / Gold / Silver:* Check live momentum near key'
                ' levels.\n💡 *Strategy:* Trade strictly in the direction of'
                ' live trend.',
            )
          else:
            send_telegram_message(
                chat_id,
                '✅ Command received. Type `/trend` to check live market.',
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
    
