import requests
import time

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"


class TradingBot:

    def __init__(self):
        self.prices = []

        # cooldown system
        self.last_signal = None
        self.last_alert_time = 0

        # 15 minutes cooldown
        self.cooldown_seconds = 900

    def send_alert(self, message):

        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            response = requests.post(url, data={
                "chat_id": CHAT_ID,
                "text": message
            })

            print("TELEGRAM:", response.status_code)

        except Exception as e:
            print("TELEGRAM ERROR:", e)

    def get_price(self):

        try:
            response = requests.get(BASE_URL, params={
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": "EUR",
                "to_currency": "USD",
                "apikey": API_KEY
            }, timeout=10)

            data = response.json()

            block = data.get("Realtime Currency Exchange Rate")

            if not block:
                return None

            return float(block["5. Exchange Rate"])

        except Exception as e:
            print("PRICE ERROR:", e)
            return None

    def analyze(self, price):

        if price is None:
            return "NO TRADE", 0, ["No data"]

        self.prices.append(price)

        if len(self.prices) > 50:
            self.prices.pop(0)

        score = 50
        reasons = []

        # trend
        if len(self.prices) > 5:

            if self.prices[-1] > self.prices[-5]:
                score += 20
                reasons.append("Uptrend")

            else:
                score += 20
                reasons.append("Downtrend")

        # zones
        if price > 1.10:
            score += 10
            reasons.append("Upper zone")

        elif price < 1.08:
            score += 10
            reasons.append("Lower zone")

        score = max(0, min(100, score))

        if score < 75:
            return "NO TRADE", score, reasons

        signal = "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

        return signal, score, reasons

    def can_send_signal(self, signal):

        now = time.time()

        # cooldown active
        if signal == self.last_signal:
            if now - self.last_alert_time < self.cooldown_seconds:
                return False

        return True

    def run(self):

        print("COOLDOWN BOT ONLINE")

        while True:

            price = self.get_price()

            signal, score, reasons = self.analyze(price)

            print("\nPRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            if signal != "NO TRADE":

                if self.can_send_signal(signal):

                    message = f"""
📊 TRADE SIGNAL

PAIR: EUR/USD
SIGNAL: {signal}
PRICE: {price}
CONFIDENCE: {score}

REASONS:
{chr(10).join(reasons)}
"""

                    self.send_alert(message)

                    self.last_signal = signal
                    self.last_alert_time = time.time()

                else:
                    print("⏳ SIGNAL COOLDOWN ACTIVE")

            time.sleep(20)


bot = TradingBot()
bot.run()