import streamlit as st
from datetime import datetime

from data.state_manager import load_state, accrue_staking, STAKING_APY, WITHDRAWAL_FEE_PCT
from data.price_fetcher import get_live_prices
from ui_helpers import inject_global_css, money_card, net_worth_strip, tx_icon, tx_row_html, GREEN_LIGHT, AMBER, BLUE
from charts import net_worth_history_chart, spending_breakdown_chart

st.set_page_config(
    page_title="CashFlow — Cashback & Wealth",
    page_icon="💸",
    layout="wide",
)

inject_global_css()

state = load_state()
state = accrue_staking(state)

st.title("💸 CashFlow")
st.caption("Earn cashback at Lahore's best spots. Stake it, invest it, or cash it out — your call.")

# ---------------- Live investment value ----------------
prices = get_live_prices()
invested_value = 0.0
any_price_missing = False
for ticker, units in state["holdings"].items():
    price = prices.get(ticker)
    if price:
        invested_value += units * price
    else:
        any_price_missing = True

# ---------------- Net worth strip (signature element) ----------------
net_worth_strip(
    cashback=state["cashback_balance"],
    staked=state["staked_balance"],
    invested=invested_value,
)

# ---------------- Balance cards ----------------
col1, col2, col3 = st.columns(3)
with col1:
    money_card("Cashback Balance", state["cashback_balance"], "Stake, invest, or withdraw", color=GREEN_LIGHT)
with col2:
    money_card("Staked Balance", state["staked_balance"], f"Earning {STAKING_APY*100:.1f}% APY daily", color=AMBER)
with col3:
    sub = "Live market value" if not any_price_missing else "Live market value (some prices delayed)"
    money_card("Invested Balance", invested_value, sub, color=BLUE)

st.markdown("")
st.caption(f"💳 Lifetime spend logged across partners: Rs {state['total_spent']:,.0f}")
st.markdown("")

# ---------------- Quick actions ----------------
st.subheader("Quick actions")
qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button("🛍️ Browse Partners", use_container_width=True):
        st.switch_page("pages/1_Partners.py")
with qa2:
    if st.button("🔒 Stake Cashback", use_container_width=True):
        st.switch_page("pages/2_Staking.py")
with qa3:
    if st.button("📊 Invest Cashback", use_container_width=True):
        st.switch_page("pages/3_Invest.py")
with qa4:
    if st.button("🏦 Withdraw Funds", use_container_width=True):
        st.switch_page("pages/4_Withdraw.py")

st.divider()

# ---------------- Charts ----------------
chart_col1, chart_col2 = st.columns([1.4, 1])
with chart_col1:
    st.subheader("📈 Balance history")
    growth_fig = net_worth_history_chart(
        state["transactions"], state["cashback_balance"],
        state["staked_balance"], invested_value,
    )
    if growth_fig:
        st.plotly_chart(growth_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Your balance history will appear here once you start using the app.")

with chart_col2:
    st.subheader("🍩 Spending by category")
    spend_fig = spending_breakdown_chart(state["transactions"])
    if spend_fig:
        st.plotly_chart(spend_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Log a purchase from a partner to see your spending breakdown here.")

st.divider()

# ---------------- Recent activity ----------------
st.subheader("Recent activity")
if not state["transactions"]:
    st.info("No activity yet. Head to **Partners** to log your first purchase and start earning cashback.")
else:
    rows_html = ""
    for tx in state["transactions"][:10]:
        ts = datetime.fromisoformat(tx["timestamp"]).strftime("%b %d, %H:%M")
        rows_html += tx_row_html(tx_icon(tx["type"]), tx["description"], ts, tx["amount"], tx_type=tx["type"])
    st.markdown(rows_html, unsafe_allow_html=True)

st.divider()
st.caption(
    f"💡 Withdrawals incur a {WITHDRAWAL_FEE_PCT*100:.1f}% service fee. "
    "Staking and investing involve simulated returns for demo purposes — this is not a real financial product."
)
