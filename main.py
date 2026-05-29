import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BASE_URL = "https://www.alphavantage.co/query"


class TradingEngine:
    def __init__(self):
        self.prices = []

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

    def moving_average(self, window):
        if len(self.prices) < window:
            return None
        return sum(self.prices[-window:]) / window

    def analyze(self, price):
        if price is None:
            return "NO TRADE", 0, ["No data"]

        self.prices.append(price)

        score = 50
        reasons = []

        # keep memory small
        if len(self.prices) > 50:
            self.prices.pop(0)

        ma_fast = self.moving_average(5)
        ma_slow = self.moving_average(15)

        # trend detection
        if ma_fast and ma_slow:
            if ma_fast > ma_slow:
                score += 20
                reasons.append("Uptrend detected (MA crossover)")
            elif ma_fast < ma_slow:
                score += 20
                reasons.append("Downtrend detected (MA crossover)")

        # momentum
        if len(self.prices) > 2:
            momentum = price - self.prices[-2]

            if abs(momentum) > 0.002:
                score += 10
                reasons.append("Strong momentum detected")

        # zone logic (lightweight now)
        if price > 1.10:
            score += 10
            reasons.append("Upper price region")

        elif price < 1.08:
            score += 10
            reasons.append("Lower price region")

        score = max(0, min(100, score))

        signal = "TRADE READY" if score >= 75 else "NO TRADE"

        return signal, score, reasons

    def run(self):
        print("AMIES PHASE 3 STRATEGY ENGINE ONLINE")

        while True:
            price = self.fetch_price()
            signal, score, reasons = self.analyze(price)

            print("\n--------------------")
            print("PRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            for r in reasons:
                print("REASON:", r)

            time.sleep(20)


engine = TradingEngine()
engine.run()
