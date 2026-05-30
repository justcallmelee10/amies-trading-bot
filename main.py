import requests
import time
import os
import psycopg2

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"

class PaperBot:

    def __init__(self):

        self.prices = []

        self.balance = 1000

        self.open_trade = None

        self.trade_log = []

        self.last_trade_time = 0

        self.cooldown = 90

        self.last_direction = None

    # ---------------- TELEGRAM ----------------

    def send(self, msg):

        try:

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

        except:

            pass

    # ---------------- PRICE ----------------

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

    # ---------------- SIGNAL (OBSERVABLE VERSION) ----------------

    def signal(self, price):

        self.prices.append(price)

        if len(self.prices) > 80:

            self.prices.pop(0)

        if len(self.prices) < 15:

            return {

                "signal": "NO TRADE",

                "reason": "INSUFFICIENT DATA",

                "volatility": 0

            }

        short = self.prices[-3:]

        mid = self.prices[-8:]

        short_trend = short[-1] - short[0]

        mid_trend = mid[-1] - mid[0]

        volatility = max(mid) - min(mid)

        avg = sum(mid) / len(mid)

        threshold = avg * 0.00025

        # ---------------- FILTER 1 ----------------

        if volatility < threshold:

            return {

                "signal": "NO TRADE",

                "reason": "LOW VOLATILITY (FLAT MARKET)",

                "volatility": volatility

            }

        # ---------------- FILTER 2 ----------------

        if short_trend > 0 and mid_trend > 0:

            return {

                "signal": "BUY",

                "reason": "MOMENTUM UP (SHORT + MID ALIGN)",

                "volatility": volatility

            }

        if short_trend < 0 and mid_trend < 0:

            return {

                "signal": "SELL",

                "reason": "MOMENTUM DOWN (SHORT + MID ALIGN)",

                "volatility": volatility

            }

        # ---------------- FILTER 3 ----------------

        return {

            "signal": "NO TRADE",

            "reason": "CHOPPY / NO CLEAR TREND",

            "volatility": volatility

        }

    # ---------------- CAN TRADE ----------------

    def can_trade(self, signal):

        now = time.time()

        if now - self.last_trade_time < self.cooldown:

            return False

        if signal == self.last_direction:

            return False

        return True

    # ---------------- OPEN TRADE ----------------

    def open_trade_fn(self, signal, price):

        sl = price - 0.0010 if signal == "BUY" else price + 0.0010

        tp = price + 0.0020 if signal == "BUY" else price - 0.0020

        self.open_trade = {

            "type": signal,

            "entry": price,

            "sl": sl,

            "tp": tp,

            "time": time.time()

        }

        self.last_trade_time = time.time()

        self.last_direction = signal

        self.send(f"""

📥 OPEN {signal}

Entry: {price}

SL: {sl}

TP: {tp}

""")

    # ---------------- CLOSE TRADE ----------------

    def close_trade(self, price):

        t = self.open_trade

        self.open_trade = None

        entry = t["entry"]

        sl = t["sl"]

        tp = t["tp"]

        side = t["type"]

        if side == "BUY":

            if price <= sl:

                pnl = -abs(entry - sl)

                result = "STOP LOSS"

            elif price >= tp:

                pnl = abs(tp - entry)

                result = "TAKE PROFIT"

            else:

                pnl = price - entry

                result = "TIME EXIT"

        else:

            if price >= sl:

                pnl = -abs(sl - entry)

                result = "STOP LOSS"

            elif price <= tp:

                pnl = abs(entry - tp)

                result = "TAKE PROFIT"

            else:

                pnl = entry - price

                result = "TIME EXIT"

        self.balance += pnl

        self.trade_log.append(pnl)

        self.send(f"""

📤 CLOSE ({result})

PnL: {round(pnl,5)}

Balance: {round(self.balance,2)}

""")

    # ---------------- MAIN LOOP (OBSERVABLE LOGS) ----------------

    def run(self):

        print("BOT RUNNING (OBSERVABLE MODE)")

        while True:

            price = self.get_price()

            if price is None:

                time.sleep(5)

                continue

            result = self.signal(price)

            sig = result["signal"]

            reason = result["reason"]

            vol = result["volatility"]

            print(f"""

PRICE: {price}

SIGNAL: {sig}

REASON: {reason}

VOLATILITY: {vol}

--------------------

""")

            if self.open_trade is None:

                if sig != "NO TRADE" and self.can_trade(sig):

                    self.open_trade_fn(sig, price)

            else:

                self.close_trade(price)

            time.sleep(5)

bot = PaperBot()
bot.run()