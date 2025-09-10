import pandas as pd
from fastapi import APIRouter, Query
from typing import Optional
from ..utils import calculate_customer_trust_score, calculate_merchant_trust_score, assign_loyalty_tier

router = APIRouter()

@router.get(
    "/customers",
    summary="Get Customers with Trust & Loyalty Info",
    description="""
    Retrieves customers with calculated TrustScore and LoyaltyTier.  

    Supports:
    - **limit** (int): Number of records to return (default = 10).  
    - **sort_order** (asc/desc): Sort by TrustScore ascending or descending (default = desc).  
    """
)
def get_customers(
    limit: int = Query(10, description="Number of customers to return"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order for TrustScore"),
):
    df = pd.read_csv("app/data/payments.csv")

    grouped = df.groupby(["CustomerID", "CustomerName"])
    customers = grouped.agg(
        RepaymentRate=("PaymentStatus", lambda x: (x == "PAID").sum() / len(x)),
        DisputeCount=("DisputeFlag", "sum"),
        DefaultRate=("DefaultFlag", "mean"),
        TransactionVolume=("PaymentAmount", "sum")
    ).reset_index()

    customers["TransactionVolume"] = customers["TransactionVolume"].round(0).astype(int)
    customers[["RepaymentRate", "DefaultRate"]] = customers[["RepaymentRate", "DefaultRate"]].round(2)

    customers["TrustScore"] = customers.apply(
        lambda row: calculate_customer_trust_score(
            row["RepaymentRate"], row["DisputeCount"], row["DefaultRate"]
        ),
        axis=1
    )
    customers["LoyaltyTier"] = customers["TrustScore"].apply(assign_loyalty_tier)

    # Sorting
    ascending = sort_order == "asc"
    customers = customers.sort_values(by="TrustScore", ascending=ascending).head(limit)

    return customers.to_dict(orient="records")


@router.get(
    "/merchants",
    summary="Get Merchants with Trust & Loyalty Info",
    description="""
    Retrieves merchants with calculated TrustScore and LoyaltyTier.  

    Supports:
    - **limit** (int): Number of records to return (default = 10).  
    - **sort_order** (asc/desc): Sort by TrustScore ascending or descending (default = desc).  
    """
)
def get_merchants(
    limit: int = Query(10, description="Number of merchants to return"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order for TrustScore"),
):
    df = pd.read_csv("app/data/merchants_loyalty.csv")

    numeric_cols = [
        "RepaymentRate", "DisputeRate", "DefaultRate",
        "TransactionVolume", "EngagementScore", "ComplianceScore", "ResponsivenessScore"
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

    # Sorting
    ascending = sort_order == "asc"
    df = df.sort_values(by="TrustScore", ascending=ascending).head(limit)

    return df.to_dict(orient="records")
