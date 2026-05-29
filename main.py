import requests
import time

# =========================
# CONFIG (FILL THESE)
# =========================

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"


# =========================
# BOT CORE
# =========================

class TradingBot:

    def __init__(self):
        self.prices = []

    # -------------------------
    # TELEGRAM ALERT SYSTEM
    # -------------------------
    def send_alert(self, message):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            response = requests.post(url, data={
                "chat_id": CHAT_ID,
                "text": message
            }, timeout=10)

            # DEBUG OUTPUT (IMPORTANT)
            print("📩 TELEGRAM STATUS:", response.status_code)
            print("📩 TELEGRAM RESPONSE:", response.text)

        except Exception as e:
            print("❌ TELEGRAM ERROR:", e)

    # -------------------------
    # GET MARKET PRICE
    # -------------------------
    def get_price(self):
        try:
            response = requests.get(BASE_URL, params={
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": "EUR",
                "to_currency": "USD",
                "apikey": API_KEY
            }, timeout=10)

            data = response.json()

            if "Note" in data:
                print("⏳ API LIMIT HIT")
                return None

            block = data.get("Realtime Currency Exchange Rate")
            if not block:
                print("⚠️ NO MARKET DATA")
                return None

            return float(block["5. Exchange Rate"])

        except Exception as e:
            print("❌ PRICE ERROR:", e)
            return None

    # -------------------------
    # STRATEGY ENGINE
    # -------------------------
    def analyze(self, price):

        if price is None:
            return "NO TRADE", 0, ["No data"]

        self.prices.append(price)

        if len(self.prices) > 50:
            self.prices.pop(0)

        score = 50
        reasons = []

        # trend logic (simple but stable)
        if len(self.prices) > 5:
            if self.prices[-1] > self.prices[-5]:
                score += 20
                reasons.append("Uptrend detected")
            else:
                score += 20
                reasons.append("Downtrend detected")

        # zone logic
        if price > 1.10:
            score += 10
            reasons.append("Upper zone")

        elif price < 1.08:
            score += 10
            reasons.append("Lower zone")

        # clamp score
        score = max(0, min(100, score))

        if score < 75:
            return "NO TRADE", score, reasons

        signal = "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

        return signal, score, reasons

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def run(self):
        print("🚀 TELEGRAM TRADING BOT STARTED")

        while True:

            price = self.get_price()
            signal, score, reasons = self.analyze(price)

            print("\n----------------------")
            print("PRICE:", price)
            print("SIGNAL:", signal)
            print("CONFIDENCE:", score)

            for r in reasons:
                print("REASON:", r)

            # SEND ALERT ONLY ON TRADE
            if signal != "NO TRADE":
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

            time.sleep(20)


# =========================
# START BOT
# =========================

bot = TradingBot()
bot.run()
