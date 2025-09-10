"""
payments_data_generator.py

Generates synthetic payments data for customers and merchants using Faker.

- Creates a configurable number of records with:
  * Customer and Merchant IDs & names
  * Payment IDs and dates within 2024
  * Payment amounts (50–500 range)
  * Payment status (PAID or FAILED)
  * Dispute and default flags

Output:
    app/data/payments.csv
"""

import pandas as pd
import random
from faker import Faker
from datetime import date

# Initialize Faker and seed for reproducibility
fake = Faker()
random.seed(42)
Faker.seed(42)

# Configurable parameters
num_records = 1000      # Total number of payment transactions
num_customers = 50      # Number of unique customers
num_merchants = 20      # Number of unique merchants

# Generate synthetic customers and merchants
customers = [(f"C{i+1:03d}", fake.name()) for i in range(num_customers)]
merchants = [(f"M{i+1:03d}", fake.company()) for i in range(num_merchants)]

rows = []
for i in range(num_records):
    cust_id, cust_name = random.choice(customers)
    merch_id, merch_name = random.choice(merchants)

    payment_id = f"P{i+1:04d}"  # Payment ID like P0001
    payment_date = fake.date_between(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
    payment_amount = round(random.uniform(50, 500), 2)

    # Assign payment status with 90% PAID and 10% FAILED
    payment_status = random.choices(["PAID", "FAILED"], weights=[0.9, 0.1])[0]

    # Small probability of dispute (5%)
    dispute_flag = random.choices([0, 1], weights=[0.95, 0.05])[0]

    # DefaultFlag = 1 only if FAILED
    default_flag = 1 if payment_status == "FAILED" else 0

    rows.append([
        payment_id, cust_id, cust_name, merch_id, merch_name,
        payment_date, payment_amount, payment_status, dispute_flag, default_flag
    ])

# Build DataFrame
df = pd.DataFrame(rows, columns=[
    "PaymentID", "CustomerID", "CustomerName", "MerchantID", "MerchantName",
    "PaymentDate", "PaymentAmount", "PaymentStatus", "DisputeFlag", "DefaultFlag"
])

# Save to CSV
output_path = "app/data/payments.csv"
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df)} payment records at {output_path}")
