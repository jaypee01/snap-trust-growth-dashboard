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

ALLOWED_SORT_BY = ["TrustScore", "LoyaltyTier"]
ALLOWED_SORT_ORDER = ["asc", "desc"]

# ------------------------------
# Customers Endpoints
# ------------------------------
@router.get("/", summary="Get Customers with Trust & Loyalty Info")
def get_customers(
    limit: int = Query(10, ge=1),
    sort_by: str = Query("TrustScore,LoyaltyTier", description="Columns to sort by, comma separated. Allowed: TrustScore,LoyaltyTier"),
    sort_order: str = Query("desc,desc", description="Sort order for each column, comma separated. Allowed: asc,desc")
) -> List[dict]:
    # Load data
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)

    # Map LoyaltyTier to numeric for sorting
    loyalty_mapping = {"Platinum": 4, "Gold": 3, "Silver": 2, "Bronze": 1}
    customers["LoyaltyScore"] = customers["LoyaltyTier"].map(loyalty_mapping)

    # Split and validate query params
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
        customers = customers.sort_values(sort_columns, ascending=ascending_list)

    results = customers[["CustomerID", "CustomerName", "TrustScore", "LoyaltyTier"]].head(limit).to_dict(orient="records")
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
