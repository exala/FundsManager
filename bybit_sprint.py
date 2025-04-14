from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

def bybit_wallet_sprint():
    api_key = os.getenv('BYBIT_API_KEY_SPRINT')
    secret = os.getenv('BYBIT_API_SECRET_SPRINT')
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=secret,
    )
    wallet_balance = session.get_wallet_balance(accountType="UNIFIED")
    total_equity = wallet_balance['result']['list'][0]['totalEquity']
    print(f"Total Equity: {total_equity} USDT")
    return total_equity