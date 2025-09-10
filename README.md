# Snap Trust & Growth Dashboard

**Hackathon 2025 Project** – A dashboard to track **merchant and customer trust scores, loyalty tiers, and leaderboards**. Built with **FastAPI (backend)** and **React + Vite (frontend)** using synthetic CSV data.

---

## 🚀 Quick Overview

* **Backend:** FastAPI REST APIs serving trust scores, loyalty tiers, and leaderboard data.
* **Frontend:** React + Vite dashboard to visualize metrics and leaderboards.
* **Data Generator:** Python scripts to generate synthetic data for `merchants_loyalty.csv` and `payments.csv`.

---

## 📁 Repository Structure

```
snap-trust-growth-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── utils.py
│   │   ├── endpoints/
│   │   │   └── leaderboard.py
│   │   ├── data/
│   │   │   ├── merchants_loyalty.csv
│   │   │   └── payments.csv
│   │   └── dataGenerator/
│   │       ├── merchant_loyalty_data_generator.py
│   │       └── payments_data_generator.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── .env
├── .gitignore
└── README.md
```

---

## 🛠️ Setup Instructions

### Backend

1. **Navigate to backend folder:**

```bash
cd backend
```

2. **Create virtual environment & activate:**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a .env file in the backend root (next to main.py) with content like:

OPENAI_API_KEY=your_api_key_here

5. **Run the server:**

```bash
uvicorn app.main:app --reload
```

* API base: `http://127.0.0.1:8000`
* Interactive docs: `http://127.0.0.1:8000/docs`

---

### Frontend

1. **Navigate to frontend folder:**

```bash
cd frontend
```

2. **Install dependencies:**

```bash
npm install
```

3. **Run the frontend server:**

```bash
npm run dev
```

* Dashboard available at the printed URL (usually `http://localhost:5173`)

---

## 🛠️ API Endpoints

### Merchants

* `GET /merchants` — List all merchants (summary only) with fields:

  * `MerchantID` — Unique merchant identifier
  * `MerchantName` — Name of the merchant
  * `ExclusivityFlag` — 1 if exclusive partner, 0 otherwise
  * `TrustScore` — Calculated composite trust score
  * `LoyaltyTier` — Tier assigned based on TrustScore (e.g., Gold, Silver)

* `GET /merchants/{merchant_id}` — Get full metrics for a specific merchant by ID, including:

  * `MerchantID`
  * `MerchantName`
  * `RepaymentRate`
  * `DisputeRate`
  * `DefaultRate`
  * `TransactionVolume`
  * `TenureMonths`
  * `EngagementScore`
  * `ComplianceScore`
  * `ResponsivenessScore`
  * `ExclusivityFlag`
  * `TrustScore`
  * `LoyaltyTier`

### Customers

* `GET /customers` — List all customers (summary only) with fields:

  * `CustomerID` — Unique customer identifier
  * `CustomerName` — Name of the customer
  * `TrustScore` — Calculated composite trust score
  * `LoyaltyTier` — Tier assigned based on TrustScore (e.g., Gold, Silver)

* `GET /customers/{customer_id}` — Get full metrics for a specific customer by ID, including:

  * `CustomerID`
  * `CustomerName`
  * `RepaymentRate`
  * `DisputeCount`
  * `DefaultRate`
  * `TransactionVolume`
  * `TrustScore`
  * `LoyaltyTier`

### Leaderboard (sorted by TrustScore)

* `GET /leaderboard/merchants?sort_order=asc|desc&limit=10` — Returns top merchants sorted by `TrustScore` (summary fields only).
* `GET /leaderboard/customers?sort_order=asc|desc&limit=10` — Returns top customers sorted by `TrustScore` (summary fields only).

---

## 🎯 Features

* Trust score & loyalty tier calculation for merchants & customers
* Leaderboards with sorting & filtering
* Synthetic data generated via `dataGenerator/` scripts
* Designed for hackathon/demo use

---

## 👥 Contributors

* Tarun Bhartiya
* Harneet Chugga
* Neel Khalade
* Jyoti Parkash

---

## ⚠️ Notes

* Data is synthetic for demo purposes.
* Add CORS middleware if connecting frontend on a different port.
* CSV files can be regenerated using the scripts in `dataGenerator/`.

---
