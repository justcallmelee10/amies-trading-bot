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

        # trading control

        self.last_trade_time = 0

        self.cooldown = 120

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

    # ---------------- SIGNAL ----------------

    def signal(self, price):

        self.prices.append(price)

        if len(self.prices) > 50:

            self.prices.pop(0)

        if len(self.prices) < 10:

            return "NO TRADE"

        # volatility filter

        recent_range = max(self.prices[-10:]) - min(self.prices[-10:])

        if recent_range < 0.0015:

            return "NO TRADE"

        # trend logic

        if self.prices[-1] > self.prices[-8]:

            return "BUY"

        else:

            return "SELL"

    # ---------------- TRADE RULES ----------------

    def can_trade(self, signal):

        now = time.time()

        if now - self.last_trade_time < self.cooldown:

            return False

        if signal == self.last_direction:

            return False

        return True

    # ---------------- OPEN TRADE ----------------

    def open_trade_fn(self, signal, price):

        # SL / TP setup

        sl_distance = 0.0010

        tp_distance = 0.0020

        if signal == "BUY":

            sl = price - sl_distance

            tp = price + tp_distance

        else:

            sl = price + sl_distance

            tp = price - tp_distance

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

SL: {round(sl,5)}

TP: {round(tp,5)}

""")

    # ---------------- CLOSE TRADE ----------------

    def close_trade(self, price):

        t = self.open_trade

        self.open_trade = None

        entry = t["entry"]

        sl = t["sl"]

        tp = t["tp"]

        side = t["type"]

        result = ""

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

📤 CLOSED ({result})

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

            # OPEN TRADE

            if self.open_trade is None:

                if sig != "NO TRADE" and self.can_trade(sig):

                    self.open_trade_fn(sig, price)

            # CLOSE TRADE (SL/TP check every loop)

            elif self.open_trade is not None:

                self.close_trade(price)

            # STATS every 5 min

            if time.time() - last_stats > 300:

                self.stats()

                last_stats = time.time()

            time.sleep(10)

bot = PaperBot()
bot.run()