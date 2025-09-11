# Snap Trust & Growth Dashboard Backend

This is the backend API for the **Snap Trust & Growth Dashboard** hackathon project.
It is built with **Python FastAPI** and serves trust scores, loyalty tiers, AI-generated summaries, historical metrics, benchmarks, and recommendations for **merchants** and **customers** using mock CSV data.

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
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the backend root (next to `main.py`) with:

```
OPENAI_API_KEY=your_api_key_here
```

### 5. Add Data Files

Place CSV files in `app/data/`:

* `merchants_loyalty.csv`
* `payments.csv`

Sample CSVs are already included in `app/data/`.

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

* API base: `http://127.0.0.1:8000`
* Interactive docs: `http://127.0.0.1:8000/docs`

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
│   │   │   ├── merchants.py
│   │   │   ├── customers.py
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

* `GET /merchants` — List all merchants (summary only):

  * `MerchantID`, `MerchantName`, `ExclusivityFlag`, `TrustScore`, `LoyaltyTier`

* `GET /merchants/{merchant_id}` — Full metrics for a merchant:

  * Core metrics: `RepaymentRate`, `DisputeRate`, `DefaultRate`, `TransactionVolume`, `TenureMonths`
  * Engagement metrics: `EngagementScore`, `ComplianceScore`, `ResponsivenessScore`, `ExclusivityFlag`
  * Derived metrics: `TrustScore`, `LoyaltyTier`
  * Optional AI fields: `Benchmark`, `Recommendations`, `Explanation`, `History`

* `GET /merchants/{merchant_id}/summary/explain` — Explanation for TrustScore & LoyaltyTier.

* `GET /merchants/{merchant_id}/history` — Historical trends of TrustScore, EngagementScore, ComplianceScore.

* `GET /merchants/{merchant_id}/benchmark` — Compare merchant metrics against peers.

* `GET /merchants/{merchant_id}/recommendations` — AI-generated actionable recommendations to improve performance.

### Customers

* `GET /customers` — List all customers (summary only):

  * `CustomerID`, `CustomerName`, `TrustScore`, `LoyaltyTier`

* `GET /customers/{customer_id}` — Full metrics for a customer:

  * Core metrics: `RepaymentRate`, `DisputeCount`, `DefaultRate`, `TransactionVolume`
  * Derived metrics: `TrustScore`, `LoyaltyTier`
  * Optional AI fields: `Recommendations`, `Explanation`, `History`

* `GET /customers/{customer_id}/summary/explain` — Explanation for TrustScore & LoyaltyTier.

* `GET /customers/{customer_id}/history` — Historical trends of TrustScore, disputes, defaults.

* `GET /customers/{customer_id}/recommendations` — AI-generated actionable recommendations.

### Leaderboard (sorted by TrustScore)

* `GET /leaderboard/merchants?sort_order=asc|desc&limit=10` — Top merchants summary.
* `GET /leaderboard/customers?sort_order=asc|desc&limit=10` — Top customers summary.

---

## ⚙️ How It Works

* Reads merchant and customer data from CSV files.
* Computes TrustScore and LoyaltyTier dynamically if not present.
* Uses AI (OpenAI) for summaries and recommendations if `OPENAI_API_KEY` is set.
* Provides REST APIs for dashboard consumption.

---

## 🔗 Frontend

Pair with the React + Vite frontend in the `frontend/` directory for a full dashboard experience.

---

## 📝 Notes

* All data is mock/synthetic for demo purposes.
* You can expand CSVs, scoring logic, or AI prompts to improve realism.
* Add CORS middleware if connecting to a frontend running on a different port.

---