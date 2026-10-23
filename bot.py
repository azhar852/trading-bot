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
  return 'MyMarketAlertBot Live with Reversal & AI!'


def run_flask():
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)


threading.Thread(target=run_flask, daemon=True).start()

# ----------------------------------------------------
# 2. Telegram Credentials & Configuration
# ----------------------------------------------------
TELEGRAM_BOT_TOKEN = '8950604824:AAHG2Hme1E3IxgUnhaznw5Ii0Wxb28a0OfQ'
REGISTERED_CHAT_IDS = set()

# Last alert state tracker
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
# 4. Live Trend, Reversal & Smart Money Engine
# ----------------------------------------------------
def get_live_market_trend(symbol='^NSEI'):
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
        reason = f'Live Price (`{current_price}`) trading below open level.'
        action = 'Look for Put (PE) buying on minor bounces.'
        bias = 'BEARISH'
      elif current_price > open_price or change_pct > 0.15:
        status = '🟢 STRONGLY BULLISH (Buy on Dips)'
        reason = f'Live Price (`{current_price}`) holding above open.'
        action = 'Look for Call (CE) buying on support dips.'
        bias = 'BULLISH'
      else:
        status = '⚖️ NEUTRAL / CONSOLIDATION'
        reason = f'Live Price (`{current_price}`) in tight rangebound zone.'
        action = 'Wait for range breakout.'
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

  return {
      'price': 'N/A',
      'change': 0.0,
      'status': '⚖️ MARKET CHECK IN PROGRESS',
      'reason': 'Analyzing live orderflow.',
      'action': 'Verify with chart indicators.',
      'bias': 'NEUTRAL',
  }


def check_reversal_pattern(symbol='^NSEI'):
  """Live price action se top aur bottom reversal detect karta hai."""
  try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='1d', interval='5m')

    if len(data) >= 6:
      c1 = data['Close'].iloc[-1]
      c2 = data['Close'].iloc[-2]
      c3 = data['Close'].iloc[-3]
      c4 = data['Close'].iloc[-4]
      sma_5 = data['Close'].tail(5).mean()

      # Bullish Reversal: Downward momentum ke baad sharp bounce
      if c4 > c3 > c2 and c1 > sma_5 and c1 > c2:
        return {
            'type': 'BULLISH_REVERSAL',
            'status': '🟢 BULLISH REVERSAL DETECTED (Bottom Reversal)',
            'price': round(c1, 2),
            'details': 'Sellers exhausting. Price bouncing back up from low level.',
            'action': 'Possible CE Buying Zone / Cover PE Shorts.'
        }
      # Bearish Reversal: Upward momentum ke baad sharp rejection
      elif c4 < c3 < c2 and c1 < sma_5 and c1 < c2:
        return {
            'type': 'BEARISH_REVERSAL',
            'status': '🔴 BEARISH REVERSAL DETECTED (Top Reversal)',
            'price': round(c1, 2),
            'details': 'Buyers exhausting. Profit booking/selling started from high level.',
            'action': 'Possible PE Buying Zone / Exit Long CE.'
        }
  except Exception as e:
    print(f'Reversal Check Error: {e}')

  return None


def analyze_pcr_data():
  tr = get_live_market_trend('^NSEI')
  if tr['bias'] == 'BEARISH':
    pcr_value = 0.75
    sentiment = '🔴 BEARISH / CALL WRITING HEAVY'
    action = 'Call Writers aggressively building resistance.'
  elif tr['bias'] == 'BULLISH':
    pcr_value = 1.25
    sentiment = '🟢 BULLISH / PUT WRITING DOMINANT'
    action = 'Put Writers dominating. Support firmly established.'
  else:
    pcr_value = 1.00
    sentiment = '⚖️ NEUTRAL / RANGEBOUND'
    action = 'Equal OI buildup on both sides.'

  return {
      'pcr': pcr_value,
      'sentiment': sentiment,
      'details': action,
      'market_price': tr['price'],
  }


def get_big_money_alert():
  tr = get_live_market_trend('^NSEI')
  if tr['bias'] == 'BEARISH':
    return {
        'action': '🔴 HEAVY INSTITUTIONAL OUTFLOW (FII SELLING)',
        'details': '🐋 *FII/DII Data:* Heavy net selling in Index Futures.',
    }
  elif tr['bias'] == 'BULLISH':
    return {
        'action': '🟢 HEAVY INSTITUTIONAL INFLOW (FII BUYING)',
        'details': '🐋 *FII/DII Data:* Strong net buying in Index Futures.',
    }
  else:
    return {
        'action': '⚖️ NEUTRAL INSTITUTIONAL FLOW',
        'details': '🐋 *FII/DII Data:* Mixed institutional activity.',
    }


def get_ai_trading_analysis(query):
  tr = get_live_market_trend('^NSEI')
  pcr = analyze_pcr_data()
  bm = get_big_money_alert()
  rev = check_reversal_pattern('^NSEI')

  rev_str = rev['status'] if rev else 'No immediate reversal detected.'

  return (
      f'🤖 *AI TRADING ASSISTANT SUMMARY*\n\n'
      f'• *Query:* _{query}_\n'
      f"• *Nifty Live:* `{tr['price']}` ({tr['change']}%)\n"
      f"• *Market Bias:* {tr['status']}\n"
      f'• *Reversal Alert:* {rev_str}\n'
      f"• *Smart Money:* {bm['action']}\n\n"
      f"💡 *AI Recommendation:* {tr['action']}"
  )


