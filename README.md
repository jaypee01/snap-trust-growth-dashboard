# Snap Trust & Growth Dashboard

A full-stack dashboard to track merchant and customer trust scores, loyalty tiers, historical trends, and AI-generated insights. Built for Hackathon 2025 with FastAPI (backend) and React + Vite (frontend) using synthetic CSV data and an auto-initialized SQLite DB.

---

## 🚀 What’s Inside

- **Backend (FastAPI)**: Trust scoring, loyalty tiers, history, benchmarks, dashboard aggregates, AI chat, and natural-language queries
- **Frontend (React + Vite + MUI + Nivo)**: Merchants/Consumers listings, detail pages, and dashboards with charts
- **Data**: `payments.csv` and `merchants_loyalty.csv` bootstrapped into `app/data/app.db`
- **AI**: OpenAI-backed summaries, recommendations, chart code generation (with safe fallbacks)

---

## 📁 Project Structure

```
snap-trust-growth-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── utils.py
│   │   ├── db.py
│   │   ├── endpoints/
│   │   │   ├── merchants_router.py
│   │   │   ├── customers_router.py
│   │   │   ├── dashboard.py
│   │   │   ├── ai_router.py
│   │   │   └── ai_query_router.py
│   │   ├── data/
│   │   │   ├── app.db
│   │   │   ├── merchants_loyalty.csv
│   │   │   └── payments.csv
│   │   └── dataGenerator/
│   │       ├── merchant_loyalty_data_generator.py
│   │       └── payments_data_generator.py
│   ├── requirements.txt
│   ├── package.json
│   └── test_ai_integration.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── Navbar.jsx
│   │       ├── MerchantsListing.jsx
│   │       ├── ConsumersListing.jsx
│   │       ├── Merchant-Detail.jsx
│   │       ├── Consumer-Detail.jsx
│   │       ├── MerchantsDashboard.jsx
│   │       ├── ConsumerDashboard.jsx
│   │       └── charts/
│   │           ├── TopMerchantsBar.jsx
│   │           ├── PaymentStatusPie.jsx
│   │           └── MonthlyCollectionsLine.jsx
│   └── package.json
├── start.sh
└── README.md
```

---

## ⚡ Quick Start (one command)

```bash
bash start.sh
```

- Verifies ports 8000 and 5173 are free
- Ensures backend `.env` exists with `OPENAI_API_KEY`
- Installs backend and frontend deps, then runs both servers
- Backend: http://localhost:8000  |  Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

If you prefer manual setup, see below.

---

## 🛠️ Manual Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Create backend/.env with your key
# echo "OPENAI_API_KEY=your_api_key_here" > .env

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Base URL: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`
- On startup, the app loads CSVs into `app/data/app.db` if empty and creates helpful indexes.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- Runs Vite dev server (default `http://localhost:5173`)

---

## 🔌 Backend Endpoints

### Root
- `GET /` — Health message

### Merchants (`app/endpoints/merchants_router.py`)
- `GET /merchants` — Paginated, sortable by `TrustScore` and `LoyaltyTier`
- `GET /merchants/{merchant_id}` — Full metrics + `Summary`, `Recommendations`
- `GET /merchants/{merchant_id}/summary/explain` — Explanation for TrustScore/Tier
- `GET /merchants/{merchant_id}/history` — Synthetic trend history for key metrics
- `GET /merchants/{merchant_id}/benchmark` — Peer benchmarks via `describe()`
- `GET /merchants/{merchant_id}/recommendations` — AI-backed with fallbacks

### Customers (`app/endpoints/customers_router.py`)
- `GET /customers` — Paginated, sortable by `TrustScore` and `LoyaltyTier`
- `GET /customers/{customer_id}` — Full metrics + `Summary`, `Recommendations`
- `GET /customers/{customer_id}/summary/explain` — Explanation for TrustScore/Tier
- `GET /customers/{customer_id}/history` — Date-wise metrics + derived scores
- `GET /customers/{customer_id}/recommendations` — AI-backed with fallbacks

### Dashboards (`app/endpoints/dashboard.py`)
- `GET /dashboard/merchants` —
  - `topMerchantsByPayments`: `[ { merchant, amount } ]`
  - `paymentStatusMix`: `[ { id, value } ]`
  - `topMerchantTrust`: `[ { merchant, trustScore, loyaltyTier } ]`
- `GET /dashboard/consumers` —
  - `monthlyCollections`: Nivo line-series for expected vs received

### AI Chat (`app/endpoints/ai_router.py`)
- `POST /ai/chat` — General AI chat for `consumer` or `merchant` context.
  - Detects chart requests and can generate Nivo chart component code.
  - Falls back to informative text if OpenAI is unavailable.
- `GET /ai/health` — Health check

### Natural Language Query (`app/endpoints/ai_query_router.py`)
- `POST /ai-query` — Auto-classifies query as `customers` or `merchants`, prepares data preview, and returns structured analysis (JSON-first). Includes safe JSON parsing.
- `POST /customers/ai-query` — Customer-specific analysis
- `POST /merchants/ai-query` — Merchant-specific analysis

---

## 🖥️ Frontend Routes (`src/App.jsx`)

- `/` → redirects to `/merchants`
- `/merchants` — `MerchantsListing`
- `/consumers` — `ConsumersListing`
- `/merchants-dashboard` — `MerchantsDashboard`
- `/consumer-dashboard` — `ConsumerDashboard`
- `/merchants/:merchantId` — `Merchant-Detail`
- `/consumers/:customerId` — `Consumer-Detail`

The UI uses **Material UI** for layout and **Nivo** for charts:
- `TopMerchantsBar`, `PaymentStatusPie`, `MonthlyCollectionsLine`

---

## 🧠 Trust Score & Loyalty Logic

- Merchant trust score blends repayment, defaults, disputes, engagement, compliance, responsiveness, and small boosts for exclusivity and very high volume.
- Customer trust score weighs on-time repayment, defaults, and disputes.
- Loyalty tiers: `Platinum (≥95)`, `Gold (≥90)`, `Silver (≥80)`, else `Bronze`.
- AI summaries and recommendations are requested via OpenAI with strict JSON/text constraints and robust fallbacks for reliability.

---

## 🔐 Environment

Create `backend/.env`:
```
OPENAI_API_KEY=your_api_key_here
```
If no key or quota issues occur, endpoints gracefully fall back to deterministic logic and canned insights.

---

## 🧪 Testing

- `backend/test_ai_integration.py` contains basic integration tests for AI flows (adjust API key and quotas as needed).

---

## 🧰 Troubleshooting

- Port already in use: stop previous processes or change ports, then re-run
- No `.env` detected: create `backend/.env` with `OPENAI_API_KEY`
- Empty charts/data: ensure CSVs exist in `backend/app/data/` or regenerate via data generators, then restart the backend to re-seed SQLite
- CORS issues: `main.py` enables localhost:5173; adjust origins if your frontend runs elsewhere

---

## 👥 Contributors

- Tarun Bhartiya
- Neel Khalade
- Jyoti Parkash

---

## 📜 License

For hackathon/demo use. Add a license of your choice for wider distribution.
