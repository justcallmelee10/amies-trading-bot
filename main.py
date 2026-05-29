import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BASE_URL = "https://www.alphavantage.co/query"

def get_price():
    try:
        response = requests.get(BASE_URL, params={
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": "EUR",
            "to_currency": "USD",
            "apikey": API_KEY
        }, timeout=10)

        data = response.json()

        if not isinstance(data, dict):
            print("Bad response format")
            return None

        if "Note" in data:
            print("API limit hit - waiting")
            return None

        rate_block = data.get("Realtime Currency Exchange Rate")
        if not rate_block:
            print("No market data")
            return None

        return float(rate_block.get("5. Exchange Rate"))

    except Exception as e:
        print("Safe error:", e)
        return None


def strategy(price):
    if price is None:
        return "NO TRADE", ["Waiting for data"]

    if price > 1.10:
        return "SELL", ["Resistance zone detected"]

    if price < 1.08:
        return "BUY", ["Support zone detected"]

    return "NO TRADE", ["Neutral market"]


print("AMIES BOT STARTED (STABLE SERVICE MODE)")

while True:
    price = get_price()
    signal, reasons = strategy(price)

    print("\n---")
    print("PRICE:", price)
    print("SIGNAL:", signal)

    for r in reasons:
        print("REASON:", r)

    time.sleep(20)
