import requests
import time

BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"


class PaperBot:

    def __init__(self):

        self.prices = []
        self.balance = 1000.0
        self.open_trade = None

        self.last_trade_time = 0
        self.cooldown = 60

        self.last_direction = None
        self.last_signal = None

        self.last_price = None

    # ---------------- TELEGRAM ----------------
    def send(self, msg):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            r = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "text": msg
                },
                timeout=10
            )

            print("TELEGRAM STATUS:", r.status_code)
            print("TELEGRAM RESPONSE:", r.text)

        except Exception as e:
            print("TELEGRAM ERROR:", e)

    # ---------------- PRICE ENGINE ----------------
    def get_price(self):

        sources = [
            "https://stooq.com/q/l/?s=eurusd&f=sd2t2ohlcv&h&e=json",
            "https://api.exchangerate.host/latest?base=EUR&symbols=USD"
        ]

        for url in sources:

            try:
                r = requests.get(url, timeout=10)

                if r.status_code != 200:
                    continue

                try:
                    data = r.json()
                except:
                    continue

                # SOURCE 1
                if "symbols" in data:
                    price = data["symbols"][0].get("close")
                    if price:
                        self.last_price = float(price)
                        return float(price)

                # SOURCE 2
                if "rates" in data:
                    price = data["rates"].get("USD")
                    if price:
                        self.last_price = float(price)
                        return float(price)

            except:
                continue

        return self.last_price

    # ---------------- SIGNAL ----------------
    def signal(self, price):

        if price is None:
            return "NO TRADE"

        self.prices.append(price)

        if len(self.prices) > 50:
            self.prices.pop(0)

        if len(self.prices) < 10:
            return "NO TRADE"

        short = self.prices[-3:]
        mid = self.prices[-8:]

        short_trend = short[-1] - short[0]
        mid_trend = mid[-1] - mid[0]

        volatility = max(mid) - min(mid)
        avg = sum(mid) / len(mid)

        threshold = avg * 0.0003

        if volatility < threshold:
            return "NO TRADE"

        if short_trend > 0 and mid_trend > 0:
            return "BUY"

        if short_trend < 0 and mid_trend < 0:
            return "SELL"

        return "NO TRADE"

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

        self.send(f"📥 OPEN {signal}\nPrice: {price}\nSL: {sl}\nTP: {tp}\nBalance: {self.balance}")

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

        self.send(f"📤 {result}\nPnL: {round(pnl,5)}\nBalance: {round(self.balance,2)}")

    # ---------------- MAIN LOOP ----------------
    def run(self):

        print("🔥 BOT RUNNING - STABLE MODE")

        while True:

            try:

                price = self.get_price()

                if price is None:
                    print("NO PRICE → waiting")
                    time.sleep(5)
                    continue

                sig = self.signal(price)

                if sig == self.last_signal:
                    time.sleep(5)
                    continue

                self.last_signal = sig

                print("PRICE:", price, "SIGNAL:", sig)

                if self.open_trade is None:
                    if sig != "NO TRADE" and self.can_trade(sig):
                        self.open_trade_fn(sig, price)

                else:
                    self.close_trade(price)

                time.sleep(5)

            except Exception as e:
                print("LOOP ERROR:", e)
                time.sleep(5)


# ---------------- START ----------------
if __name__ == "__main__":
    bot = PaperBot()

    bot.send("✅ BOT STARTED")

    bot.run()