import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List
from ..utils import (
    get_customer_trust_loyalty,   # formula-based
    generate_summary,
    generate_customer_recommendations
)

router = APIRouter()

# ------------------------------
# Field definitions
# ------------------------------
CUSTOMER_SUMMARY_FIELDS = ["CustomerID", "CustomerName", "TrustScore", "LoyaltyTier", "Summary"]
CUSTOMER_FULL_FIELDS_ORDER = [
    "CustomerID",
    "CustomerName",
    "RepaymentRate",
    "DisputeCount",
    "DefaultRate",
    "TransactionVolume",
    "TrustScore",
    "LoyaltyTier",
]

# ------------------------------
# Helper function
# ------------------------------
def prepare_customer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["CustomerID", "CustomerName"])
    customers = grouped.agg(
        RepaymentRate=("PaymentStatus", lambda x: (x == "PAID").mean()),
        DisputeCount=("DisputeFlag", "sum"),
        DefaultRate=("DefaultFlag", "mean"),
        TransactionVolume=("PaymentAmount", "sum")
    ).reset_index()

    customers["TransactionVolume"] = customers["TransactionVolume"].round(0).astype(int)
    customers[["RepaymentRate", "DefaultRate"]] = customers[["RepaymentRate", "DefaultRate"]].round(2)

    # ------------------------------
    # Formula-based TrustScore & LoyaltyTier
    # ------------------------------
    trust_loyalty_results = customers.apply(
        lambda row: get_customer_trust_loyalty(
            row["RepaymentRate"], row["DisputeCount"], row["DefaultRate"]
        ),
        axis=1
    )

    customers["TrustScore"] = trust_loyalty_results.apply(lambda x: x["TrustScore"])
    customers["LoyaltyTier"] = trust_loyalty_results.apply(lambda x: x["LoyaltyTier"])

    return customers

# ------------------------------
# Customers Endpoints
# ------------------------------
@router.get("/", summary="Get Customers with Trust & Loyalty Info")
def get_customers(limit: int = Query(10), sort_order: str = Query("desc", regex="^(asc|desc)$")) -> List[dict]:
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)
    ascending = sort_order == "asc"
    customers = customers.sort_values(by="TrustScore", ascending=ascending).head(limit)

    results = customers[["CustomerID", "CustomerName", "TrustScore", "LoyaltyTier"]].to_dict(orient="records")
    return results

@router.get("/{customer_id}", summary="Get Customer Full Metrics with Recommendations")
def get_customer_details(customer_id: str) -> dict:
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)
    row = customers[customers["CustomerID"] == customer_id]

    if row.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_data = row.iloc[0].to_dict()
    result = {field: customer_data[field] for field in CUSTOMER_FULL_FIELDS_ORDER}
    result["Summary"] = generate_summary("customer", customer_data)
    result["Recommendations"] = generate_customer_recommendations(customer_data)
    return result

@router.get("/{customer_id}/summary/explain", summary="Explain Customer TrustScore & LoyaltyTier")
def explain_customer_summary(customer_id: str) -> dict:
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)
    row = customers[customers["CustomerID"] == customer_id]

    if row.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    data = row.iloc[0].to_dict()
    explanation = generate_summary("customer", data)
    return {"CustomerID": data["CustomerID"], "Explanation": explanation}

@router.get("/{customer_id}/history", summary="Customer Historical Metrics")
def customer_history(customer_id: str) -> dict:
    df = pd.read_csv("app/data/payments.csv")
    customer_df = df[df["CustomerID"] == customer_id].sort_values("PaymentDate")

    if customer_df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    history = customer_df.groupby("PaymentDate").agg(
        RepaymentRate=("PaymentStatus", lambda x: (x == "PAID").mean()),
        DisputeCount=("DisputeFlag", "sum"),
        DefaultRate=("DefaultFlag", "mean"),
        TransactionVolume=("PaymentAmount", "sum")
    ).reset_index()

    # Formula-based TrustScore & LoyaltyTier
    trust_loyalty_results = history.apply(
        lambda row: get_customer_trust_loyalty(
            row["RepaymentRate"], row["DisputeCount"], row["DefaultRate"]
        ),
        axis=1
    )
    history["TrustScore"] = trust_loyalty_results.apply(lambda x: x["TrustScore"])
    history["LoyaltyTier"] = trust_loyalty_results.apply(lambda x: x["LoyaltyTier"])

    return {"CustomerID": customer_id, "History": history.to_dict(orient="records")}

@router.get("/{customer_id}/recommendations", summary="Customer Recommendations")
def customer_recommendations(customer_id: str):
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)
    row = customers[customers["CustomerID"] == customer_id]

    if row.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    data = row.iloc[0].to_dict()
    recommendations = generate_customer_recommendations(data)
    return {"CustomerID": customer_id, "Recommendations": recommendations}
