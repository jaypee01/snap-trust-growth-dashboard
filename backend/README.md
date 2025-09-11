# Snap Trust & Growth Dashboard

**Hackathon 2025 Project** – A dashboard to track **merchant and customer trust scores, loyalty tiers, historical trends, and AI-generated insights**. Built with **FastAPI (backend)** and **React + Vite (frontend)** using synthetic CSV data.

---

## 🚀 Quick Overview

* **Backend:** FastAPI REST APIs serving trust scores, loyalty tiers, historical trends, benchmarks, AI-generated summaries, recommendations, and natural language queries.
* **Frontend:** React + Vite dashboard to visualize metrics.
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
│   │   │   ├── merchants.py
│   │   │   ├── customers.py
│   │   │   └── ai_query_router.py
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

````

---

## 🛠️ Setup Instructions

### Backend

1. Clone the repository:

```bash
git clone https://github.com/jaypee01/snap-trust-growth-dashboard.git
cd backend
````

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

Create a `.env` file in the backend root with:

```
OPENAI_API_KEY=your_api_key_here
```

5. **Run the server:**

```bash
uvicorn app.main:app --reload
```

* API base: `http://127.0.0.1:8000`
* Interactive docs: `http://127.0.0.1:8000/docs`

---

### Frontend

1. Navigate to frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the frontend server:

```bash
npm run dev
```

* Dashboard available at the printed URL (usually `http://localhost:5173`)

---

## 🛠️ API Endpoints

### Merchants

* `GET /merchants` — List all merchants (summary only)
* `GET /merchants/{merchant_id}` — Full metrics with optional AI fields: `Summary`, `Explanation`, `History`, `Recommendations`, `Benchmark`
* `GET /merchants/{merchant_id}/summary/explain` — Explanation for TrustScore & LoyaltyTier
* `GET /merchants/{merchant_id}/history` — Historical trends
* `GET /merchants/{merchant_id}/benchmark` — Compare metrics against peers
* `GET /merchants/{merchant_id}/recommendations` — AI-generated actionable recommendations

### Customers

* `GET /customers` — List all customers (summary only)
* `GET /customers/{customer_id}` — Full metrics with optional AI fields: `Summary`, `Explanation`, `History`, `Recommendations`
* `GET /customers/{customer_id}/summary/explain` — Explanation for TrustScore & LoyaltyTier
* `GET /customers/{customer_id}/history` — Historical trends
* `GET /customers/{customer_id}/recommendations` — AI-generated actionable recommendations

### AI Query (Natural Language)

* `POST /ai-query/` — Single endpoint for **any natural language query** about merchants or customers.

**Request Body Example:**

```json
{
  "query": "Show top 10 customers by TrustScore and their loyalty tiers"
}
```

**Features:**

* Automatically detects if query is about **customers** or **merchants**
* Prepares metrics using `prepare_customer_metrics` or `prepare_merchant_metrics`
* Generates **analysis, summaries, recommendations**, or **filtered/sorted data**
* Returns **readable JSON, HTML, or text** depending on the request

---

## 🎯 Features

* Trust score & loyalty tier calculation
* Historical trend tracking
* AI-powered summaries and recommendations
* Benchmarks against peers
* Natural language query API (`/ai-query`) for flexible analytics
* Synthetic data generation via `dataGenerator/` scripts

---

## 👥 Contributors

* Tarun Bhartiya
* Harneet Chugga
* Neel Khalade
* Jyoti Parkash

---

## ⚠️ Notes

* All data is synthetic for demo purposes
* AI summaries/recommendations require `OPENAI_API_KEY` in `.env`
* CSV files can be regenerated using the scripts in `dataGenerator/`
* Add CORS middleware if connecting frontend on a different port

```