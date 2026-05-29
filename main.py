import requests
import time

API_KEY = "2UFIT1549JNPNLPY"

BASE_URL = "https://www.alphavantage.co/query"

def get_price():
    try:
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "EUR",
            "to_currency": "USD",
            "apikey": API_KEY
        }

        response = requests.get(BASE_URL, params=params, timeout=10)

        # handle HTTP errors
        if response.status_code != 200:
            print("HTTP ERROR:", response.status_code)
            return None

        data = response.json()

        # handle API limits / missing data safely
        if not isinstance(data, dict):
            print("INVALID RESPONSE FORMAT")
            return None

        if "Note" in data:
            print("API LIMIT REACHED - WAITING")
            return None

        rate_block = data.get("Realtime Currency Exchange Rate")
        if not rate_block:
            print("NO RATE DATA")
            return None

        price = rate_block.get("5. Exchange Rate")
        if not price:
            print("NO PRICE VALUE")
            return None

        return float(price)

    except Exception as e:
        print("ERROR SAFE HANDLED:", str(e))
        return None


def strategy(price):
    if price is None:
        return "NO TRADE", ["Waiting for valid market data"]

    reasons = []

    if price > 1.10:
        reasons.append("Price in upper zone (possible resistance)")
        return "SELL", reasons

    if price < 1.08:
        reasons.append("Price in lower zone (possible support)")
        return "BUY", reasons

    reasons.append("Market in neutral range")
    return "NO TRADE", reasons


print("AMIES STABLE TRADING BOT ONLINE")

while True:
    price = get_price()

    signal, reasons = strategy(price)

    print("\n--------------------")
    print("PRICE:", price)
    print("SIGNAL:", signal)

    for r in reasons:
        print("REASON:", r)

    time.sleep(20)
