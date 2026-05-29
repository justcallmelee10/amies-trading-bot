import time
import random

def get_market_data():
    # fake market simulation for now (we upgrade later to real forex feed)
    return {
        "price": round(random.uniform(1.05, 1.15), 5)
    }

def strategy(price):
    if price > 1.10:
        return "SELL", "Price above threshold (overbought zone)"
    elif price < 1.08:
        return "BUY", "Price below threshold (value zone)"
    else:
        return "NO TRADE", "Market neutral"

while True:
    data = get_market_data()
    signal, reason = strategy(data["price"])

    print("PRICE:", data["price"])
    print("SIGNAL:", signal)
    print("REASON:", reason)

    time.sleep(5)
