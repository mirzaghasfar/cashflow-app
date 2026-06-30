import streamlit as st

from data.state_manager import load_state, accrue_staking, withdraw_funds, WITHDRAWAL_FEE_PCT
from ui_helpers import inject_global_css, money_card, pill

st.set_page_config(page_title="Withdraw — CashFlow", page_icon="🏦", layout="wide")
inject_global_css()

state = load_state()
state = accrue_staking(state)

st.title("🏦 Withdraw")
st.caption("Cash out your cashback balance to your bank account or a digital wallet.")

money_card("Cashback Balance", state["cashback_balance"], "Available to withdraw")
st.markdown("")
st.markdown(pill(f"{WITHDRAWAL_FEE_PCT*100:.1f}% service fee applies on withdrawal", "red"), unsafe_allow_html=True)
st.markdown("")

if state["cashback_balance"] <= 0:
    st.info("You have no cashback balance to withdraw. Earn cashback by ordering from partners, or unstake/sell investments first.")
else:
    destination_type = st.radio("Withdraw to", ["Bank Account", "Digital Wallet"], horizontal=True)

    if destination_type == "Bank Account":
        c1, c2 = st.columns(2)
        with c1:
            bank_name = st.text_input("Bank name", placeholder="e.g. HBL, Meezan, UBL, Allied")
        with c2:
            account_number = st.text_input("Account number (demo only — last 4 digits is enough)", placeholder="••••1234")
        destination_label = f"{bank_name or 'Bank account'} (****{account_number[-4:] if account_number else 'xxxx'})"
    else:
        wallet_provider = st.selectbox("Provider", ["JazzCash", "EasyPaisa", "NayaPay", "SadaPay", "Other"])
        wallet_id = st.text_input("Wallet ID / phone number (demo only)")
        destination_label = f"{wallet_provider} ({wallet_id or 'unspecified'})"

    amount = st.slider(
        "Amount to withdraw (Rs)",
        min_value=0.0,
        max_value=float(state["cashback_balance"]),
        value=float(state["cashback_balance"]),
        step=50.0,
    )

    fee = round(amount * WITHDRAWAL_FEE_PCT, 2)
    net = round(amount - fee, 2)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Withdrawal amount", f"Rs {amount:,.0f}")
    with s2:
        st.metric("Service fee", f"-Rs {fee:,.0f}")
    with s3:
        st.metric("You receive", f"Rs {net:,.0f}")

    st.markdown("")
    confirm = st.checkbox("I understand a service fee applies and this is a simulated demo transaction.")

    if st.button("🏦 Withdraw funds", type="primary", disabled=not confirm):
        ok, msg = withdraw_funds(state, amount, destination_label)
        if ok:
            st.success(msg)
            st.balloons()
        else:
            st.error(msg)

st.divider()
st.caption(
    "This is a demo app — no real money is transferred. In a production fintech product, this flow "
    "would integrate with a licensed payments processor and require KYC/AML compliance."
)

