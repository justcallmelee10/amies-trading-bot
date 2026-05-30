import requests
import time
import os
import psycopg2

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"

class TradingBot:

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

            pass

    def get_price(self):

        try:

            r = requests.get(BASE_URL, params={

                "function": "CURRENCY_EXCHANGE_RATE",

                "from_currency": "EUR",

                "to_currency": "USD",

                "apikey": API_KEY

            }, timeout=10)

            data = r.json()

            block = data.get("Realtime Currency Exchange Rate")

            if not block:

                return None

            return float(block["5. Exchange Rate"])

        except:

            return None

    # ---------------------------

    # RSI CALCULATION

    # ---------------------------

    def calculate_rsi(self, period=10):

        if len(self.prices) < period + 1:

            return 50  # neutral default

        gains = 0

        losses = 0

        for i in range(-period, -1):

            change = self.prices[i] - self.prices[i - 1]

            if change > 0:

                gains += change

            else:

                losses += abs(change)

        if losses == 0:

            return 100

        rs = gains / losses

        rsi = 100 - (100 / (1 + rs))

        return rsi

    def analyze(self, price):

        if price is None:

            return "NO TRADE", 0, []

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

        # RSI filter

        rsi = self.calculate_rsi()

        reasons.append(f"RSI: {round(rsi,2)}")

        if rsi > 70:

            score -= 25

            reasons.append("Overbought - avoid BUY")

        elif rsi < 30:

            score -= 25

            reasons.append("Oversold - avoid SELL")

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

    def run(self):

        print("RSI BOT ONLINE")

        while True:

            price = self.get_price()

            signal, score, reasons = self.analyze(price)

            print("\nPRICE:", price)

            print("SIGNAL:", signal)

            print("CONFIDENCE:", score)

            if signal != "NO TRADE":

                msg = f"""

📊 SIGNAL

EUR/USD

{signal}

Price: {price}

Confidence: {score}

{chr(10).join(reasons)}

"""

                self.send_alert(msg)

            time.sleep(20)

bot = TradingBot()
bot.run()