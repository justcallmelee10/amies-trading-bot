import requests
import time
API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"


class AlertTradingBot:
    def __init__(self):
        self.prices = []

    def send_alert(self, message):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": CHAT_ID,
                "text": message
            })
        except:
            print("Telegram alert failed")

    def get_price(self):
        try:
            r = requests.get(BASE_URL, params={
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": "EUR",
                "to_currency": "USD",
                "apikey": API_KEY
            }, timeout=10)

            data = r.json()

            if "Realtime Currency Exchange Rate" not in data:
                return None

            return float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])

        except:
            return None

    def analyze(self, price):
        if price is None:
            return "NO TRADE", 0, "No data"

        self.prices.append(price)
        if len(self.prices) > 50:
            self.prices.pop(0)

        score = 50
        reason = []

        if len(self.prices) > 5:
            if self.prices[-1] > self.prices[-5]:
                score += 20
                reason.append("Uptrend detected")
            else:
                score += 20
                reason.append("Downtrend detected")

        if price > 1.10:
            score += 10
            reason.append("Upper zone")

        elif price < 1.08:
            score += 10
            reason.append("Lower zone")

        score = max(0, min(100, score))

        if score < 75:
            return "NO TRADE", score, reason

        signal = "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

        return signal, score, reason

    def run(self):
        print("TELEGRAM ALERT BOT ONLINE")

        while True:
            price = self.get_price()
            signal, score, reasons = self.analyze(price)

            print(price, signal, score)

            if signal != "NO TRADE":
                msg = f"""
📊 TRADE SIGNAL

PAIR: EUR/USD
SIGNAL: {signal}
PRICE: {price}
CONFIDENCE: {score}

REASONS:
{chr(10).join(reasons)}
"""
                self.send_alert(msg)

            time.sleep(20)


bot = AlertTradingBot()
bot.run()
