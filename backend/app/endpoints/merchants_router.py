import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict
from ..utils import (
    calculate_merchant_trust_score,
    assign_loyalty_tier,
    generate_summary,
    generate_merchant_recommendations
)

router = APIRouter()

# ------------------------------
# Field definitions
# ------------------------------
MERCHANT_SUMMARY_FIELDS = ["MerchantID", "MerchantName", "ExclusivityFlag", "TrustScore", "Summary"]
MERCHANT_OUTPUT_FIELDS_ORDER = [
    "MerchantID", "MerchantName", "RepaymentRate", "DisputeRate", "DefaultRate",
    "TransactionVolume", "TenureMonths", "EngagementScore", "ComplianceScore",
    "ResponsivenessScore", "ExclusivityFlag", "TrustScore", "LoyaltyTier"
]

# ------------------------------
# Helper Functions
# ------------------------------
def prepare_merchant_metrics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "RepaymentRate", "DisputeRate", "DefaultRate", "TransactionVolume",
        "EngagementScore", "ComplianceScore", "ResponsivenessScore"
    ]
    df[numeric_cols] = df[numeric_cols].round(2)
    if "TrustScore" not in df.columns or df["TrustScore"].isnull().any():
        df["TrustScore"] = df.apply(
            lambda row: calculate_merchant_trust_score(
                row["RepaymentRate"], row["DisputeRate"], row["DefaultRate"],
                row["TransactionVolume"], row["EngagementScore"],
                row["ComplianceScore"], row["ResponsivenessScore"],
                row.get("ExclusivityFlag", 0)
            ),
            axis=1
        )
    if "LoyaltyTier" not in df.columns or df["LoyaltyTier"].isnull().any():
        df["LoyaltyTier"] = df["TrustScore"].apply(assign_loyalty_tier)
    return df

# ------------------------------
# Merchant Endpoints
# ------------------------------
@router.get("/", summary="Get Merchants with Trust & Loyalty Info")
def get_merchants(
    limit: int = Query(10),
    sort_order: str = Query("desc")
) -> List[dict]:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    ascending = sort_order == "asc"
    df = df.sort_values("TrustScore", ascending=ascending).head(limit)

    # No Summary in list API
    results = df[["MerchantID", "MerchantName", "ExclusivityFlag", "TrustScore", "LoyaltyTier"]].to_dict(orient="records")
    return results


@router.get("/{merchant_id}", summary="Get Merchant Full Metrics")
def get_merchant_details(merchant_id: str) -> dict:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    data = row.iloc[0].to_dict()

    result = {field: data[field] for field in MERCHANT_OUTPUT_FIELDS_ORDER}
    result["Summary"] = generate_summary("merchant", data)  # <-- add summary only here
    return result
    
@router.get("/{merchant_id}/summary/explain", summary="Explain Merchant Scores/Tiers")
def explain_merchant_summary(merchant_id: str) -> dict:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    data = row.iloc[0].to_dict()
    explanation = generate_summary("merchant", data)
    return {"MerchantID": merchant_id, "Explanation": explanation}

@router.get("/{merchant_id}/history", summary="Merchant Historical Metrics")
def merchant_history(merchant_id: str) -> dict:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)  # <-- important, adds TrustScore and LoyaltyTier
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    data = row.iloc[0].to_dict()
    
    # Simple demo history (replace with real historical data if available)
    history = {
        "TrustScore": [max(data["TrustScore"] - i * 2, 0) for i in range(5)],
        "EngagementScore": [max(data["EngagementScore"] - i * 0.05, 0) for i in range(5)],
        "ComplianceScore": [max(data["ComplianceScore"] - i * 0.03, 0) for i in range(5)]
    }
    return {"MerchantID": merchant_id, "History": history}

@router.get("/{merchant_id}/benchmark", summary="Merchant Benchmark Against Peers")
def merchant_benchmark(merchant_id: str):
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    merchant = row.iloc[0].to_dict()
    benchmarks = df.describe().to_dict()
    return {"MerchantID": merchant_id, "MerchantMetrics": merchant, "Benchmarks": benchmarks}

@router.get("/{merchant_id}/recommendations", summary="Merchant Recommendations")
def merchant_recommendations(merchant_id: str):
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    merchant = row.iloc[0].to_dict()
    recommendations = generate_merchant_recommendations(merchant)
    return {"MerchantID": merchant_id, "Recommendations": recommendations}
