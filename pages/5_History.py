import streamlit as st
from datetime import datetime

from data.state_manager import load_state, accrue_staking
from ui_helpers import inject_global_css, tx_icon, tx_row_html

st.set_page_config(page_title="History — CashFlow", page_icon="📜", layout="wide")
inject_global_css()

state = load_state()
state = accrue_staking(state)

st.title("📜 Transaction History")
st.caption("Full activity log across orders, cashback, staking, investing, and withdrawals.")

filter_types = sorted(set(tx["type"] for tx in state["transactions"]))
selected = st.multiselect("Filter by type", options=filter_types, default=filter_types)

if not state["transactions"]:
    st.info("No transactions yet.")
else:
    filtered = [tx for tx in state["transactions"] if tx["type"] in selected]
    if not filtered:
        st.warning("No transactions match the selected filters.")
    else:
        rows_html = ""
        for tx in filtered:
            ts = datetime.fromisoformat(tx["timestamp"]).strftime("%b %d, %Y · %H:%M")
            rows_html += tx_row_html(tx_icon(tx["type"]), tx["description"], ts, tx["amount"], tx_type=tx["type"])
        st.markdown(rows_html, unsafe_allow_html=True)

