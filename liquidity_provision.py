import os
import requests
from zapper_query import z_query_app_nft_lp

def get_liquidity_provision_zapper():
    response = requests.post(
        'https://public.zapper.xyz/graphql',
        headers={
            'Content-Type': 'application/json',
            'x-zapper-api-key': os.getenv('ZAPPER_API')
        },
        json={
            'query': z_query_app_nft_lp,
            'variables': {
                "addresses": [os.getenv('ZAPPER_WALLET')],
            }
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    positions = data['data']['portfolioV2']['appBalances']['byApp']['edges'][0]['node']['positionBalances']['edges']

    liquidity = sum(
        float(token['token']['balanceUSD'])
        for pos in positions 
        if 'Staked' in pos['node']['displayProps']['label']
        for token in pos['node']['tokens']
        if token['metaType'] == 'SUPPLIED'
    )
    print(f"💧 Total in Liquidity Provision: ${liquidity:,.2f}")
    return liquidity

get_liquidity_provision_zapper()