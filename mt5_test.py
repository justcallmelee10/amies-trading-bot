import MetaTrader5 as mt5

# login details from MT5 demo account
LOGIN = 1200059296
PASSWORD = "Eliudmugu@2004"
SERVER = "JustMarkets-Demo3"

# connect
if not mt5.initialize():
    print("MT5 init failed")
    quit()

authorized = mt5.login(LOGIN, password=PASSWORD, server=SERVER)

if authorized:
    print("CONNECTED TO DEMO ACCOUNT")
else:
    print("LOGIN FAILED")