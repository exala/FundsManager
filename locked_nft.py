import os
import requests
from zapper_query import z_query_app_nft_lp

def get_locked_nft_zapper():
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

    locked_nft = sum(
        float(pos['node']['balanceUSD']) 
        for pos in positions 
        if 'veNFT' in pos['node']['displayProps']['label']
    )
    print(f"\n🔒 Total Locked in veNFTs: ${locked_nft:,.2f}")
    return locked_nft

get_locked_nft_zapper()