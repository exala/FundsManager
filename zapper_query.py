z_query = """
  query PortfolioV2Totals($addresses: [Address!]!) {
    portfolioV2(addresses: $addresses) {
      # Token balances total
      tokenBalances {
        totalBalanceUSD

        # Network breakdown for tokens
        byNetwork(first: 10) {
          edges {
            node {
              network {
                name
                slug
                chainId
              }
              balanceUSD
            }
          }
        }
      }

      # App balances total
      appBalances {
        totalBalanceUSD

        # Network breakdown for app positions
        byNetwork(first: 10) {
          edges {
            node {
              network {
                name
                slug
                chainId
              }
              balanceUSD
            }
          }
        }
      }
    }
  }
"""

z_query_spot = """
query TokenBalances($addresses: [Address!]!, $first: Int) {
  portfolioV2(addresses: $addresses) {
    tokenBalances {
      totalBalanceUSD
      byToken(first: $first) {
        totalCount
        edges {
          node {
            symbol
            tokenAddress
            balance
            balanceUSD
            price
            imgUrlV2
            name
            network {
              name
            }
          }
        }
      }
    }
  }
}
"""

z_query_app_nft_lp = """
query AppBalances($addresses: [Address!]!, $first: Int = 10) {
  portfolioV2(addresses: $addresses) {
    appBalances {
      # Total value of all app positions
      totalBalanceUSD

      # Group positions by application
      byApp(first: $first) {
        totalCount
        edges {
          node {
            # App metadata
            balanceUSD
            app {
              displayName
              imgUrl
              description
              slug
              url
              category {
                name
              }
            }
            network {
              name
              slug
              chainId
              evmCompatible
            }

            # Position details with underlying assets
            positionBalances(first: 10) {
              edges {
                node {
                  # App token positions (e.g. LP tokens)
                  ... on AppTokenPositionBalance {
                    type
                    address
                    network
                    symbol
                    decimals
                    balance
                    balanceUSD
                    price
                    appId
                    groupId
                    groupLabel
                    supply
                    pricePerShare                    
                    # Underlying tokens in this position
                    tokens {
                      ... on BaseTokenPositionBalance {
                        type
                        address
                        network
                        balance
                        balanceUSD
                        price
                        symbol
                        decimals
                      }
                      ... on AppTokenPositionBalance {
                        type
                        address
                        network
                        balance
                        balanceUSD
                        price
                        symbol
                        decimals
                      }
                    }

                    # Detailed display properties 
                    displayProps {
                      label
                      images
                      balanceDisplayMode
                    }
                  }

                  # Contract positions (e.g. lending, farming positions)
                  ... on ContractPositionBalance {
                    type
                    address
                    network
                    appId
                    groupId
                    groupLabel
                    balanceUSD

                    # Underlying tokens with meta-types (SUPPLIED, BORROWED, etc.)
                    tokens {
                      metaType
                      token {
                        ... on BaseTokenPositionBalance {
                          type
                          address
                          network
                          balance
                          balanceUSD
                          price
                          symbol
                          decimals
                        }
                        ... on AppTokenPositionBalance {
                          type
                          address
                          network
                          balance
                          balanceUSD
                          price
                          symbol
                          decimals
                        }
                        ... on NonFungiblePositionBalance {
                          type
                          address
                          network
                          balance
                          balanceUSD
                          price
                          symbol
                          decimals
                        }
                      }
                    }

                    # Detailed display properties 
                    displayProps {
                      label
                      images
                      balanceDisplayMode
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""