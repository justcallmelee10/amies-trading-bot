import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BASE_URL = "https://www.alphavantage.co/query"


class RiskTradingEngine:
    def __init__(self):
        self.prices = []

        # risk settings (VERY IMPORTANT)
        self.account_balance = 1000  # demo assumption
        self.risk_per_trade = 0.02   # 2% risk max

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

    def calculate_position_size(self):
        # simple risk model
        risk_amount = self.account_balance * self.risk_per_trade
        return round(risk_amount, 2)

    def analyze(self, price):
        if price is None:
            return "NO TRADE", 0, None, None, ["No market data"]

        self.prices.append(price)
        if len(self.prices) > 50:
            self.prices.pop(0)

        score = 50
        reasons = []

        ma_fast = self.moving_average(5)
        ma_slow = self.moving_average(15)

        if ma_fast and ma_slow:
            if ma_fast > ma_slow:
                score += 20
                reasons.append("Uptrend detected")
            else:
                score += 20
                reasons.append("Downtrend detected")

        # volatility check
        if len(self.prices) > 2:
            momentum = abs(price - self.prices[-2])
            if momentum > 0.002:
                score += 10
                reasons.append("High momentum detected")

        # market zone logic
        if price > 1.10:
            score += 10
            reasons.append("Upper zone")

        elif price < 1.08:
            score += 10
            reasons.append("Lower zone")

        score = max(0, min(100, score))

        # risk filter (IMPORTANT)
        if score < 75:
            return "NO TRADE", score, None, None, reasons

        # trade decision
        direction = "BUY" if ma_fast and ma_fast > ma_slow else "SELL"

        position_size = self.calculate_position_size()

        # fake SL/TP (for structure only)
        stop_loss = price - 0.002 if direction == "BUY" else price + 0.002
        take_profit = price + 0.004 if direction == "BUY" else price - 0.004

        return direction, score, position_size, (stop_loss, take_profit), reasons

    def run(self):
        print("AMIES RISK ENGINE ONLINE")

        while True:
            price = self.fetch_price()
            signal, score, size, levels, reasons = self.analyze(price)

            print("\n--------------------")
            print("PRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            if signal != "NO TRADE":
                print("POSITION SIZE:", size)
                print("SL/TP:", levels)

            for r in reasons:
                print("REASON:", r)

            time.sleep(20)


engine = RiskTradingEngine()
engine.run()
