import requests
import time
import os
import psycopg2

API_KEY = "2UFIT1549JNPNLPY"
BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"

BASE_URL = "https://www.alphavantage.co/query"

class PerformanceBot:

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

    # ---------------- SIGNAL ----------------

    def analyze(self, price):

        self.prices.append(price)

        if len(self.prices) > 50:

            self.prices.pop(0)

        score = 50

        if len(self.prices) > 5:

            if self.prices[-1] > self.prices[-5]:

                score += 20

            else:

                score += 20

        if score < 75:

            return "NO TRADE", score

        signal = "BUY" if self.prices[-1] > self.prices[-5] else "SELL"

        return signal, score

    # ---------------- TRADE ----------------

    def open_trade(self, signal, price):

        self.open_trade = {

            "signal": signal,

            "entry": price,

            "time": time.time()

        }

        self.send_alert(f"OPEN {signal} @ {price}")

    def close_trade(self, price):

        trade = self.open_trade

        self.open_trade = None

        entry = trade["entry"]

        signal = trade["signal"]

        pnl = (price - entry) if signal == "BUY" else (entry - price)

        self.balance += pnl

        self.trade_log.append(pnl)

        result = "WIN" if pnl > 0 else "LOSS"

        self.send_alert(f"CLOSE {result} | PnL {round(pnl,5)} | BAL {round(self.balance,2)}")

    # ---------------- STATS ----------------

    def show_stats(self):

        total = len(self.trade_log)

        if total == 0:

            return

        wins = len([t for t in self.trade_log if t > 0])

        losses = total - wins

        win_rate = (wins / total) * 100

        total_pnl = sum(self.trade_log)

        avg_pnl = total_pnl / total

        stats = f"""

📊 PERFORMANCE UPDATE

Trades: {total}

Wins: {wins}

Losses: {losses}

Win Rate: {round(win_rate,2)}%

Total PnL: {round(total_pnl,4)}

Avg Trade: {round(avg_pnl,5)}

Balance: {round(self.balance,2)}

"""

        self.send_alert(stats)

    # ---------------- LOOP ----------------

    def run(self):

        print("PERFORMANCE BOT ONLINE")

        last_stats_time = time.time()

        while True:

            price = self.get_price()

            if price is None:

                time.sleep(5)

                continue

            signal, score = self.analyze(price)

            print("PRICE:", price, "SIGNAL:", signal)

            # open trade

            if self.open_trade is None and signal != "NO TRADE":

                self.open_trade(signal, price)

            # close trade after 1 min

            elif self.open_trade is not None:

                if time.time() - self.open_trade["time"] > 60:

                    self.close_trade(price)

            # send stats every 5 minutes

            if time.time() - last_stats_time > 300:

                self.show_stats()

                last_stats_time = time.time()

            time.sleep(10)

bot = PerformanceBot()
bot.run()