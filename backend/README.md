# Snap Trust & Growth Dashboard Backend

This is the backend API for the **Snap Trust & Growth Dashboard** hackathon project.
It is built with **Python FastAPI** and serves trust scores, loyalty tiers, and leaderboards for merchants and customers using mock CSV data.

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/jaypee01/snap-trust-growth-dashboard.git
cd backend
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. **Set up environment variables:**

Create a .env file in the backend root (next to main.py) with content like:

OPENAI_API_KEY=your_api_key_here

### 5. Add Data Files

Place your CSV files in `app/data/`:

- `merchants_loyality.csv`
- `payments.csv`

Sample CSVs are already provided in the `app/data/` folder.

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

- API base: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

---

## 📁 Project Structure

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

👉 Full interactive API docs available at `/docs`.

---

## ⚙️ How It Works

- Reads merchant and customer data from CSV files
- Calculates trust scores and loyalty tiers (if not present in CSV)
- Provides REST APIs for use in frontend dashboards

---

## 🔗 Frontend

Pair this backend with the React + Vite frontend in the `frontend/` directory for a complete dashboard experience.

---

## 📝 Notes

- For hackathon/demo purposes, all data is mock/synthetic.
- You can expand the CSVs or scoring logic as needed.
- Add CORS middleware if connecting to a frontend on a different port.
