# 💸 CashFlow — Cashback & Wealth App

A Streamlit fintech demo: users earn cashback (10–15%) by ordering or booking from
40+ partners (coffee, food, ecommerce, padel, go-karting), then choose to **stake**
that cashback for daily yield, **invest** it into live-priced gold/silver/crypto/stocks,
or **withdraw** it (minus a service fee).

> ⚠️ **This is a simulated demo, not a real financial product.** No real money moves,
> no real assets are purchased, and there is no real user authentication. Building a
> production version that handles real funds would require money-transmitter licensing,
> KYC/AML compliance, and integration with a real payments processor (e.g. Stripe, Plaid)
> and brokerage/exchange APIs (e.g. Alpaca, a licensed crypto exchange).

## Features

- **Partners** — browse 5 categories (coffee, food, ecommerce, padel, go-karting),
  add items to a cart or book a time slot, checkout from your wallet balance, earn
  cashback automatically.
- **Staking** — move cashback into a staking pool earning 10.5% APY, compounded and
  credited daily based on real elapsed time.
- **Invest** — allocate cashback into 20 real assets (gold, silver, oil, BTC, ETH, SOL,
  AAPL, GOOGL, META, and more) with **live prices via yfinance**.
- **Withdraw** — cash out to a bank account or digital wallet, with a transparent 2.5%
  service fee shown before confirming.
- **History** — full transaction log across every action.

## Project structure

```
cashback_app/
├── Home.py                      # Dashboard / entry point
├── pages/
│   ├── 1_🛍️_Partners.py         # Browse, order, book
│   ├── 2_🔒_Staking.py          # Stake / unstake
│   ├── 3_📊_Invest.py           # Buy/sell live-priced assets
│   ├── 4_🏦_Withdraw.py         # Withdraw with fee
│   └── 5_📜_History.py          # Transaction log
├── data/
│   ├── partners.py              # Partner directory (static)
│   ├── assets.py                # Investable asset list (tickers)
│   ├── state_manager.py         # Core business logic + persistence
│   ├── price_fetcher.py         # Live price fetching (yfinance, cached)
│   └── state.json               # Auto-created on first run (gitignored)
├── ui_helpers.py                # Shared styling/components
├── requirements.txt
└── .streamlit/config.toml       # Theme
```

## Run locally

```bash
# 1. Clone your repo (after pushing, see GitHub steps below)
git clone https://github.com/YOUR-USERNAME/cashflow-app.git
cd cashflow-app

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run Home.py
```

The app will open at `http://localhost:8501`. A demo wallet is seeded with
$1,000 on first run.

## How daily staking/investment updates work

Every time you load the app, it checks how much real time has passed since your
last visit (`staked_last_accrued` timestamp) and compounds the staking yield for
that elapsed period — so if you come back after 3 days, you'll see 3 days of yield
applied at once. Investment values are simply `units held × current live price`,
fetched fresh (cached 5 minutes) on every page load.

## Notes on data persistence

This demo uses a single local JSON file (`data/state.json`) as a stand-in
database — there's no login system, so it's a single shared "demo user."
This is intentional for simplicity per the project scope. If deployed to
Streamlit Community Cloud, note that the filesystem there is **ephemeral**:
the app's state will reset whenever the app restarts/redeploys (e.g. after
inactivity or a new git push). For persistent multi-user data, swap
`state_manager.py`'s file I/O for a real database (e.g. Supabase, Postgres,
Firebase) — the function signatures are written so this swap is contained
to one file.

---

## Deploying: GitHub + Streamlit Community Cloud (step by step)

### Step 1 — Create a GitHub repository
1. Go to [github.com](https://github.com) and log in (create an account if you don't have one).
2. Click the **+** icon (top right) → **New repository**.
3. Name it something like `cashflow-app`. Keep it **Public** (required for the free
   tier of Streamlit Community Cloud, unless you have a paid plan).
4. Don't initialize with a README (we already have one) — leave all checkboxes
   unchecked, then click **Create repository**.

### Step 2 — Push this project to GitHub
From inside the `cashback_app` folder on your computer, run:

```bash
git init
git add .
git commit -m "Initial commit: CashFlow cashback app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cashflow-app.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username. If prompted, log in with
your GitHub credentials (GitHub may require a Personal Access Token instead of a
password for `git push` — GitHub will show a link to create one if needed).

### Step 3 — Deploy on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your
   GitHub account.
2. Click **Create app** (or **New app**).
3. Choose **"Deploy a public app from GitHub"**.
4. Select:
   - **Repository**: `YOUR-USERNAME/cashflow-app`
   - **Branch**: `main`
   - **Main file path**: `Home.py`
5. Click **Deploy**. Streamlit Cloud will install everything in `requirements.txt`
   and launch your app — this takes 1–3 minutes the first time.
6. You'll get a public URL like `https://cashflow-app-yourname.streamlit.app` that
   you can share with anyone.

### Step 4 — Making updates later
Whenever you change the code locally:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

Streamlit Community Cloud auto-redeploys within a minute or two of every push to
`main`.

### Troubleshooting
- **App shows an import error on deploy**: double check `requirements.txt` lists
  every package you're using.
- **Stock/crypto prices show "unavailable"**: yfinance occasionally rate-limits;
  prices are cached for 5 minutes and will retry automatically. This can also
  happen if Yahoo Finance is temporarily down.
- **Balances reset unexpectedly**: this is expected ephemeral-storage behavior on
  free hosting (see "Notes on data persistence" above) — wire up a real database
  if you need state to survive redeploys/restarts.
