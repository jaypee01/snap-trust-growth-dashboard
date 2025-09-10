from pydantic import BaseModel, Field

class Merchant(BaseModel):
    """
    Pydantic model representing a Merchant for API responses.

    Attributes:
    -----------
    MerchantID : str
        Unique identifier of the merchant.
    MerchantName : str
        Name of the merchant.
    RepaymentRate : float
        Fraction of payments received on time (0 to 1), rounded to 2 decimals.
    DisputeCount : int
        Number of disputed transactions.
    DefaultRate : float
        Fraction of payments defaulted (0 to 1), rounded to 2 decimals.
    TransactionVolume : int
        Total transaction volume (whole number).
    TrustScore : float
        Calculated trust score (0 to 100).
    LoyaltyTier : str
        Loyalty tier assigned based on TrustScore (Gold, Silver, Bronze).
    Summary : str
        AI-generated natural language summary of the merchant's trust and loyalty profile.
    """
    MerchantID: str = Field(..., description="Unique identifier of the merchant")
    MerchantName: str = Field(..., description="Name of the merchant")
    RepaymentRate: float = Field(..., description="Fraction of payments received on time (0 to 1)")
    DisputeCount: int = Field(..., description="Number of disputed transactions")
    DefaultRate: float = Field(..., description="Fraction of payments defaulted (0 to 1)")
    TransactionVolume: int = Field(..., description="Total transaction volume (whole number)")
    TrustScore: float = Field(..., description="Calculated trust score (0 to 100)")
    LoyaltyTier: str = Field(..., description="Loyalty tier based on TrustScore (Gold, Silver, Bronze)")
    Summary: str = Field(..., description="AI-generated summary of merchant profile")


class Customer(BaseModel):
    """
    Pydantic model representing a Customer for API responses.

    Attributes:
    -----------
    CustomerID : str
        Unique identifier of the customer.
    CustomerName : str
        Name of the customer.
    RepaymentRate : float
        Fraction of payments made on time (0 to 1), rounded to 2 decimals.
    DisputeCount : int
        Total number of disputes raised by the customer.
    DefaultRate : float
        Fraction of payments defaulted (0 to 1), rounded to 2 decimals.
    TransactionVolume : int
        Total amount paid by the customer (whole number).
    TrustScore : float
        Calculated trust score (0 to 100).
    LoyaltyTier : str
        Loyalty tier assigned based on TrustScore (Gold, Silver, Bronze).
    Summary : str
        AI-generated natural language summary of the customer's trust and loyalty profile.
    """
    CustomerID: str = Field(..., description="Unique identifier of the customer")
    CustomerName: str = Field(..., description="Name of the customer")
    RepaymentRate: float = Field(..., description="Fraction of payments made on time (0 to 1)")
    DisputeCount: int = Field(..., description="Total number of disputes raised by the customer")
    DefaultRate: float = Field(..., description="Fraction of payments defaulted (0 to 1)")
    TransactionVolume: int = Field(..., description="Total amount paid by the customer (whole number)")
    TrustScore: float = Field(..., description="Calculated trust score (0 to 100)")
    LoyaltyTier: str = Field(..., description="Loyalty tier based on TrustScore (Gold, Silver, Bronze)")
    Summary: str = Field(..., description="AI-generated summary of customer profile")
