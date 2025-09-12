## Charts for Loan-Service MVP

This file outlines core and optional charts to build from the mock datasets and how to compute each at a high level.

## Datasets
- merchants.csv: merchant_id, merchant_name, category, city, state, onboard_date, risk_tier, avg_ticket_size, monthly_gmv_est
- customers.csv: customer_id, full_name, age, gender, city, state, primary_merchant_id, income_band, kyc_status
- loans.csv: loan_id, customer_id, merchant_id, disbursed_date, principal, tenure_months, annual_interest_rate, emi_amount, status
- payments.csv: payment_id, loan_id, due_date, paid_date, amount_due, amount_paid, status (ON_TIME/LATE/MISSED), days_past_due

## Core charts
1) Top 10 merchants by total principal (bar)
- Purpose: Identify largest disbursers.
- Compute: Sum loans.principal grouped by merchant_id; sort desc; top 10. Join merchant_name for labels.

2) Payment status mix (overall) (pie)
- Purpose: Portfolio health snapshot.
- Compute: Count payments.status across all rows: ON_TIME, LATE, MISSED. Use shares (%) for the pie.

3) Monthly collections: expected vs received (line)
- Purpose: Track cash flow vs plan.
- Compute: For payments, group by month(due_date). expected = sum(amount_due); received = sum(amount_paid). Plot two lines.

4) Delinquency trend (30+/60+/90+) (line)
- Purpose: Monitor risk over time.
- Compute: Derive bucket by days_past_due: 30+, 60+, 90+. Group by month(due_date) × bucket; plot three lines.

5) Interest rate distribution (histogram)
- Purpose: Pricing spread overview.
- Compute: Histogram of loans.annual_interest_rate (e.g., 10–30% with ~10–20 bins).

## Optional charts
- Payment status mix per merchant (stacked bar)
  - Count payments.status per merchant (join via payments.loan_id → loans.merchant_id).
- Risk × outcome matrix (heat/table)
  - For each merchants.risk_tier, compute delinquency rate = MISSED payments / total payments.
- Cohort default rate by disbursed month (line/bar)
  - Cohort on month(loans.disbursed_date); default rate = share of loans with any MISSED payment.
- Loan amount vs income band (box/hist)
  - Distribution of loans.principal by customers.income_band (join via customer_id).
- On-time % distribution (hist)
  - For each customer, on_time_rate = ON_TIME / total payments; plot histogram.
- Loan status mix (donut)
  - Share of loans.status: ACTIVE, CLOSED, DEFAULTED.

## Implementation notes
- Chart libs: Recharts, ECharts, or Chart.js.
- Data source: For MVP, load CSVs at app init or via simple API endpoints.
- Filtering: Support merchant, status, date range; recompute aggregates client-side for small datasets.

## Reference
- Shared chat (spec and mock data context): [Loan-service MVP conversation](https://chatgpt.com/share/68c1653e-8d50-8000-9ff4-ece9b400b10a)
