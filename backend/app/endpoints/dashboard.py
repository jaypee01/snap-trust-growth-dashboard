import sqlite3
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from fastapi import APIRouter, Query

from ..utils import calculate_merchant_trust_score, assign_loyalty_tier


router = APIRouter()

# Match db.py location: app/data/app.db
DB_PATH = Path(__file__).resolve().parent / ".." / "data" / "app.db"
DB_PATH = DB_PATH.resolve()


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


@router.get("/merchants")
def merchants_dashboard(limit: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """
    Returns chart-ready data for the merchants dashboard in one payload.

    - topMerchantsByPayments: [{ merchant, amount }]
    - paymentStatusMix: [{ id, value }]
    - topMerchantTrust: [{ merchant, trustScore, loyaltyTier }]
    """
    with _connect() as conn:
        # Top merchants by total collected payments
        top_merchants_df = pd.read_sql_query(
            """
            SELECT MerchantName AS merchant,
                   ROUND(SUM(PaymentAmount), 2) AS amount
            FROM payments
            GROUP BY MerchantName
            ORDER BY amount DESC
            LIMIT ?
            """,
            conn,
            params=(limit,),
        )

        # Payment status mix
        status_mix_df = pd.read_sql_query(
            """
            SELECT PaymentStatus AS id, COUNT(*) AS value
            FROM payments
            GROUP BY PaymentStatus
            """,
            conn,
        )

        # Trust score from merchants_loyalty
        merchants_df = pd.read_sql_query(
            """
            SELECT MerchantName,
                   RepaymentRate, DisputeRate, DefaultRate,
                   TransactionVolume, EngagementScore, ComplianceScore,
                   ResponsivenessScore, COALESCE(ExclusivityFlag, 0) AS ExclusivityFlag
            FROM merchants_loyalty
            """,
            conn,
        )

    merchants_df["TrustScore"] = merchants_df.apply(
        lambda r: calculate_merchant_trust_score(
            r["RepaymentRate"], r["DisputeRate"], r["DefaultRate"],
            r["TransactionVolume"], r["EngagementScore"], r["ComplianceScore"],
            r["ResponsivenessScore"], int(r["ExclusivityFlag"])
        ), axis=1
    )
    merchants_df["LoyaltyTier"] = merchants_df["TrustScore"].apply(assign_loyalty_tier)
    top_trust_df = merchants_df.sort_values("TrustScore", ascending=False).head(limit)

    return {
        "topMerchantsByPayments": top_merchants_df.to_dict(orient="records"),
        "paymentStatusMix": status_mix_df.to_dict(orient="records"),
        "topMerchantTrust": [
            {
                "merchant": row.MerchantName,
                "trustScore": float(row.TrustScore),
                "loyaltyTier": row.LoyaltyTier,
            }
            for _, row in top_trust_df.iterrows()
        ],
    }


@router.get("/consumers")
def consumers_dashboard() -> Dict[str, Any]:
    """
    Returns chart-ready data for the consumers dashboard in one payload.

    - monthlyCollections: line series [{ id, data: [{ x, y }] }]
    """
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT PaymentDate, PaymentAmount, PaymentStatus
            FROM payments
            """,
            conn,
            parse_dates=["PaymentDate"],
        )

    df["month"] = df["PaymentDate"].dt.to_period("M").astype(str)
    monthly_expected = df.groupby("month")["PaymentAmount"].sum().reset_index()
    monthly_received = (
        df[df["PaymentStatus"] == "PAID"]
        .groupby("month")["PaymentAmount"].sum().reset_index()
    )

    # Ensure union of months for consistent x-axis
    all_months = pd.DataFrame({"month": sorted(set(df["month"]))})
    monthly_expected = all_months.merge(monthly_expected, on="month", how="left").fillna(0)
    monthly_received = all_months.merge(monthly_received, on="month", how="left").fillna(0)

    series = [
        {
            "id": "expected",
            "data": [
                {"x": m, "y": float(v)}
                for m, v in zip(monthly_expected["month"], monthly_expected["PaymentAmount"])
            ],
        },
        {
            "id": "received",
            "data": [
                {"x": m, "y": float(v)}
                for m, v in zip(monthly_received["month"], monthly_received["PaymentAmount"])
            ],
        },
    ]

    return {"monthlyCollections": series}


