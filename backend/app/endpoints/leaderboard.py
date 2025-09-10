import pandas as pd
from fastapi import APIRouter, Query, HTTPException
from typing import List
from ..utils import (
    calculate_customer_trust_score,
    calculate_merchant_trust_score,
    assign_loyalty_tier,
)

router = APIRouter()

# ------------------------------
# Field definitions and documentation
# ------------------------------

# Merchants
MERCHANT_SUMMARY_FIELDS = ["MerchantID", "MerchantName", "ExclusivityFlag", "TrustScore", "LoyaltyTier"]
MERCHANT_OUTPUT_FIELDS_ORDER = [
    "MerchantID",           # Unique merchant identifier
    "MerchantName",         # Name of the merchant
    "RepaymentRate",        # % of transactions that were repaid
    "DisputeRate",          # % of transactions disputed
    "DefaultRate",          # % of transactions defaulted
    "TransactionVolume",    # Total transaction amount handled by merchant
    "TenureMonths",         # Number of months merchant has been active
    "EngagementScore",      # Engagement metric calculated internally
    "ComplianceScore",      # Compliance metric based on regulatory adherence
    "ResponsivenessScore",  # Responsiveness metric to disputes or queries
    "ExclusivityFlag",      # Flag indicating exclusive partner (1 = Yes, 0 = No)
    "TrustScore",           # Composite score derived from above metrics
    "LoyaltyTier"           # Tier assigned based on TrustScore (e.g., Gold, Silver)
]

# Customers
CUSTOMER_SUMMARY_FIELDS = ["CustomerID", "CustomerName", "TrustScore", "LoyaltyTier"]
CUSTOMER_FULL_FIELDS_ORDER = [
    "CustomerID",           # Unique customer identifier
    "CustomerName",         # Name of the customer
    "RepaymentRate",        # % of payments successfully repaid
    "DisputeCount",         # Number of payment disputes raised
    "DefaultRate",          # % of payments defaulted
    "TransactionVolume",    # Total payment amount made by customer
    "TrustScore",           # Composite score derived from above metrics
    "LoyaltyTier"           # Tier assigned based on TrustScore (e.g., Gold, Silver)
]

# ------------------------------
# Helper functions
# ------------------------------
def prepare_customer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate payment data to calculate customer metrics, TrustScore, and LoyaltyTier.

    Args:
        df (pd.DataFrame): Raw payments dataframe.

    Returns:
        pd.DataFrame: Dataframe with calculated metrics and scores for each customer.
    """
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
        lambda row: calculate_customer_trust_score(row["RepaymentRate"], row["DisputeCount"], row["DefaultRate"]),
        axis=1
    )
    customers["LoyaltyTier"] = customers["TrustScore"].apply(assign_loyalty_tier)
    return customers


def prepare_merchant_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare merchant metrics, calculate TrustScore and LoyaltyTier.

    Args:
        df (pd.DataFrame): Raw merchants dataframe.

    Returns:
        pd.DataFrame: Dataframe with calculated metrics and scores for each merchant.
    """
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
    return df


# ------------------------------
# Customers Endpoints
# ------------------------------
@router.get(
    "/customers",
    summary="Get Customers with Trust & Loyalty Info",
    description="""
    Retrieves customers with calculated TrustScore and LoyaltyTier (summary only).

    Fields returned:
    - CustomerID: Unique customer identifier
    - CustomerName: Name of the customer
    - TrustScore: Composite trust score
    - LoyaltyTier: Tier assigned based on TrustScore
    """
)
def get_customers(
    limit: int = Query(10, description="Number of customers to return"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order for TrustScore"),
) -> List[dict]:
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)

    ascending = sort_order == "asc"
    customers = customers.sort_values(by="TrustScore", ascending=ascending).head(limit)

    return customers[CUSTOMER_SUMMARY_FIELDS].to_dict(orient="records")


@router.get(
    "/customers/{customer_id}",
    summary="Get Customer Full Metrics",
    description="""
    Retrieves all metrics and scores for a specific customer by CustomerID.

    Full Fields:
    - CustomerID
    - CustomerName
    - RepaymentRate
    - DisputeCount
    - DefaultRate
    - TransactionVolume
    - TrustScore
    - LoyaltyTier
    """
)
def get_customer_details(customer_id: str) -> dict:
    df = pd.read_csv("app/data/payments.csv")
    customers = prepare_customer_metrics(df)

    customer_row = customers[customers["CustomerID"] == customer_id]
    if customer_row.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_data = customer_row.iloc[0].to_dict()
    return {field: customer_data[field] for field in CUSTOMER_FULL_FIELDS_ORDER}


# ------------------------------
# Merchants Endpoints
# ------------------------------
@router.get(
    "/merchants",
    summary="Get Merchants with Trust & Loyalty Info",
    description="""
    Retrieves merchants with calculated TrustScore and LoyaltyTier (summary only).

    Fields returned:
    - MerchantID: Unique merchant identifier
    - MerchantName: Name of the merchant
    - ExclusivityFlag: 1 if exclusive partner, 0 otherwise
    - TrustScore: Composite trust score
    - LoyaltyTier: Tier assigned based on TrustScore
    """
)
def get_merchants(
    limit: int = Query(10, description="Number of merchants to return"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order for TrustScore"),
) -> List[dict]:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)

    ascending = sort_order == "asc"
    df = df.sort_values(by="TrustScore", ascending=ascending).head(limit)

    return df[MERCHANT_SUMMARY_FIELDS].to_dict(orient="records")


@router.get(
    "/merchants/{merchant_id}",
    summary="Get Merchant Full Metrics",
    description="""
    Retrieves all metrics and scores for a specific merchant by MerchantID.

    Full Fields:
    - MerchantID
    - MerchantName
    - RepaymentRate
    - DisputeRate
    - DefaultRate
    - TransactionVolume
    - TenureMonths
    - EngagementScore
    - ComplianceScore
    - ResponsivenessScore
    - ExclusivityFlag
    - TrustScore
    - LoyaltyTier
    """
)
def get_merchant_details(merchant_id: str) -> dict:
    df = pd.read_csv("app/data/merchants_loyalty.csv")
    df = prepare_merchant_metrics(df)

    merchant_row = df[df["MerchantID"] == merchant_id]
    if merchant_row.empty:
        raise HTTPException(status_code=404, detail="Merchant not found")

    merchant_data = merchant_row.iloc[0].to_dict()
    return {field: merchant_data[field] for field in MERCHANT_OUTPUT_FIELDS_ORDER}
