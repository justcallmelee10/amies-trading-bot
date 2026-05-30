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

    # ---------------- PRICE ----------------
    def get_price(self):

        try:
            r = requests.get(
                "https://api.fxratesapi.com/latest?base=EUR&currencies=USD",
                timeout=10
            )

            data = r.json()
            price = data.get("rates", {}).get("USD")

            if price:
                self.last_price = float(price)
                return float(price)

        except:
            pass

        return self.last_price

    # ---------------- STRATEGY (UPGRADED) ----------------
    def signal(self, price):

        self.prices.append(price)

        if len(self.prices) > 80:
            self.prices.pop(0)

        if len(self.prices) < 20:
            return "NO TRADE"

        # ---------------- LAYER 1: TREND ----------------
        fast = sum(self.prices[-5:]) / 5
        slow = sum(self.prices[-20:]) / 20

        trend_up = fast > slow
        trend_down = fast < slow

        # ---------------- LAYER 2: MOMENTUM ----------------
        momentum = self.prices[-1] - self.prices[-5]

        strong_momentum = abs(momentum) > (price * 0.0002)

        # ---------------- LAYER 3: VOLATILITY FILTER ----------------
        recent = self.prices[-10:]
        volatility = max(recent) - min(recent)

        low_noise = volatility > price * 0.0003

        # ---------------- DECISION LOGIC ----------------
        if not strong_momentum or not low_noise:
            return "NO TRADE"

        if trend_up and momentum > 0:
            return "BUY"

        if trend_down and momentum < 0:
            return "SELL"

        return "NO TRADE"

    # ---------------- RISK CONTROL ----------------
    def can_trade(self, signal):

        now = time.time()

        if now - self.last_trade_time < self.cooldown:
            return False

        if signal == self.last_direction:
            return False

        return True

    # ---------------- OPEN TRADE ----------------
    def open_trade_fn(self, signal, price):

        sl = price * (0.999) if signal == "BUY" else price * (1.001)
        tp = price * (1.002) if signal == "BUY" else price * (0.998)

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
            f"📥 STRATEGY ENTRY {signal}\nPrice: {price}\nSL: {sl}\nTP: {tp}\nBalance: {self.balance}"
        )

    # ---------------- CLOSE TRADE ----------------
    def close_trade(self, price):

        t = self.open_trade
        self.open_trade = None

        entry = t["entry"]
        side = t["type"]

        if side == "BUY":
            pnl = price - entry
        else:
            pnl = entry - price

        self.balance += pnl

        self.send(
            f"📤 EXIT {side}\nPnL: {round(pnl,5)}\nBalance: {round(self.balance,2)}"
        )

    # ---------------- MAIN LOOP ----------------
    def run(self):

        self.send("✅ UPGRADED STRATEGY BOT STARTED")

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


if __name__ == "__main__":
    PaperBot().run()