import streamlit as st
import plotly.graph_objects as go

from data.state_manager import load_state, accrue_staking, stake_funds, unstake_funds, STAKING_APY
from ui_helpers import inject_global_css, money_card, pill, AMBER, SURFACE, TEXT, MUTED, BORDER

st.set_page_config(page_title="Staking — CashFlow", page_icon="🔒", layout="wide")
inject_global_css()

state = load_state()
state = accrue_staking(state)

st.title("🔒 Staking")
st.caption(f"Put your cashback to work. Earn {STAKING_APY*100:.1f}% APY, calculated and added to your balance every day.")

col1, col2 = st.columns(2)
with col1:
    money_card("Cashback Balance", state["cashback_balance"], "Available to stake")
with col2:
    money_card("Staked Balance", state["staked_balance"], "Earning daily yield", color=AMBER)

st.markdown(pill(f"{STAKING_APY*100:.1f}% APY · accrued daily · no lock-up", "amber"), unsafe_allow_html=True)
st.markdown("")

stake_tab, unstake_tab = st.tabs(["Stake", "Unstake"])

with stake_tab:
    st.markdown("##### Move cashback into staking")
    if state["cashback_balance"] <= 0:
        st.info("You have no cashback balance to stake yet. Earn some by ordering from partners first.")
    else:
        amount = st.slider(
            "Amount to stake (Rs)",
            min_value=0.0,
            max_value=float(state["cashback_balance"]),
            value=min(1000.0, float(state["cashback_balance"])),
            step=50.0,
        )

        # 12-month projection chart
        months = list(range(0, 13))
        values = [amount * (1 + STAKING_APY / 365) ** (m * 30) for m in months]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=values, mode="lines",
            line=dict(color=AMBER, width=3, shape="spline"),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.12)",
            hovertemplate="Month %{x}<br>Rs %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
            font=dict(color=TEXT), margin=dict(l=10, r=10, t=10, b=10),
            height=220, showlegend=False,
            xaxis=dict(title="Months", showgrid=False, color=MUTED, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED, tickfont=dict(size=10), tickprefix="Rs "),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        projected_daily = amount * STAKING_APY / 365
        projected_yearly = amount * STAKING_APY
        st.caption(f"Estimated yield: ~Rs {projected_daily:,.2f}/day · ~Rs {projected_yearly:,.0f}/year at current APY")

        if st.button("🔒 Stake now", type="primary"):
            ok, msg = stake_funds(state, amount)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

with unstake_tab:
    st.markdown("##### Move staked funds back to cashback balance")
    if state["staked_balance"] <= 0:
        st.info("You don't have any funds staked right now.")
    else:
        unstake_amount = st.slider(
            "Amount to unstake (Rs)",
            min_value=0.0,
            max_value=float(state["staked_balance"]),
            value=float(state["staked_balance"]),
            step=50.0,
        )
        if st.button("🔓 Unstake", type="primary"):
            ok, msg = unstake_funds(state, unstake_amount)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

st.divider()
st.caption(
    "Yield is calculated daily compounding based on real elapsed time since your last visit — "
    "come back tomorrow and you'll see it grow. This is a simulated yield for demo purposes."
)

