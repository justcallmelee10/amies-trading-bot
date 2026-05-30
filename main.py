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

    # ---------------- SIGNAL ENGINE ----------------

    def signal(self, price):

        self.prices.append(price)

        if len(self.prices) > 50:

            self.prices.pop(0)

        if len(self.prices) < 6:

            return "NO TRADE"

        # volatility filter

        recent_range = max(self.prices[-5:]) - min(self.prices[-5:])

        if recent_range < 0.0010:

            return "NO TRADE"

        score = 50

        # trend

        if self.prices[-1] > self.prices[-5]:

            score += 25

        else:

            score += 25

        # momentum

        change = self.prices[-1] - self.prices[-2]

        if change > 0:

            score += 10

        else:

            score += 10

        # threshold (more active than before)

        if score < 65:

            return "NO TRADE"

        return "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

    # ---------------- OPEN TRADE ----------------

    def open_trade_fn(self, signal, price):

        self.open_trade = {

            "type": signal,

            "entry": price,

            "time": time.time()

        }

        self.send(f"📥 OPEN {signal} @ {price}")

    # ---------------- CLOSE TRADE ----------------

    def close_trade(self, price):

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

        total_pnl = sum(self.trade_log)

        self.send(f"""

📊 STATS

Trades: {total}

Winrate: {round(winrate,2)}%

PnL: {round(total_pnl,4)}

Balance: {round(self.balance,2)}

""")

    # ---------------- MAIN LOOP ----------------

    def run(self):

        print("BOT RUNNING")

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

                self.open_trade_fn(sig, price)

            # close after 60 sec

            elif self.open_trade is not None:

                if time.time() - self.open_trade["time"] > 60:

                    self.close_trade(price)

            # stats every 5 min

            if time.time() - last_stats > 300:

                self.stats()

                last_stats = time.time()

            time.sleep(10)

bot = PaperBot()
bot.run()