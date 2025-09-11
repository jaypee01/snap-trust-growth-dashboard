from typing import Optional, List
from pydantic import BaseModel, Field


from typing import List, Optional
from pydantic import BaseModel, Field


class Merchant(BaseModel):
    """
    Pydantic model representing a Merchant for API responses.
    Combines core metrics with optional AI-driven insights.
    """

    # Core metrics
    MerchantID: str = Field(..., description="Unique identifier of the merchant")
    MerchantName: str = Field(..., description="Name of the merchant")
    RepaymentRate: float = Field(..., description="Fraction of payments received on time (0 to 1)")
    DisputeRate: float = Field(..., description="Fraction of transactions disputed (0 to 1)")
    DefaultRate: float = Field(..., description="Fraction of payments defaulted (0 to 1)")
    TransactionVolume: int = Field(..., description="Total transaction volume (whole number)")
    TenureMonths: int = Field(..., description="Duration of the merchant’s partnership in months")
    EngagementScore: float = Field(..., description="Customer engagement score (0 to 100)")
    ComplianceScore: float = Field(..., description="Compliance score (0 to 100)")
    ResponsivenessScore: float = Field(..., description="Responsiveness score (0 to 100)")
    ExclusivityFlag: int = Field(..., description="1 if exclusive partner, 0 otherwise")
    TrustScore: float = Field(..., description="Calculated trust score (0 to 100)")
    LoyaltyTier: str = Field(..., description="Loyalty tier based on TrustScore (Gold, Silver, Bronze, Platinum)")

    # Optional AI/derived insights
    RiskScore: Optional[str] = Field(None, description="AI-predicted risk level (Low, Medium, High)")
    Summary: Optional[str] = Field(None, description="AI-generated natural language summary of the merchant’s trust and loyalty profile")
    Benchmark: Optional[str] = Field(None, description="Comparative statement against peers (e.g., 'Top 10% in sector')")
    Recommendations: Optional[List[str]] = Field(None, description="AI-generated suggestions for improving performance")
    Explanation: Optional[str] = Field(None, description="Reasoning for TrustScore and LoyaltyTier assignment")
    History: Optional[List[dict]] = Field(None, description="Historical trust, dispute, and default trends")
    Rank: Optional[int] = Field(None, description="Leaderboard rank for this merchant")


class Customer(BaseModel):
    """
    Pydantic model representing a Customer for API responses.
    Combines core metrics with optional AI-driven insights.
    """

    # Core metrics
    CustomerID: str = Field(..., description="Unique identifier of the customer")
    CustomerName: str = Field(..., description="Name of the customer")
    RepaymentRate: float = Field(..., description="Fraction of payments made on time (0 to 1)")
    DisputeCount: int = Field(..., description="Total number of disputes raised by the customer")
    DefaultRate: float = Field(..., description="Fraction of payments defaulted (0 to 1)")
    TransactionVolume: int = Field(..., description="Total amount paid by the customer (whole number)")
    TrustScore: float = Field(..., description="Calculated trust score (0 to 100)")
    LoyaltyTier: str = Field(..., description="Loyalty tier based on TrustScore (Gold, Silver, Bronze, Platinum)")

    # Optional AI/derived insights
    RiskScore: Optional[str] = Field(None, description="AI-predicted risk level (Low, Medium, High)")
    Summary: Optional[str] = Field(None, description="AI-generated natural language summary of the customer's trust and loyalty profile")
    Recommendations: Optional[List[str]] = Field(None, description="AI-generated suggestions for merchants or products")
    Explanation: Optional[str] = Field(None, description="Reasoning for TrustScore and LoyaltyTier assignment")
    History: Optional[List[dict]] = Field(None, description="Historical trust, repayment, and dispute trends")
    Rank: Optional[int] = Field(None, description="Leaderboard rank for this customer")
