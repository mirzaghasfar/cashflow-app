"""
Chart builders using Plotly, styled to match the dark fintech theme.
"""

import plotly.graph_objects as go
from datetime import datetime
from collections import defaultdict

from ui_helpers import BG, SURFACE, TEXT, MUTED, GREEN_LIGHT, AMBER, BLUE, RED, BORDER

CHART_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(color=TEXT, family="-apple-system, Segoe UI, sans-serif"),
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        font=dict(color=MUTED, size=11),
    ),
)


def net_worth_history_chart(transactions, current_cashback, current_staked, current_invested):
    """
    Reconstructs an approximate net-worth-over-time series by walking transactions
    backwards from the current totals. This is a simulated/demo visualization —
    it shows the shape of how balances moved, not a perfectly audited ledger.
    'order' entries are excluded since they're informational logs of external
    spend, not movements of in-app balances.
    """
    if not transactions:
        return None

    balance_affecting = [tx for tx in transactions if tx["type"] != "order"]
    if not balance_affecting:
        return None

    # transactions are newest-first; walk backwards (oldest first) for a running total
    events = sorted(balance_affecting, key=lambda t: t["timestamp"])

    running_total = 0.0
    points_x = []
    points_y = []
    for tx in events:
        running_total += tx["amount"]
        ts = datetime.fromisoformat(tx["timestamp"])
        points_x.append(ts)
        points_y.append(running_total)

    if not points_x:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=points_x, y=points_y,
        mode="lines",
        line=dict(color=GREEN_LIGHT, width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(45,212,191,0.12)",
        hovertemplate="%{x|%b %d, %H:%M}<br>Rs %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        height=260,
        showlegend=False,
        xaxis=dict(showgrid=False, color=MUTED, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED, tickfont=dict(size=10), tickprefix="Rs "),
    )
    return fig


def spending_breakdown_chart(transactions):
    """Donut chart of spend by partner category, based on 'order' transactions."""
    category_totals = defaultdict(float)
    for tx in transactions:
        if tx["type"] == "order":
            # description format: "Partner (category): summary"
            desc = tx["description"]
            if "(" in desc and ")" in desc:
                category = desc.split("(")[1].split(")")[0]
            else:
                category = "other"
            category_totals[category] += abs(tx["amount"])

    if not category_totals:
        return None

    labels = list(category_totals.keys())
    values = list(category_totals.values())
    palette = [GREEN_LIGHT, AMBER, BLUE, RED, "#A78BFA", "#FB923C"]
    colors = [palette[i % len(palette)] for i in range(len(labels))]

    fig = go.Figure(data=[go.Pie(
        labels=[l.title() for l in labels],
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color=SURFACE, width=2)),
        textfont=dict(color=TEXT, size=12),
        hovertemplate="%{label}<br>Rs %{value:,.0f} (%{percent})<extra></extra>",
    )])
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        height=280,
        showlegend=True,
    )
    return fig


def portfolio_allocation_chart(holdings, prices, ticker_lookup):
    """Bar chart of current investment holdings by value."""
    rows = []
    for ticker, units in holdings.items():
        price = prices.get(ticker)
        if price and units > 0:
            rows.append((ticker_lookup.get(ticker, {}).get("name", ticker), units * price))

    if not rows:
        return None

    rows.sort(key=lambda r: r[1], reverse=True)
    names = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig = go.Figure(data=[go.Bar(
        x=values, y=names,
        orientation="h",
        marker=dict(color=BLUE),
        hovertemplate="%{y}<br>Rs %{x:,.0f}<extra></extra>",
    )])
    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        height=max(180, 40 * len(rows)),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor=BORDER, color=MUTED, tickprefix="Rs "),
        yaxis=dict(showgrid=False, color=TEXT, autorange="reversed"),
    )
    return fig
