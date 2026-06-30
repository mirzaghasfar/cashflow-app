"""
Live price fetching via yfinance, with Streamlit caching to avoid
hammering the API, and graceful fallback if a fetch fails.
"""

import streamlit as st
import yfinance as yf

from data.assets import ASSETS


@st.cache_data(ttl=300, show_spinner=False)  # cache for 5 minutes
def get_live_prices():
    """
    Fetches current prices for all tracked assets in one batch call.
    Returns dict: ticker -> price (float) or None if unavailable.
    """
    tickers = [a["ticker"] for a in ASSETS]
    prices = {t: None for t in tickers}
    try:
        data = yf.download(
            tickers=tickers,
            period="1d",
            interval="1m",
            progress=False,
            group_by="ticker",
            threads=True,
        )
        for t in tickers:
            try:
                if len(tickers) == 1:
                    close_series = data["Close"].dropna()
                else:
                    close_series = data[t]["Close"].dropna()
                if len(close_series) > 0:
                    prices[t] = float(close_series.iloc[-1])
            except Exception:
                prices[t] = None
    except Exception:
        pass

    # fallback: try fetching any missing tickers individually
    missing = [t for t, p in prices.items() if p is None]
    for t in missing:
        try:
            tk = yf.Ticker(t)
            hist = tk.history(period="1d")
            if not hist.empty:
                prices[t] = float(hist["Close"].iloc[-1])
        except Exception:
            prices[t] = None

    return prices


def get_price(ticker, price_cache=None):
    """Convenience accessor; uses a provided cache dict or fetches fresh."""
    if price_cache is None:
        price_cache = get_live_prices()
    return price_cache.get(ticker)


FALLBACK_USD_PKR = 278.60  # used only if the live fetch fails


@st.cache_data(ttl=300, show_spinner=False)
def get_usd_to_pkr_rate():
    """Fetches the live USD->PKR exchange rate, with a static fallback if unavailable."""
    try:
        tk = yf.Ticker("USDPKR=X")
        hist = tk.history(period="1d")
        if not hist.empty:
            rate = float(hist["Close"].iloc[-1])
            if rate > 0:
                return rate
    except Exception:
        pass
    return FALLBACK_USD_PKR

