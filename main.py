import requests
import time

BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"


class PaperBot:

    def __init__(self):

        self.prices = []
        self.balance = 1000
        self.open_trade = None

        self.last_trade_time = 0
        self.cooldown = 60
        self.last_direction = None
        self.last_signal = None

    # ---------------- TELEGRAM ----------------
    def send(self, msg):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        except Exception as e:
            print("TELEGRAM ERROR:", e)

    # ---------------- SAFE PRICE FEED ----------------
    def get_price(self):
        try:
            url = "https://stooq.com/q/l/?s=eurusd&f=sd2t2ohlcv&h&e=json"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                print("BAD STATUS:", r.status_code)
                return None

            # SAFE JSON PARSING
            try:
                data = r.json()
            except Exception:
                print("RAW RESPONSE (NOT JSON):", r.text[:200])
                return None

            if "symbols" not in data or not data["symbols"]:
                print("BAD RESPONSE FORMAT:", data)
                return None

            price = data["symbols"][0].get("close")

            if price is None:
                return None

            return float(price)

        except Exception as e:
            print("PRICE ERROR:", e)
            return None

    # ---------------- SIGNAL ENGINE ----------------
    def signal(self, price):

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

        self.send(f"""📥 OPEN {signal}
Price: {price}
SL: {sl}
TP: {tp}
Balance: {self.balance}""")

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

        self.send(f"""📤 {result}
PnL: {round(pnl,5)}
Balance: {round(self.balance,2)}""")

    # ---------------- MAIN LOOP ----------------
    def run(self):

        print("🔥 BOT STARTED - STABLE MODE")

        while True:

            try:

                price = self.get_price()

                if price is None:
                    time.sleep(5)
                    continue

                sig = self.signal(price)

                if sig == self.last_signal:
                    time.sleep(5)
                    continue

                self.last_signal = sig

                if self.open_trade is None:
                    if sig != "NO TRADE" and self.can_trade(sig):
                        self.open_trade_fn(sig, price)

                else:
                    self.close_trade(price)

                time.sleep(5)

            except Exception as e:
                print("LOOP ERROR:", e)
                time.sleep(5)


# ---------------- START BOT ----------------
if __name__ == "__main__":
    bot = PaperBot()
    bot.run()