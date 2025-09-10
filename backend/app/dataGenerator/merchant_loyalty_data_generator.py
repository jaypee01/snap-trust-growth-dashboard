"""
merchants_loyalty_generator.py

Generates synthetic merchant loyalty data for testing Snap Trust & Growth Dashboard.

Features generated per merchant:
- MerchantID, MerchantName
- RepaymentRate (0.7–0.98)
- DisputeRate (0.01–0.15)
- DefaultRate (0.01–0.22)
- TransactionVolume (2,000–10,000)
- TenureMonths (1–36 months)
- EngagementScore (0.3–1.0)
- ComplianceScore (0.6–1.0)
- ResponsivenessScore (0.4–1.0)
- ExclusivityFlag (0 or 1, ~50/50 split)

Output:
    app/data/merchants_loyalty.csv
"""

import pandas as pd
import numpy as np

# Seed ensures reproducibility
np.random.seed(42)

# Configurable parameters
num_merchants = 100  # total merchants to generate

# Generate IDs like M001, M002... and names like Merchant A1, Merchant B2
merchant_ids = [f"M{str(i+1).zfill(3)}" for i in range(num_merchants)]
merchant_names = [f"Merchant {chr(65 + (i % 26))}{i+1}" for i in range(num_merchants)]

# Generate synthetic metrics
repayment_rate = np.round(np.random.uniform(0.7, 0.98, num_merchants), 2)
dispute_rate = np.round(np.random.uniform(0.01, 0.15, num_merchants), 2)
default_rate = np.round(np.random.uniform(0.01, 0.22, num_merchants), 2)
transaction_volume = np.random.randint(2000, 10000, num_merchants)
tenure_months = np.random.randint(1, 36, num_merchants)
engagement_score = np.round(np.random.uniform(0.3, 1.0, num_merchants), 2)
compliance_score = np.round(np.random.uniform(0.6, 1.0, num_merchants), 2)
responsiveness_score = np.round(np.random.uniform(0.4, 1.0, num_merchants), 2)
exclusivity_flag = np.random.choice([0, 1], num_merchants, p=[0.5, 0.5])

# Assemble into DataFrame
df = pd.DataFrame({
    "MerchantID": merchant_ids,
    "MerchantName": merchant_names,
    "RepaymentRate": repayment_rate,
    "DisputeRate": dispute_rate,
    "DefaultRate": default_rate,
    "TransactionVolume": transaction_volume,
    "TenureMonths": tenure_months,
    "EngagementScore": engagement_score,
    "ComplianceScore": compliance_score,
    "ResponsivenessScore": responsiveness_score,
    "ExclusivityFlag": exclusivity_flag
})

# Save to CSV
output_path = "app/data/merchants_loyalty.csv"
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df)} merchants at {output_path}")
print(df.head())
