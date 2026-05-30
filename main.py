import requests
import time
import os
import psycopg2

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"

class PaperTradingBot:

    def __init__(self):

        self.prices = []

        self.open_trade = None

        self.balance = 1000

        self.trade_log = []

    # ---------------- TELEGRAM ----------------

    def send_alert(self, message):

        try:

            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            requests.post(url, data={

                "chat_id": CHAT_ID,

                "text": message

            })

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

    # ---------------- RSI ----------------

    def rsi(self):

        if len(self.prices) < 10:

            return 50

        gains, losses = 0, 0

        for i in range(-10, -1):

            diff = self.prices[i] - self.prices[i - 1]

            if diff > 0:

                gains += diff

            else:

                losses += abs(diff)

        if losses == 0:

            return 100

        rs = gains / losses

        return 100 - (100 / (1 + rs))

    # ---------------- SIGNAL ----------------

    def analyze(self, price):

        self.prices.append(price)

        if len(self.prices) > 50:

            self.prices.pop(0)

        score = 50

        reasons = []

        if len(self.prices) > 5:

            if self.prices[-1] > self.prices[-5]:

                score += 20

                reasons.append("Uptrend")

            else:

                score += 20

                reasons.append("Downtrend")

        rsi = self.rsi()

        reasons.append(f"RSI {round(rsi,2)}")

        if rsi > 70:

            score -= 20

        elif rsi < 30:

            score -= 20

        score = max(0, min(100, score))

        if score < 75:

            return "NO TRADE", score, reasons

        signal = "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

        return signal, score, reasons

    # ---------------- TRADE ENGINE ----------------

    def open_trade_fn(self, signal, price):

        self.open_trade = {

            "signal": signal,

            "entry": price,

            "time": time.time()

        }

        msg = f"OPENED {signal} @ {price}"

        self.send_alert(msg)

    def close_trade(self, price):

        trade = self.open_trade

        self.open_trade = None

        entry = trade["entry"]

        signal = trade["signal"]

        if signal == "BUY":

            pnl = price - entry

        else:

            pnl = entry - price

        self.balance += pnl

        result = "WIN" if pnl > 0 else "LOSS"

        log = {

            "entry": entry,

            "exit": price,

            "pnl": pnl,

            "result": result,

            "balance": self.balance

        }

        self.trade_log.append(log)

        msg = f"""

CLOSED TRADE

Result: {result}

PnL: {round(pnl,5)}

Balance: {round(self.balance,2)}

"""

        self.send_alert(msg)

    # ---------------- LOOP ----------------

    def run(self):

        print("PAPER TRADING ACTIVE")

        while True:

            price = self.get_price()

            if price is None:

                time.sleep(5)

                continue

            signal, score, reasons = self.analyze(price)

            print("\nPRICE:", price)

            print("SIGNAL:", signal)

            print("BALANCE:", self.balance)

            # open trade

            if self.open_trade is None and signal != "NO TRADE":

                self.open_trade_fn(signal, price)

            # close trade after small move or time

            elif self.open_trade is not None:

                entry_time = self.open_trade["time"]

                if time.time() - entry_time > 60:  # 1 min trade cycle

                    self.close_trade(price)

            time.sleep(10)

bot = PaperTradingBot()
bot.run()