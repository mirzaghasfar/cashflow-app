"""
Shared UI helpers: dark fintech design system + reusable components.

Design tokens
-------------
Background:      #0B1120 (deep ink-indigo, not pure black)
Surface:         #141B2E (card backgrounds)
Surface-raised:  #1C2540 (hover/expander backgrounds)
Border:          #232C45
Text primary:    #F3F5F9
Text muted:      #8B93AB
Accent (growth): #2DD4BF -> #10B981 (teal-emerald, cashback/positive)
Accent (stake):  #F59E0B (amber, reserved only for staking/earning state)
Accent (invest): #60A5FA (blue, market/investing)
Accent (danger): #F87171 (withdrawals/fees/negative)
"""

import streamlit as st

BG = "#0B1120"
SURFACE = "#141B2E"
SURFACE_RAISED = "#1C2540"
BORDER = "#232C45"
TEXT = "#F3F5F9"
MUTED = "#8B93AB"

GREEN = "#10B981"
GREEN_LIGHT = "#2DD4BF"
AMBER = "#F59E0B"
BLUE = "#60A5FA"
RED = "#F87171"


def inject_global_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {BG};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stSidebar"] * {{
            color: {TEXT} !important;
        }}
        h1, h2, h3, h4 {{
            letter-spacing: -0.02em;
            font-weight: 700;
            color: {TEXT} !important;
        }}
        p, span, div, label {{
            color: {TEXT};
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {MUTED} !important;
        }}

        /* ---------- money card ---------- */
        .money-card {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 20px 22px;
        }}
        .money-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {MUTED};
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .money-value {{
            font-size: 2rem;
            font-weight: 800;
            color: {TEXT};
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.02em;
        }}
        .money-sub {{
            font-size: 0.8rem;
            color: {MUTED};
            margin-top: 4px;
        }}

        /* ---------- pills ---------- */
        .pill {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.01em;
        }}
        .pill-green {{ background: rgba(16,185,129,0.15); color: {GREEN_LIGHT}; }}
        .pill-amber {{ background: rgba(245,158,11,0.15); color: {AMBER}; }}
        .pill-blue  {{ background: rgba(96,165,250,0.15); color: {BLUE}; }}
        .pill-red   {{ background: rgba(248,113,113,0.15); color: {RED}; }}
        .pill-gray  {{ background: {SURFACE_RAISED}; color: {MUTED}; }}

        /* ---------- net worth strip ---------- */
        .networth-strip {{
            background: linear-gradient(135deg, {SURFACE} 0%, {SURFACE_RAISED} 100%);
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 24px 26px;
            margin-bottom: 22px;
        }}
        .networth-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {MUTED};
            font-weight: 700;
        }}
        .networth-value {{
            font-size: 2.6rem;
            font-weight: 800;
            color: {TEXT};
            letter-spacing: -0.02em;
            font-variant-numeric: tabular-nums;
            margin: 4px 0 14px 0;
        }}
        .networth-bar {{
            display: flex;
            width: 100%;
            height: 10px;
            border-radius: 999px;
            overflow: hidden;
            background: {SURFACE_RAISED};
        }}
        .networth-seg {{ height: 100%; }}

        /* ---------- activity rows ---------- */
        .tx-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 13px 0;
            border-bottom: 1px solid {BORDER};
        }}
        .tx-desc {{ font-weight: 500; color: {TEXT}; }}
        .tx-time {{ font-size: 0.76rem; color: {MUTED}; margin-left: 30px; margin-top: 2px; }}
        .tx-amount {{ font-weight: 700; font-variant-numeric: tabular-nums; }}

        /* ---------- buttons ---------- */
        .stButton button {{
            background: {SURFACE_RAISED};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            font-weight: 600;
        }}
        .stButton button:hover {{
            border-color: {GREEN_LIGHT};
            color: {GREEN_LIGHT};
        }}
        .stButton button[kind="primary"] {{
            background: {GREEN};
            border: none;
            color: #04231A;
        }}
        .stButton button[kind="primary"]:hover {{
            background: {GREEN_LIGHT};
            color: #04231A;
        }}

        /* ---------- tabs ---------- */
        .stTabs [data-baseweb="tab"] {{
            color: {MUTED};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            color: {GREEN_LIGHT} !important;
        }}

        hr {{ border-color: {BORDER} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def money_card(label, value, sub=None, color=None, currency="Rs"):
    color = color or TEXT
    sub_html = f'<div class="money-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="money-card">
            <div class="money-label">{label}</div>
            <div class="money-value" style="color:{color};">{currency} {value:,.0f}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def net_worth_strip(cashback, staked, invested, currency="Rs"):
    total = max(cashback + staked + invested, 0.01)
    segs = [
        ("Cashback", cashback, GREEN_LIGHT),
        ("Staked", staked, AMBER),
        ("Invested", invested, BLUE),
    ]
    bar_html = "".join(
        f'<div class="networth-seg" style="width:{max(v,0)/total*100:.2f}%; background:{c};"></div>'
        for _, v, c in segs
    )
    legend_html = "".join(
        f'<span style="margin-right:18px; font-size:0.78rem; color:{MUTED};">'
        f'<span style="display:inline-block; width:8px; height:8px; border-radius:50%; '
        f'background:{c}; margin-right:6px;"></span>{label}: {currency} {v:,.0f}</span>'
        for label, v, c in segs
    )
    st.markdown(
        f"""
        <div class="networth-strip">
            <div class="networth-label">Total Net Worth</div>
            <div class="networth-value">{currency} {total:,.0f}</div>
            <div class="networth-bar">{bar_html}</div>
            <div style="margin-top:14px;">{legend_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text, kind="gray"):
    return f'<span class="pill pill-{kind}">{text}</span>'


def tx_icon(tx_type):
    mapping = {
        "order": "🛍️",
        "cashback_earned": "💰",
        "topup": "➕",
        "stake": "🔒",
        "unstake": "🔓",
        "staking_yield": "📈",
        "invest": "📊",
        "divest": "💵",
        "withdrawal": "🏦",
    }
    return mapping.get(tx_type, "•")


def tx_row_html(icon, desc, time_str, amount, tx_type=None, currency="Rs"):
    if tx_type == "order":
        # informational spend log only — not an in-app balance movement
        amount_str = f"{currency} {amount:,.0f} spent"
        amount_color = MUTED
    else:
        amount_str = f"+{currency} {amount:,.0f}" if amount >= 0 else f"-{currency} {abs(amount):,.0f}"
        amount_color = GREEN_LIGHT if amount >= 0 else TEXT
    return f"""
    <div class="tx-row">
        <div>
            <span style="font-size:1.1rem; margin-right:8px;">{icon}</span>
            <span class="tx-desc">{desc}</span>
            <div class="tx-time">{time_str}</div>
        </div>
        <div class="tx-amount" style="color:{amount_color};">{amount_str}</div>
    </div>
    """
