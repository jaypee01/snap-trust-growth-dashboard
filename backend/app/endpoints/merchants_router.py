import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List, Literal
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
MERCHANT_SUMMARY_FIELDS = ["MerchantID", "MerchantName", "ExclusivityFlag", "TrustScore", "LoyaltyTier", "Summary"]
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

    def compute_scores(row):
        trust = calculate_merchant_trust_score(
            row["RepaymentRate"], row["DisputeRate"], row["DefaultRate"],
            row["TransactionVolume"], row["EngagementScore"],
            row["ComplianceScore"], row["ResponsivenessScore"],
            row.get("ExclusivityFlag", 0)
        )
        return pd.Series({
            "TrustScore": trust,
            "LoyaltyTier": assign_loyalty_tier(trust)
        })

    scores = df.apply(compute_scores, axis=1)
    df["TrustScore"] = scores["TrustScore"]
    df["LoyaltyTier"] = scores["LoyaltyTier"]

    return df

ALLOWED_SORT_BY = ["TrustScore", "LoyaltyTier"]
ALLOWED_SORT_ORDER = ["asc", "desc"]

# ------------------------------
# Merchant Endpoints
# ------------------------------
@router.get("/", summary="Get Merchants with Trust & Loyalty Info")
def get_merchants(
    limit: int = Query(10, ge=1),
    sort_by: str = Query("TrustScore,LoyaltyTier", description="Columns to sort by, comma separated. Allowed: TrustScore,LoyaltyTier"),
    sort_order: str = Query("desc,desc", description="Sort order for each column, comma separated. Allowed: asc,desc")
) -> List[dict]:
    import pandas as pd

    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)

    # Map LoyaltyTier to numeric
    loyalty_mapping = {"Platinum": 4, "Gold": 3, "Silver": 2, "Bronze": 1}
    df["LoyaltyScore"] = df["LoyaltyTier"].map(loyalty_mapping)

    # Split and validate input
    sort_by_list = [s.strip() for s in sort_by.split(",")]
    sort_order_list = [s.strip().lower() for s in sort_order.split(",")]

    if len(sort_by_list) != len(sort_order_list):
        raise HTTPException(status_code=400, detail="sort_by and sort_order must have same number of elements")

    sort_columns = []
    ascending_list = []
    for col, order in zip(sort_by_list, sort_order_list):
        if col not in ALLOWED_SORT_BY:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by value: {col}")
        if order not in ALLOWED_SORT_ORDER:
            raise HTTPException(status_code=400, detail=f"Invalid sort_order value: {order}")

        if col == "LoyaltyTier":
            sort_columns.append("LoyaltyScore")
        else:
            sort_columns.append(col)

        ascending_list.append(order == "asc")

    if sort_columns:
        df = df.sort_values(sort_columns, ascending=ascending_list)

    results = df[["MerchantID", "MerchantName", "ExclusivityFlag", "TrustScore", "LoyaltyTier"]].head(limit).to_dict(orient="records")
    return results

@router.get("/{merchant_id}", summary="Get Merchant Full Metrics with Recommendations")
def get_merchant_details(merchant_id: str) -> dict:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    data = row.iloc[0].to_dict()

    result = {field: data[field] for field in MERCHANT_OUTPUT_FIELDS_ORDER}
    result["Summary"] = generate_summary("merchant", data)
    result["Recommendations"] = generate_merchant_recommendations(data)
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
    df = prepare_merchant_metrics(df)
    row = df[df["MerchantID"] == merchant_id]
    if row.empty:
        raise HTTPException(404, "Merchant not found")
    data = row.iloc[0].to_dict()

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

@router.get("/metrics/averages", summary="Get Overall Average Merchant Metrics")
def get_merchant_averages() -> dict:
    """
    Returns overall average metrics across all merchants,
    including repayment, disputes, defaults, engagement,
    compliance, responsiveness, and trust.
    """
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)

    averages = {
        "AverageRepaymentRate": round(df["RepaymentRate"].mean(), 2),
        "AverageDisputeRate": round(df["DisputeRate"].mean(), 2),
        "AverageDefaultRate": round(df["DefaultRate"].mean(), 2),
        "AverageTransactionVolume": round(df["TransactionVolume"].mean(), 2),
        "AverageTenureMonths": round(df["TenureMonths"].mean(), 2),
        "AverageEngagementScore": round(df["EngagementScore"].mean(), 2),
        "AverageComplianceScore": round(df["ComplianceScore"].mean(), 2),
        "AverageResponsivenessScore": round(df["ResponsivenessScore"].mean(), 2),
        "AverageTrustScore": round(df["TrustScore"].mean(), 2),
    }

    return averages