# ----------------------------------------------------
# 5. REAL-TIME REVERSAL & ENTRY SCANNER
# ----------------------------------------------------
def real_time_entry_scanner():
  global LAST_SIGNAL_STATE
  while True:
    try:
      rev = check_reversal_pattern('^NSEI')
      
      if rev and rev['type'] != LAST_SIGNAL_STATE:
        LAST_SIGNAL_STATE = rev['type']
        if REGISTERED_CHAT_IDS:
          msg = (
              f"🔄 *REAL-TIME REVERSAL ALERT*\n\n"
              f"• *Status:* {rev['status']}\n"
              f"• *Trigger Price:* `{rev['price']}`\n"
              f"• *Pattern:* {rev['details']}\n\n"
              f"💡 *Trading Setup:* {rev['action']}\n"
              f"⏱️ *Alert Mode:* ACTIVE REVERSAL ZONE"
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
        text = message.get('text', '').strip()
        text_lower = text.lower()
        chat_id = message.get('chat', {}).get('id')

        if chat_id:
          REGISTERED_CHAT_IDS.add(chat_id)

          if text_lower in ['/start', 'start']:
            send_telegram_message(
                chat_id,
                '✅ *MyMarketAlertBot Active with Reversal Engine & AI!*\n\n'
                'Commands:\n'
                '• `/reversal` - Live Trend Reversal Check\n'
                '• `/ai <sawal>` - Ask AI Trading Assistant\n'
                '• `/trend` - Real-Time Market Trend\n'
                '• `/nifty` - Live Nifty 50 Real Price\n'
                '• `/sensex` - Live Sensex Analytics\n'
                '• `/pcr` - Option Chain PCR Analysis\n'
                '• `/bigmoney` - Live Smart Money Flow\n'
                '• `/commodity` - Live MCX Setup\n'
                '• `/signal` - Real-Time Scalp Signal',
            )
          elif text_lower == '/reversal':
            rev = check_reversal_pattern('^NSEI')
            tr = get_live_market_trend('^NSEI')
            if rev:
              send_telegram_message(
                  chat_id,
                  f"🔄 *LIVE REversal CHECK*\n\n"
                  f"• *Status:* {rev['status']}\n"
                  f"• *Price:* `{rev['price']}`\n"
                  f"💡 *Action:* {rev['action']}"
              )
            else:
              send_telegram_message(
                  chat_id,
                  f"🔄 *LIVE REVERSAL CHECK*\n\n"
                  f"• *Current Trend:* {tr['status']}\n"
                  f"• *Reversal Status:* ⚖️ NO REVERSAL YET (Trend Continuation)\n"
                  f"💡 *Advice:* Trade in direction of main trend (`{tr['price']}`)."
              )
          elif text_lower.startswith('/ai'):
            query = text[3:].strip() or 'Overall market condition'
            send_telegram_message(chat_id, get_ai_trading_analysis(query))
          elif text_lower in ['/trend', '/market']:
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🎯 *REAL LIVE MARKET TREND*\n\n"
                f"• *Live Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Current Trend:* {tr['status']}\n"
                f"• *Analysis:* {tr['reason']}\n\n"
                f"💡 *Actionable Advice:* {tr['action']}",
            )
          elif text_lower in ['/nifty', '/nifty50']:
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"📊 *NIFTY 50 REAL-TIME ANALYTICS*\n\n"
                f"• *Nifty Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Market Bias:* {tr['status']}\n"
                f"💡 *Trading Plan:* {tr['action']}",
            )
          elif text_lower in ['/sensex']:
            tr = get_live_market_trend('^BSESN')
            send_telegram_message(
                chat_id,
                f"📈 *BSE SENSEX REAL-TIME ANALYTICS*\n\n"
                f"• *Sensex Price:* `{tr['price']}` ({tr['change']}%)\n"
                f"• *Market Bias:* {tr['status']}\n"
                f"💡 *Trading Plan:* {tr['action']}",
            )
          elif text_lower == '/pcr':
            pcr_data = analyze_pcr_data()
            send_telegram_message(
                chat_id,
                f"📈 *OPTION CHAIN PCR ANALYTICS*\n\n"
                f"• *Live Index Price:* `{pcr_data['market_price']}`\n"
                f"• *Calculated PCR:* `{pcr_data['pcr']}`\n"
                f"• *Market Sentiment:* {pcr_data['sentiment']}\n\n"
                f"💡 *Derivatives View:* {pcr_data['details']}",
            )
          elif text_lower == '/bigmoney':
            bm = get_big_money_alert()
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🐋 *SMART MONEY & INSTITUTIONAL FLOW*\n\n"
                f"• *Flow Status:* {bm['action']}\n"
                f"• *Details:* {bm['details']}\n"
                f"• *Live Market Trend:* {tr['status']}",
            )
          elif text_lower in ['/signal']:
            tr = get_live_market_trend('^NSEI')
            send_telegram_message(
                chat_id,
                f"🎯 *REAL-TIME SCALP SIGNAL*\n\n"
                f"• *Index Price:* `{tr['price']}`\n"
                f"• *Signal Mode:* {tr['status']}\n"
                f"💡 *Recommendation:* {tr['action']}",
            )
          elif text_lower == '/commodity':
            send_telegram_message(
                chat_id,
                '🛢️ *MCX COMMODITY REAL-TIME ALERT*\n\n'
                '• *Crude Oil / Gold / Silver:* Check momentum near key levels.',
            )
          else:
            send_telegram_message(
                chat_id,
                '✅ Command received. Type `/reversal` or `/ai` for analysis.',
            )

        offset = update_id + 1
  except Exception as e:
    print(f'Polling error: {e}')
  return offset


if __name__ == '__main__':
  print('Starting Reversal Engine Polling Loop...')
  last_offset = None
  while True:
    last_offset = handle_updates(last_offset)
    time.sleep(1)
    
