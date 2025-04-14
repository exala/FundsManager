from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv
from typing import Dict, Any
from zapper_query import z_query_spot
import requests

load_dotenv()

def stablecoin_bybit():
    api_key = os.getenv('BYBIT_API_KEY_MARATHON')
    secret = os.getenv('BYBIT_API_SECRET_MARATHON')
    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=secret,
        recv_window=10000
    )
    wallet_balance = session.get_wallet_balance(accountType="UNIFIED")
    
    sum = float(wallet_balance['result']['list'][0]['totalEquity'])
    coins = wallet_balance['result']['list'][0]['coin']
    sum = 0
    for x in range(len(coins)):
        if coins[x]['coin'] == 'USDT':
            usdValue = float(coins[x]['usdValue'])
            sum += usdValue
        if coins[x]['coin'] == 'USDTC':
            usdValue = float(coins[x]['usdValue'])
            sum += usdValue
            
            # sum = sum + int(coins[x]['usdValue'])
        
    # print(json.dumps(wallet_balance, indent=2))
    return sum

def stablecoin_zapper():
    response = requests.post(
            'https://public.zapper.xyz/graphql',
            headers={
                'Content-Type': 'application/json',
                'x-zapper-api-key': os.getenv('ZAPPER_API')
            },
            json={
                'query': z_query_spot,
                'variables': {
                    "addresses": [os.getenv('ZAPPER_WALLET')],
                    "first": 100
                }
            },
            timeout=30
        )
    response.raise_for_status()
    data = response.json()
    tokens = data['data']['portfolioV2']['tokenBalances']['byToken']['edges']
    sum = 0
    for x in range(len(tokens)):
        # print(x)
        symbol = tokens[x]['node']['symbol']
        # print(symbol)
        if symbol == 'USDC':
            usdc_balance = float(tokens[x]['node']['balanceUSD'])
            sum += usdc_balance
        if symbol == 'USDS':
            usds_balance = float(tokens[x]['node']['balanceUSD'])
            sum += usds_balance
        if symbol == 'USDT':
            usdt_balance = float(tokens[x]['node']['balanceUSD'])
            sum += usdt_balance
    return sum
    # print(json.dumps(data, indent=2))

def total_stablecoin():
    wallet = stablecoin_zapper()
    bybit = stablecoin_bybit()
    total = bybit+wallet
    print('bybit', bybit)
    print('wallet', wallet)
    print("Total", total)
    return total

# bybit = get_spot_position_reserve_bybit()
# wallet = get_spot_position_reserve_zapper()
# print(bybit + wallet)

total_stablecoin()