"""
Top 20 investable assets: commodities, crypto, and top stocks.
Tickers are Yahoo Finance compatible (used by yfinance).
"""

ASSETS = [
    {"ticker": "GLD", "name": "Gold (SPDR Gold Shares)", "type": "Commodity"},
    {"ticker": "SLV", "name": "Silver (iShares Silver Trust)", "type": "Commodity"},
    {"ticker": "USO", "name": "Crude Oil (US Oil Fund)", "type": "Commodity"},
    {"ticker": "BTC-USD", "name": "Bitcoin", "type": "Crypto"},
    {"ticker": "ETH-USD", "name": "Ethereum", "type": "Crypto"},
    {"ticker": "SOL-USD", "name": "Solana", "type": "Crypto"},
    {"ticker": "AAPL", "name": "Apple Inc.", "type": "Stock"},
    {"ticker": "GOOGL", "name": "Alphabet (Google)", "type": "Stock"},
    {"ticker": "META", "name": "Meta Platforms", "type": "Stock"},
    {"ticker": "MSFT", "name": "Microsoft", "type": "Stock"},
    {"ticker": "AMZN", "name": "Amazon", "type": "Stock"},
    {"ticker": "TSLA", "name": "Tesla", "type": "Stock"},
    {"ticker": "NVDA", "name": "NVIDIA", "type": "Stock"},
    {"ticker": "NFLX", "name": "Netflix", "type": "Stock"},
    {"ticker": "DIS", "name": "Disney", "type": "Stock"},
    {"ticker": "NKE", "name": "Nike", "type": "Stock"},
    {"ticker": "KO", "name": "Coca-Cola", "type": "Stock"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "type": "Stock"},
    {"ticker": "V", "name": "Visa", "type": "Stock"},
    {"ticker": "SPY", "name": "S&P 500 Index (ETF)", "type": "Index"},
]

# Note: SpaceX is privately held and has no public ticker, so it isn't
# included here. If SpaceX ever lists publicly, swap it in by ticker.

TICKER_LOOKUP = {a["ticker"]: a for a in ASSETS}

