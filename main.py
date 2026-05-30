import requests
import time

BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"


class PaperBot:

    def __init__(self):

        self.prices = []
        self.last_price = None

        self.balance = 1000.0
        self.open_trade = None

        self.last_trade_time = 0
        self.cooldown = 60

        self.last_signal = None
        self.last_direction = None

    # ---------------- TELEGRAM ----------------
    def send(self, msg):
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg},
                timeout=10
            )
        except:
            pass

    # ---------------- PRICE (STABLE) ----------------
    def get_price(self):

        try:
            r = requests.get(
                "https://api.fxratesapi.com/latest?base=EUR&currencies=USD",
                timeout=10
            )

            data = r.json()

            rates = data.get("rates", {})

            price = rates.get("USD")

            if price is not None:
                self.last_price = float(price)
                return float(price)

        except:
            pass

        return self.last_price

    # ---------------- SIGNAL ENGINE ----------------
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

        if volatility < avg * 0.0003:
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

        self.send(
            f"📥 OPEN {signal}\nPrice: {price}\nSL: {sl}\nTP: {tp}\nBalance: {self.balance}"
        )

    # ---------------- CLOSE TRADE ----------------
    def close_trade(self, price):

        trade = self.open_trade
        self.open_trade = None

        entry = trade["entry"]
        side = trade["type"]

        if side == "BUY":
            pnl = price - entry
        else:
            pnl = entry - price

        self.balance += pnl

        self.send(
            f"📤 CLOSE {side}\nPnL: {round(pnl,5)}\nBalance: {round(self.balance,2)}"
        )

    # ---------------- MAIN LOOP ----------------
    def run(self):

        self.send("✅ BOT STARTED")

        while True:

            try:
                price = self.get_price()

                print("PRICE:", price)

                if price is None:
                    time.sleep(3)
                    continue

                sig = self.signal(price)

                print("SIGNAL:", sig)

                if self.open_trade is None:

                    if sig != "NO TRADE" and self.can_trade(sig):
                        self.open_trade_fn(sig, price)

                else:
                    self.close_trade(price)

                time.sleep(3)

            except Exception as e:
                print("ERROR:", e)
                time.sleep(3)


# ---------------- START ----------------
if __name__ == "__main__":
    PaperBot().run()