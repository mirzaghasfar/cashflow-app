"""
Core state management for the cashback app.
Single demo-user model, persisted to a local JSON file.

Model: the user pays partners directly (outside this app). This app only
tracks the cashback earned on that spend. The cashback balance is the one
and only pool of funds the user controls in-app — they can stake it,
invest it, or withdraw it (minus a service fee).
"""

import json
import os
from datetime import datetime, timezone

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "state.json")

STAKING_APY = 0.105          # 10.5% annual, accrued daily
WITHDRAWAL_FEE_PCT = 0.025   # 2.5% platform service fee on withdrawals


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _default_state():
    return {
        "cashback_balance": 0.0,
        "staked_balance": 0.0,
        "staked_last_accrued": None,   # ISO timestamp of last accrual
        "invested_balance_cost_basis": 0.0,  # total Rs ever put into investments (cost basis)
        "holdings": {},                # ticker -> units held
        "total_spent": 0.0,            # lifetime spend logged across all partners
        "transactions": [],            # list of dicts, newest first
        "created_at": _now_iso(),
    }


def load_state():
    if not os.path.exists(STATE_FILE):
        state = _default_state()
        save_state(state)
        return state
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        # backfill any missing keys (forward compatibility)
        defaults = _default_state()
        for k, v in defaults.items():
            if k not in state:
                state[k] = v
        return state
    except (json.JSONDecodeError, OSError):
        state = _default_state()
        save_state(state)
        return state


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def add_transaction(state, tx_type, description, amount):
    """Append a transaction record. amount is signed (+credit / -debit) from the user's perspective."""
    state["transactions"].insert(0, {
        "timestamp": _now_iso(),
        "type": tx_type,
        "description": description,
        "amount": round(amount, 2),
    })
    # keep history bounded so the file doesn't grow unbounded
    state["transactions"] = state["transactions"][:300]


# ---------------------------------------------------------------------------
# Logging a purchase (payment happens directly with the partner, outside the app)
# ---------------------------------------------------------------------------

def log_purchase(state, partner_name, category, items_summary, total_spend, cashback_pct):
    """
    Records a purchase made directly with a partner (no in-app payment).
    Credits cashback_balance based on total_spend * cashback_pct.
    Returns (success: bool, message: str).
    """
    if total_spend <= 0:
        return False, "Spend amount must be greater than zero."

    cashback_earned = round(total_spend * (cashback_pct / 100.0), 2)

    state["cashback_balance"] = round(state["cashback_balance"] + cashback_earned, 2)
    state["total_spent"] = round(state["total_spent"] + total_spend, 2)

    add_transaction(
        state, "order",
        f"{partner_name} ({category}): {items_summary} — Rs {total_spend:,.0f} spent",
        total_spend,  # informational only — no balance is debited in-app for this entry
    )
    add_transaction(
        state, "cashback_earned",
        f"Cashback from {partner_name} ({cashback_pct}%)",
        cashback_earned,
    )
    save_state(state)
    return True, f"Purchase logged! You earned Rs {cashback_earned:,.0f} cashback."


# ---------------------------------------------------------------------------
# Staking
# ---------------------------------------------------------------------------

def accrue_staking(state):
    """
    Calculates elapsed time since last accrual and adds daily-compounded
    interest to the staked balance. Called on every app load.
    """
    if state["staked_balance"] <= 0 or state["staked_last_accrued"] is None:
        return state

    last = datetime.fromisoformat(state["staked_last_accrued"])
    now = datetime.now(timezone.utc)
    elapsed_days = (now - last).total_seconds() / 86400.0

    if elapsed_days < (1.0 / 24):  # don't bother accruing for less than 1 hour
        return state

    daily_rate = STAKING_APY / 365.0
    # compound daily for the number of whole days elapsed, then prorate the remainder
    full_days = int(elapsed_days)
    remainder = elapsed_days - full_days

    balance = state["staked_balance"]
    total_interest = 0.0
    for _ in range(full_days):
        day_interest = balance * daily_rate
        total_interest += day_interest
        balance += day_interest
    if remainder > 0:
        partial_interest = balance * daily_rate * remainder
        total_interest += partial_interest
        balance += partial_interest

    if total_interest > 0.0001:
        state["staked_balance"] = round(balance, 4)
        add_transaction(
            state, "staking_yield",
            f"Staking yield ({elapsed_days:.2f} days @ {STAKING_APY*100:.1f}% APY)",
            total_interest,
        )

    state["staked_last_accrued"] = _now_iso()
    save_state(state)
    return state


