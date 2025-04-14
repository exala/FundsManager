import requests
import os
from typing import Dict, Any
from zapper_query import z_query
from dotenv import load_dotenv

load_dotenv()

def fetch_portfolio() -> Dict[str, Any]:
  try:
      response = requests.post(
          'https://public.zapper.xyz/graphql',
          headers={
              'Content-Type': 'application/json',
              'x-zapper-api-key': os.getenv('ZAPPER_API')
          },
          json={
              'query': z_query,
              'variables': {
                  "addresses": [os.getenv('ZAPPER_WALLET')],
              }
          },
          timeout=30
      )

      response.raise_for_status()
      data = response.json()

      if 'errors' in data:
          raise ValueError(f"GraphQL Errors: {data['errors']}")

      portfolio_data = data['data']['portfolioV2']
      token_balance = portfolio_data['tokenBalances']['totalBalanceUSD']
      app_balance = portfolio_data['appBalances']['totalBalanceUSD']
      total_balance = token_balance + app_balance
      
      print(f"Token Balance: ${token_balance:,.2f}")
      print(f"App Balance: ${app_balance:,.2f}")
      print(f"Total Balance: ${total_balance:,.2f}")
      
      return total_balance

  except requests.RequestException as e:
      print(f"Request failed: {e}")
      raise
  except ValueError as e:
      print(f"Data validation failed: {e}")
      raise
  except Exception as e:
      print(f"Unexpected error: {e}")
      raise
  
fetch_portfolio()