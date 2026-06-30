"""
Static partner directory for the cashback app — Lahore edition.
Each partner belongs to a category which determines the booking/ordering UI:
  - menu: simple item list with prices + quantity (coffee, food, ecommerce)
  - slot: time-slot based booking (padel, go-karting, cinema)
"""

PARTNERS = {
    # ---------------- COFFEE (menu) ----------------
    "coffee": {
        "label": "☕ Coffee",
        "ui": "menu",
        "cashback_pct": 12,
        "partners": [
            {"name": "Extraction Coffee", "items": [
                {"item": "Cappuccino", "price": 750},
                {"item": "Latte", "price": 700},
                {"item": "Americano", "price": 550},
                {"item": "Cold Brew", "price": 800},
                {"item": "Sandwich", "price": 950},
            ]},
            {"name": "Double Shot", "items": [
                {"item": "Espresso", "price": 450},
                {"item": "Flat White", "price": 700},
                {"item": "Iced Latte", "price": 750},
                {"item": "Croissant", "price": 500},
            ]},
            {"name": "Third Culture", "items": [
                {"item": "Mocha", "price": 800},
                {"item": "Pour Over", "price": 850},
                {"item": "Chai Latte", "price": 650},
                {"item": "Brownie", "price": 600},
            ]},
        ],
    },

    # ---------------- ECOMMERCE (menu) ----------------
    "ecommerce": {
        "label": "🛒 Ecommerce",
        "ui": "menu",
        "cashback_pct": 8,
        "partners": [
            {"name": "Gymarmour", "items": [
                {"item": "Gym T-Shirt", "price": 1800},
                {"item": "Training Shorts", "price": 2200},
                {"item": "Gym Bag", "price": 3500},
                {"item": "Stringer Tank", "price": 1600},
            ]},
            {"name": "Iron Gear", "items": [
                {"item": "Lifting Belt", "price": 4500},
                {"item": "Wrist Wraps", "price": 1500},
                {"item": "Gym Gloves", "price": 1800},
                {"item": "Shaker Bottle", "price": 900},
            ]},
            {"name": "Lama", "items": [
                {"item": "Graphic Tee", "price": 2200},
                {"item": "Hoodie", "price": 4800},
                {"item": "Cap", "price": 1500},
            ]},
            {"name": "Outfitters", "items": [
                {"item": "Casual Shirt", "price": 3200},
                {"item": "Denim Jeans", "price": 4500},
                {"item": "Sneakers", "price": 6500},
                {"item": "Jacket", "price": 7800},
            ]},
        ],
    },

    # ---------------- PADEL (slot) ----------------
    "padel": {
        "label": "🎾 Padel",
        "ui": "slot",
        "cashback_pct": 15,
        "partners": [
            {"name": "Padel Club Lahore", "price_per_hour": 5000},
            {"name": "Smash Padel Arena", "price_per_hour": 5500},
            {"name": "DHA Padel Courts", "price_per_hour": 6000},
            {"name": "Gulberg Padel Hub", "price_per_hour": 5200},
        ],
    },

    # ---------------- GO-KARTING (slot) ----------------
    "karting": {
        "label": "🏎️ Go-Karting",
        "ui": "slot",
        "cashback_pct": 15,
        "partners": [
            {"name": "2F2F Karting", "price_per_hour": 4000},
        ],
    },

    # ---------------- ENTERTAINMENT (slot) ----------------
    "entertainment": {
        "label": "🎬 Entertainment",
        "ui": "slot",
        "cashback_pct": 10,
        "partners": [
            {"name": "Cue Cinemas", "price_per_hour": 1200},
        ],
    },
}


def get_all_partner_names():
    """Returns a flat list of (category, partner_name) tuples."""
    out = []
    for cat, data in PARTNERS.items():
        for p in data["partners"]:
            out.append((cat, p["name"]))
    return out


def count_partners():
    return sum(len(v["partners"]) for v in PARTNERS.values())

