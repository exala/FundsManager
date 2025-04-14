from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

def bybit_wallet_marathon():
    api_key = os.getenv('BYBIT_API_KEY_MARATHON')
    secret = os.getenv('BYBIT_API_SECRET_MARATHON')
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=secret,
    )
    wallet_balance = session.get_wallet_balance(accountType="UNIFIED")
    total_equity = wallet_balance['result']['list'][0]['totalEquity']
    print(f"Total Equity: {total_equity} USDT")
    return total_equity

bybit_wallet_marathon()