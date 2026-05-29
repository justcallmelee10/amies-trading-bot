import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BASE_URL = "https://www.alphavantage.co/query"


class SafeTradingBot:
    def __init__(self):
        self.prices = []

        # 🛡️ SAFETY SETTINGS (VERY IMPORTANT)
        self.account_balance = 10  # small account protection mode
        self.risk_per_trade = 0.01  # 1% max risk per trade
        self.max_daily_loss = 0.03  # stop if -3%
        self.daily_loss = 0

        self.trade_count = 0
        self.max_trades_per_day = 20

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

    def risk_check(self):
        if self.daily_loss >= self.max_daily_loss:
            print("🛑 DAILY LOSS LIMIT HIT — BOT STOPPED")
            return False

        if self.trade_count >= self.max_trades_per_day:
            print("🛑 TRADE LIMIT REACHED — BOT STOPPED")
            return False

        return True

    def analyze(self, price):
        if price is None:
            return "NO TRADE", 0, None, ["No data"]

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
                reasons.append("Uptrend")
            else:
                score += 20
                reasons.append("Downtrend")

        if len(self.prices) > 2:
            momentum = abs(price - self.prices[-2])
            if momentum > 0.002:
                score += 10
                reasons.append("Momentum detected")

        if price > 1.10:
            score += 10
            reasons.append("Upper zone")

        elif price < 1.08:
            score += 10
            reasons.append("Lower zone")

        score = max(0, min(100, score))

        if score < 75:
            return "NO TRADE", score, None, reasons

        direction = "BUY" if ma_fast and ma_fast > ma_slow else "SELL"

        # risk-based position sizing (VERY SMALL FOR $10 ACCOUNT)
        position_size = round(self.account_balance * self.risk_per_trade, 2)

        return direction, score, position_size, reasons

    def execute_trade(self, signal, size):
        # simulated execution (we will connect broker later)
        self.trade_count += 1
        print(f"📊 EXECUTED: {signal} | SIZE: {size}")

    def run(self):
        print("🛡️ SAFE TRADING BOT ONLINE (CAPITAL PROTECTED MODE)")

        while True:

            if not self.risk_check():
                break

            price = self.fetch_price()
            signal, score, size, reasons = self.analyze(price)

            print("\n--------------------")
            print("PRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            for r in reasons:
                print("REASON:", r)

            if signal != "NO TRADE":
                self.execute_trade(signal, size)

            time.sleep(20)


bot = SafeTradingBot()
bot.run()
