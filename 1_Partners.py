import streamlit as st
from datetime import date, timedelta

from data.partners import PARTNERS
from data.state_manager import load_state, log_purchase
from ui_helpers import inject_global_css, money_card, pill, GREEN_LIGHT

st.set_page_config(page_title="Partners — CashFlow", page_icon="🛍️", layout="wide")
inject_global_css()

state = load_state()

st.title("🛍️ Partners")
st.caption(
    "Pick what you ordered or booked — you pay the partner directly. "
    "We log it and credit your cashback instantly."
)

money_card("Cashback Balance", state["cashback_balance"], "Stake, invest, or withdraw anytime", color=GREEN_LIGHT)
st.markdown("")

# selections live in session state, keyed per item/booking
if "selections" not in st.session_state:
    st.session_state.selections = {}  # key: (category, partner, item) -> {qty, price, ...}

# ---------------- Category tabs ----------------
category_keys = list(PARTNERS.keys())
tab_labels = [PARTNERS[k]["label"] for k in category_keys]
tabs = st.tabs(tab_labels)

for tab, cat_key in zip(tabs, category_keys):
    cat_data = PARTNERS[cat_key]
    with tab:
        cashback_pct = cat_data["cashback_pct"]
        st.markdown(pill(f"{cashback_pct}% cashback at all {cat_data['label']} partners", "green"), unsafe_allow_html=True)
        st.markdown("")

        if cat_data["ui"] == "menu":
            for partner in cat_data["partners"]:
                with st.expander(f"**{partner['name']}**", expanded=False):
                    for item in partner["items"]:
                        c1, c2, c3, c4 = st.columns([3, 1.2, 1, 1.3])
                        with c1:
                            st.write(item["item"])
                        with c2:
                            st.write(f"Rs {item['price']:,.0f}")
                        with c3:
                            sel_key = (cat_key, partner["name"], item["item"])
                            qty = st.number_input(
                                "Qty", min_value=0, max_value=20, value=0, step=1,
                                key=f"qty_{cat_key}_{partner['name']}_{item['item']}",
                                label_visibility="collapsed",
                            )
                            if qty > 0:
                                st.session_state.selections[sel_key] = {
                                    "category": cat_key,
                                    "partner": partner["name"],
                                    "item": item["item"],
                                    "price": item["price"],
                                    "qty": qty,
                                    "cashback_pct": cashback_pct,
                                }
                            elif sel_key in st.session_state.selections:
                                del st.session_state.selections[sel_key]
                        with c4:
                            cb = item["price"] * qty * cashback_pct / 100
                            if qty > 0:
                                st.caption(f"+Rs {cb:,.0f} cashback")

        elif cat_data["ui"] == "slot":
            for partner in cat_data["partners"]:
                with st.expander(f"**{partner['name']}** — Rs {partner['price_per_hour']:,.0f}/hour", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        booking_date = st.date_input(
                            "Date", min_value=date.today(), max_value=date.today() + timedelta(days=30),
                            value=date.today(), key=f"date_{cat_key}_{partner['name']}",
                        )
                    with c2:
                        slot_time = st.selectbox(
                            "Time slot",
                            ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"],
                            key=f"time_{cat_key}_{partner['name']}",
                        )
                    with c3:
                        hours = st.selectbox("Duration (hrs)", [1, 2, 3], key=f"hrs_{cat_key}_{partner['name']}")

                    cost = partner["price_per_hour"] * hours
                    cashback_amt = cost * cashback_pct / 100
                    st.write(f"Total to pay partner: **Rs {cost:,.0f}**  ·  You'll earn: **Rs {cashback_amt:,.0f}** cashback")

                    if st.button(f"I booked {partner['name']}", key=f"book_{cat_key}_{partner['name']}"):
                        summary = f"{hours}h booking on {booking_date} at {slot_time}"
                        ok, msg = log_purchase(state, partner["name"], cat_key, summary, cost, cashback_pct)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

st.divider()

# ---------------- Review & log selections (menu items only) ----------------
st.subheader("🧾 Review your order")
if not st.session_state.selections:
    st.info("Select items above using the quantity selectors, then log your order here to earn cashback.")
else:
    order_total = 0.0
    cashback_total = 0.0
    by_partner = {}
    for key, line in st.session_state.selections.items():
        by_partner.setdefault((line["category"], line["partner"]), []).append(line)

    for (cat_key, partner_name), lines in by_partner.items():
        st.markdown(f"**{partner_name}**")
        partner_total = 0.0
        for line in lines:
            line_total = line["price"] * line["qty"]
            partner_total += line_total
            st.write(f"- {line['qty']}× {line['item']} — Rs {line_total:,.0f}")
        order_total += partner_total
        cashback_total += partner_total * lines[0]["cashback_pct"] / 100

    st.markdown(f"**Total to pay partner: Rs {order_total:,.0f}**  ·  Cashback you'll earn: **Rs {cashback_total:,.0f}**")

    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("✅ I paid — log this order", type="primary", use_container_width=True):
            errors = []
            for (cat_key, partner_name), lines in by_partner.items():
                partner_total = sum(l["price"] * l["qty"] for l in lines)
                summary = ", ".join(f"{l['qty']}x {l['item']}" for l in lines)
                ok, msg = log_purchase(state, partner_name, cat_key, summary, partner_total, lines[0]["cashback_pct"])
                if not ok:
                    errors.append(f"{partner_name}: {msg}")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.selections = {}
                st.success("Order logged! Cashback credited to your balance.")
                st.rerun()
    with cc2:
        if st.button("🗑️ Clear selections", use_container_width=True):
            st.session_state.selections = {}
            st.rerun()

