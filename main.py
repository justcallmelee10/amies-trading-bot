import requests
import time

BOT_TOKEN = "8637865419:AAH-pSZe4e1zgPOng9kcwYjpnxYS6v80v_c"
CHAT_ID = "8236639818"


class PaperBot:

    def __init__(self):
        self.last_price = None

    def send(self, msg):
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg},
                timeout=10
            )
        except:
            pass

    # 🔥 ONLY SAFE PRICE FUNCTION (NO ASSUMPTIONS)
    def get_price(self):

        try:
            r = requests.get(
                "https://api.fxratesapi.com/latest?base=EUR&currencies=USD",
                timeout=10
            )

            data = r.json()

            rates = data.get("rates", None)

            if isinstance(rates, dict):
                price = rates.get("USD", None)

                if price is not None:
                    self.last_price = float(price)
                    return float(price)

            return self.last_price

        except Exception as e:
            print("PRICE ERROR:", e)
            return self.last_price

    def run(self):

        self.send("BOT STARTED")

        while True:

            price = self.get_price()

            print("PRICE:", price)

            time.sleep(3)


if __name__ == "__main__":
    PaperBot().run()