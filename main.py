import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BASE_URL = "https://www.alphavantage.co/query"


class MarketBot:
    def __init__(self):
        self.last_price = None

    def fetch_price(self):
        try:
            response = requests.get(BASE_URL, params={
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": "EUR",
                "to_currency": "USD",
                "apikey": API_KEY
            }, timeout=10)

            data = response.json()

            if "Realtime Currency Exchange Rate" not in data:
                return None

            return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

        except:
            return None

    def analyze(self, price):
        if price is None:
            return "NO TRADE", 0, ["No valid market data"]

        score = 50
        reasons = []

        # trend zones (simple structure logic)
        if price > 1.10:
            score += 25
            reasons.append("Upper zone pressure (possible sell area)")

        elif price < 1.08:
            score += 25
            reasons.append("Lower zone pressure (possible buy area)")

        else:
            score -= 10
            reasons.append("Neutral market zone")

        # volatility awareness (simple momentum proxy)
        if self.last_price:
            change = abs(price - self.last_price)
            if change > 0.002:
                score += 10
                reasons.append("Active volatility detected")

        self.last_price = price

        score = max(0, min(100, score))

        signal = "TRADE READY" if score >= 70 else "NO TRADE"

        return signal, score, reasons

    def run(self):
        print("AMIES FINAL CORE ENGINE STARTED")

        while True:
            price = self.fetch_price()
            signal, score, reasons = self.analyze(price)

            print("\n----------------------")
            print("PRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            for r in reasons:
                print("REASON:", r)

            time.sleep(20)


bot = MarketBot()
bot.run()
