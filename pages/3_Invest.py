import streamlit as st

from data.state_manager import load_state, accrue_staking, invest_funds, divest_funds
from data.price_fetcher import get_live_prices, get_usd_to_pkr_rate
from data.assets import ASSETS, TICKER_LOOKUP
from ui_helpers import inject_global_css, money_card, pill, BLUE
from charts import portfolio_allocation_chart

st.set_page_config(page_title="Invest — CashFlow", page_icon="📊", layout="wide")
inject_global_css()

state = load_state()
state = accrue_staking(state)

st.title("📊 Invest")
st.caption("Put your cashback into gold, silver, crypto, and top global stocks. Prices update live, converted to PKR.")

with st.spinner("Fetching live market prices..."):
    prices_usd = get_live_prices()
    fx_rate = get_usd_to_pkr_rate()

# convert every asset price to PKR
prices_pkr = {
    t: (p * fx_rate if p is not None else None)
    for t, p in prices_usd.items()
}

st.caption(f"💱 Using live exchange rate: 1 USD ≈ Rs {fx_rate:,.2f}")

col1, col2 = st.columns(2)
with col1:
    money_card("Cashback Balance", state["cashback_balance"], "Available to invest")
with col2:
    invested_value = sum(
        (state["holdings"].get(a["ticker"], 0.0) * prices_pkr.get(a["ticker"], 0))
        for a in ASSETS
    )
    money_card("Portfolio Value", invested_value, "Live market value", color=BLUE)

st.markdown("")

browse_tab, portfolio_tab = st.tabs(["Browse Assets", "My Portfolio"])

with browse_tab:
    type_filter = st.multiselect(
        "Filter by type", options=["Commodity", "Crypto", "Stock", "Index"],
        default=["Commodity", "Crypto", "Stock", "Index"],
    )
    st.markdown("")

    for asset in ASSETS:
        if asset["type"] not in type_filter:
            continue
        price = prices_pkr.get(asset["ticker"])
        price_display = f"Rs {price:,.2f}" if price else "Price unavailable"
        kind = {"Commodity": "amber", "Crypto": "green", "Stock": "gray", "Index": "gray"}.get(asset["type"], "gray")

        with st.container():
            c1, c2, c3 = st.columns([3, 1.4, 1.5])
            with c1:
                st.markdown(
                    f"**{asset['name']}** &nbsp; <span style='color:#8B93AB; font-size:0.85rem;'>{asset['ticker']}</span> "
                    + pill(asset["type"], kind),
                    unsafe_allow_html=True,
                )
            with c2:
                st.write(price_display)
            with c3:
                if price and state["cashback_balance"] > 0:
                    with st.popover("Invest", use_container_width=True):
                        amt = st.number_input(
                            "Amount (Rs)", min_value=100.0, max_value=float(state["cashback_balance"]),
                            value=min(1000.0, float(state["cashback_balance"])), step=100.0,
                            key=f"inv_amt_{asset['ticker']}",
                        )
                        units = amt / price
                        st.caption(f"≈ {units:.6f} units at Rs {price:,.2f}")
                        if st.button("Confirm investment", key=f"inv_btn_{asset['ticker']}"):
                            ok, msg = invest_funds(state, asset["ticker"], amt, price)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                elif not price:
                    st.caption("Unavailable")
                else:
                    st.caption("No cashback balance")
        st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)

with portfolio_tab:
    holdings = {t: u for t, u in state["holdings"].items() if u > 0.000001}
    if not holdings:
        st.info("You don't hold any assets yet. Browse assets and make your first investment.")
    else:
        alloc_fig = portfolio_allocation_chart(holdings, prices_pkr, TICKER_LOOKUP)
        if alloc_fig:
            st.plotly_chart(alloc_fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("")
        for ticker, units in holdings.items():
            asset = TICKER_LOOKUP.get(ticker, {"name": ticker, "type": ""})
            price = prices_pkr.get(ticker)
            value = units * price if price else None

            c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.2, 1.5])
            with c1:
                st.markdown(f"**{asset['name']}**  ({ticker})")
            with c2:
                st.write(f"{units:.6f} units")
            with c3:
                st.write(f"Rs {value:,.2f}" if value else "—")
            with c4:
                if value and value > 0:
                    with st.popover("Sell", use_container_width=True):
                        sell_amt = st.number_input(
                            "Amount to sell (Rs)", min_value=1.0, max_value=float(value),
                            value=float(value), step=10.0, key=f"sell_amt_{ticker}",
                        )
                        if st.button("Confirm sale", key=f"sell_btn_{ticker}"):
                            ok, msg = divest_funds(state, ticker, sell_amt, price)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            st.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)

st.divider()
st.caption(
    "Prices are sourced live via Yahoo Finance (yfinance), converted to PKR using a live USD/PKR rate, "
    "and cached for 5 minutes. Investing here uses simulated holdings for demo purposes — no real assets are purchased."
)
