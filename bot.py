# UKHAHLAMBA VIEW - ONE CODE - REAL AUTO BOT
# Headway + Deriv | Flick Entry | H2
# Paste this as ONE file: bot.py
import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# === YOUR TOKENS - PUT IN RENDER > ENVIRONMENT, NOT HERE ===
METAAPI_TOKEN = os.environ.get("METAAPI_TOKEN", "")
METAAPI_ACCOUNT = os.environ.get("METAAPI_ACCOUNT", "")
DERIV_TOKEN = os.environ.get("DERIV_TOKEN", "")
LOT = 0.01

# === SYMBOL MAP - TradingView -> Broker ===
MAP = {
    "EURUSD": ("EURUSD", "frxEURUSD"),
    "GBPUSD": ("GBPUSD", "frxGBPUSD"),
    "XAUUSD": ("XAUUSD", "frxXAUUSD"),
    "Volatility 75 Index": (None, "R_75"),
    "Volatility 100 Index": (None, "R_100"),
    "Boom 1000 Index": (None, "BOOM1000"),
    "Crash 1000 Index": (None, "CRASH1000"),
    "Boom 500 Index": (None, "BOOM500"),
    "Crash 500 Index": (None, "CRASH500"),
}

def headway_trade(symbol, action):
    if not METAAPI_TOKEN:
        print(f"[HEADWAY TEST] {action} {symbol} {LOT} - Add token to go LIVE")
        return
    url = f"https://mt-client-api-v1.agiliumtrade.ai/users/current/accounts/{METAAPI_ACCOUNT}/trade"
    headers = {"auth-token": METAAPI_TOKEN, "Content-Type": "application/json"}
    side = "BUY" if action == "BUY" else "SELL"
    payload = {"symbol": symbol, "volume": LOT, "actionType": "ORDER_TYPE_MARKET", "type": f"ORDER_TYPE_{side}"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"[HEADWAY REAL] {side} {symbol} {LOT} -> {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"[HEADWAY ERROR] {e}")

def deriv_trade(symbol, action):
    if not DERIV_TOKEN:
        print(f"[DERIV TEST] {action} {symbol} - Add token to go LIVE")
        return
    # Deriv API via websocket - simplified live buy
    try:
        import websocket
        ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089", timeout=10)
        ws.send(json.dumps({"authorize": DERIV_TOKEN}))
        ws.recv()
        contract = "CALL" if action == "BUY" else "PUT"
        ws.send(json.dumps({"buy": 1, "price": 10, "parameters": {"amount": 10, "basis": "stake", "contract_type": contract, "currency": "USD", "duration": 5, "duration_unit": "t", "symbol": symbol}}))
        res = ws.recv()
        print(f"[DERIV REAL] {action} {symbol} -> {res[:200]}")
        ws.close()
    except Exception as e:
        print(f"[DERIV ERROR] {e}")

@app.route('/')
def home():
    return "UKHAHLAMBA BOT LIVE - Ready for Flick"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    action = str(data.get('action','')).upper()
    symbol = data.get('symbol','EURUSD')
    print(f"FLICK IN: {action} {symbol}")
    headway_sym, deriv_sym = MAP.get(symbol, (symbol, symbol))
    if headway_sym:
        headway_trade(headway_sym, action)
    if deriv_sym:
        deriv_trade(deriv_sym, action)
    return jsonify({"status": "OK", "action": action, "symbol": symbol})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
