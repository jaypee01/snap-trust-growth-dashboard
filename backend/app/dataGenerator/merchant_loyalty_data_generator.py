from utils import calculate_merchant_trust_score, assign_loyalty_tier, assign_risk_score

# Calculate additional fields
trust_scores = [
    calculate_merchant_trust_score(
        r, d, df_val, t, e, c, resp, ex
    ) for r, d, df_val, t, e, c, resp, ex in zip(
        repayment_rate, dispute_rate, default_rate, transaction_volume,
        engagement_score, compliance_score, responsiveness_score, exclusivity_flag
    )
]

loyalty_tiers = [assign_loyalty_tier(ts) for ts in trust_scores]
risk_scores = [
    assign_risk_score(ts, df_val, d) for ts, df_val, d in zip(trust_scores, default_rate, dispute_rate)
]

# Placeholder summaries, benchmark, recommendations
summaries = [f"{name} has a TrustScore of {ts} and is {tier}" 
             for name, ts, tier in zip(merchant_names, trust_scores, loyalty_tiers)]
benchmarks = ["Top 10% in sector" for _ in range(num_merchants)]
recommendations = [["Increase engagement", "Reduce disputes"] for _ in range(num_merchants)]

# Add to DataFrame
df["TrustScore"] = trust_scores
df["LoyaltyTier"] = loyalty_tiers
df["RiskScore"] = risk_scores
df["Summary"] = summaries
df["Benchmark"] = benchmarks
df["Recommendations"] = recommendations

# Save CSV
df.to_csv(output_path, index=False)