def stake_funds(state, amount):
    if amount <= 0:
        return False, "Stake amount must be greater than zero."
    if state["cashback_balance"] < amount:
        return False, "Insufficient cashback balance."

    # accrue any pending interest first so we don't lose it
    accrue_staking(state)

    state["cashback_balance"] = round(state["cashback_balance"] - amount, 2)
    state["staked_balance"] = round(state["staked_balance"] + amount, 2)
    if state["staked_last_accrued"] is None:
        state["staked_last_accrued"] = _now_iso()

    add_transaction(state, "stake", "Staked cashback balance", -amount)
    save_state(state)
    return True, f"Staked Rs {amount:,.0f}. Earning {STAKING_APY*100:.1f}% APY, accrued daily."


def unstake_funds(state, amount):
    if amount <= 0:
        return False, "Unstake amount must be greater than zero."
    accrue_staking(state)
    if state["staked_balance"] < amount:
        return False, "Insufficient staked balance."

    state["staked_balance"] = round(state["staked_balance"] - amount, 2)
    state["cashback_balance"] = round(state["cashback_balance"] + amount, 2)

    add_transaction(state, "unstake", "Unstaked back to cashback balance", amount)
    save_state(state)
    return True, f"Unstaked Rs {amount:,.0f} back to your cashback balance."


# ---------------------------------------------------------------------------
# Investing
# ---------------------------------------------------------------------------

def invest_funds(state, ticker, amount, current_price):
    if amount <= 0:
        return False, "Investment amount must be greater than zero."
    if state["cashback_balance"] < amount:
        return False, "Insufficient cashback balance."
    if current_price is None or current_price <= 0:
        return False, "Live price unavailable for this asset right now. Try again shortly."

    units = amount / current_price
    state["cashback_balance"] = round(state["cashback_balance"] - amount, 2)
    state["holdings"][ticker] = round(state["holdings"].get(ticker, 0.0) + units, 8)
    state["invested_balance_cost_basis"] = round(state["invested_balance_cost_basis"] + amount, 2)

    add_transaction(
        state, "invest",
        f"Invested in {ticker} @ Rs {current_price:,.2f}/unit ({units:.6f} units)",
        -amount,
    )
    save_state(state)
    return True, f"Invested Rs {amount:,.0f} in {ticker}."


def divest_funds(state, ticker, amount, current_price):
    """Sell a rupee amount worth of a holding, proceeds go to cashback_balance."""
    if amount <= 0:
        return False, "Sell amount must be greater than zero."
    if current_price is None or current_price <= 0:
        return False, "Live price unavailable for this asset right now. Try again shortly."

    held_units = state["holdings"].get(ticker, 0.0)
    held_value = held_units * current_price
    if held_value < amount - 0.01:
        return False, f"You only hold Rs {held_value:,.2f} worth of {ticker}."

    units_to_sell = amount / current_price
    state["holdings"][ticker] = round(max(0.0, held_units - units_to_sell), 8)
    if state["holdings"][ticker] <= 0.000001:
        del state["holdings"][ticker]

    state["cashback_balance"] = round(state["cashback_balance"] + amount, 2)

    add_transaction(
        state, "divest",
        f"Sold Rs {amount:,.0f} of {ticker} @ Rs {current_price:,.2f}/unit",
        amount,
    )
    save_state(state)
    return True, f"Sold Rs {amount:,.0f} worth of {ticker}. Proceeds added to cashback balance."


# ---------------------------------------------------------------------------
# Withdrawal
# ---------------------------------------------------------------------------

def withdraw_funds(state, amount, destination):
    if amount <= 0:
        return False, "Withdrawal amount must be greater than zero."
    if state["cashback_balance"] < amount:
        return False, "Insufficient cashback balance."

    fee = round(amount * WITHDRAWAL_FEE_PCT, 2)
    net_payout = round(amount - fee, 2)

    state["cashback_balance"] = round(state["cashback_balance"] - amount, 2)

    add_transaction(
        state, "withdrawal",
        f"Withdrew to {destination} (fee: Rs {fee:,.0f})",
        -amount,
    )
    save_state(state)
    return True, (
        f"Withdrawal initiated: Rs {amount:,.0f} requested, "
        f"Rs {fee:,.0f} service fee ({WITHDRAWAL_FEE_PCT*100:.1f}%) deducted, "
        f"Rs {net_payout:,.0f} net sent to {destination}."
    )

