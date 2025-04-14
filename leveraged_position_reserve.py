from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_leveraged_position_reserve():
    api_key = os.getenv('BYBIT_API_KEY_MARATHON')
    secret = os.getenv('BYBIT_API_SECRET_MARATHON')
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=secret,
    )
    wallet_balance = session.get_wallet_balance(accountType="UNIFIED", coin='USDT')
    leveraged_position = wallet_balance['result']['list'][0]['totalMarginBalance']
    print(leveraged_position)
    return leveraged_position

get_leveraged_position_reserve()