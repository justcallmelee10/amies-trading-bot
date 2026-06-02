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
        self.cooldown = 20

        self.last_signal = None

        # 🧠 AI MEMORY
        self.trades = []
        self.wins = 0
        self.losses = 0

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

        urls = [
            "https://api.fxratesapi.com/latest?base=EUR&currencies=USD",
            "https://api.exchangerate.host/latest?base=EUR&symbols=USD"
        ]

        for url in urls:
            try:
                r = requests.get(url, timeout=10)
                data = r.json()

                price = None
                if "rates" in data:
                    price = data["rates"].get("USD")

                if price:
                    self.last_price = float(price)
                    return float(price)

            except:
                continue

        return self.last_price

    # ---------------- EMA (TREND CORE) ----------------
    def ema(self, period):
        if len(self.prices) < period:
            return sum(self.prices) / len(self.prices)

        k = 2 / (period + 1)
        ema = self.prices[0]

        for p in self.prices:
            ema = p * k + ema * (1 - k)

        return ema

    # ---------------- SIGNAL ENGINE (AI SCORING) ----------------
    def signal(self, price):

        self.prices.append(price)
        if len(self.prices) > 100:
            self.prices.pop(0)

        if len(self.prices) < 20:
            return "NO TRADE", 0

        ema_fast = self.ema(5)
        ema_slow = self.ema(20)

        momentum = self.prices[-1] - self.prices[-5]

        trend_up = ema_fast > ema_slow
        trend_down = ema_fast < ema_slow

        # 🧠 confidence score (0 → 1)
        confidence = 0.5

        if trend_up:
            confidence += 0.2
        if trend_down:
            confidence += 0.2

        if abs(momentum) > price * 0.00015:
            confidence += 0.2

        if abs(ema_fast - ema_slow) > 0:
            confidence += 0.1

        # decision rules
        if confidence < 0.65:
            return "NO TRADE", confidence

        if trend_up and momentum > 0:
            return "BUY", confidence

        if trend_down and momentum < 0:
            return "SELL", confidence

        return "NO TRADE", confidence

    # ---------------- RISK CONTROL ----------------
    def can_trade(self, signal):
        now = time.time()

        if now - self.last_trade_time < self.cooldown:
            return False

        if signal == self.last_signal:
            return False

        return True

    # ---------------- OPEN TRADE ----------------
    def open_trade_fn(self, signal, price, confidence):

        sl = price * (0.999)
        tp = price * (1.0015)

        self.open_trade = {
            "type": signal,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "confidence": confidence
        }

        self.last_trade_time = time.time()
        self.last_signal = signal

        self.send(
            f"📥 OPEN {signal}\nPrice: {price}\nConfidence: {round(confidence,2)}\nSL: {sl}\nTP: {tp}"
        )

    # ---------------- CLOSE TRADE + LEARNING ----------------
    def close_trade(self, price):

        t = self.open_trade
        self.open_trade = None

        entry = t["entry"]
        side = t["type"]

        pnl = (price - entry) if side == "BUY" else (entry - price)

        self.balance += pnl

        # 🧠 learning
        if pnl > 0:
            self.wins += 1
            result = "WIN"
        else:
            self.losses += 1
            result = "LOSS"

        self.trades.append(pnl)

        winrate = self.wins / (self.wins + self.losses)

        self.send(
            f"📤 CLOSE {side}\n"
            f"Result: {result}\n"
            f"PnL: {round(pnl,5)}\n"
            f"Balance: {round(self.balance,2)}\n"
            f"WinRate: {round(winrate*100,1)}%"
        )

    # ---------------- MAIN LOOP ----------------
    def run(self):

        self.send("🚀 AI FREE BOT STARTED")

        while True:

            price = self.get_price()

            print("PRICE:", price)

            if price is None:
                time.sleep(3)
                continue

            sig, conf = self.signal(price)

            print("SIGNAL:", sig, "CONF:", conf)

            if self.open_trade is None:
                if sig != "NO TRADE" and self.can_trade(sig):
                    self.open_trade_fn(sig, price, conf)
            else:
                self.close_trade(price)

            time.sleep(3)


if __name__ == "__main__":
    PaperBot().run()