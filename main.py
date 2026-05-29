import requests
import time

API_KEY = "2UFIT1549JNPNLPY"

def get_price():
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={API_KEY}"
    data = requests.get(url).json()
    
    price = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    return price

def strategy(price):
    if price > 1.10:
        return "SELL", "High zone detected"
    elif price < 1.08:
        return "BUY", "Low zone detected"
    return "NO TRADE", "Neutral zone"

print("REAL MARKET BOT STARTED")

for i in range(20):
    price = get_price()
    signal, reason = strategy(price)

    print("PRICE:", price)
    print("SIGNAL:", signal)
    print("REASON:", reason)

    time.sleep(10)
