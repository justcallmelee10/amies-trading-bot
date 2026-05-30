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

    # ---------------- SIGNAL ----------------

    def signal(self, price):

        self.prices.append(price)

        if len(self.prices) > 50:

            self.prices.pop(0)

        if len(self.prices) < 6:

            return "NO TRADE"

        if self.prices[-1] > self.prices[-5]:

            return "BUY"

        else:

            return "SELL"

    # ---------------- TRADE OPEN ----------------

    def open(self, signal, price):

        self.open_trade = {

            "type": signal,

            "entry": price,

            "time": time.time()

        }

        self.send(f"📥 OPEN {signal} @ {price}")

    # ---------------- TRADE CLOSE ----------------

    def close(self, price):

        t = self.open_trade

        self.open_trade = None

        entry = t["entry"]

        side = t["type"]

        pnl = (price - entry) if side == "BUY" else (entry - price)

        self.balance += pnl

        self.trade_log.append(pnl)

        result = "WIN" if pnl > 0 else "LOSS"

        self.send(f"""

📤 CLOSE TRADE

Result: {result}

PnL: {round(pnl,5)}

Balance: {round(self.balance,2)}

""")

    # ---------------- STATS ----------------

    def stats(self):

        total = len(self.trade_log)

        if total == 0:

            return

        wins = len([x for x in self.trade_log if x > 0])

        winrate = (wins / total) * 100

        self.send(f"""

📊 STATS UPDATE

Trades: {total}

Winrate: {round(winrate,2)}%

Balance: {round(self.balance,2)}

""")

    # ---------------- LOOP ----------------

    def run(self):

        print("PAPER BOT RUNNING")

        last_stats = time.time()

        while True:

            price = self.get_price()

            if price is None:

                time.sleep(5)

                continue

            sig = self.signal(price)

            print("PRICE:", price, "SIGNAL:", sig)

            # open trade

            if self.open_trade is None and sig != "NO TRADE":

                self.open(sig, price)

            # close trade after 60 seconds

            elif self.open_trade is not None:

                if time.time() - self.open_trade["time"] > 60:

                    self.close(price)

            # stats every 5 minutes

            if time.time() - last_stats > 300:

                self.stats()

                last_stats = time.time()

            time.sleep(10)

bot = PaperBot()
bot.run()