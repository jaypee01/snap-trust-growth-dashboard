def calculate_customer_trust_score(repayment_rate: float, dispute_count: int, default_rate: float) -> float:
    """
    Calculate the Trust Score for a customer based on repayment behavior and disputes.

    Formula:
        score = (repayment_rate * 0.5 + (1 - default_rate) * 0.3 + (1 - dispute_count / 10) * 0.2) * 100

    Parameters:
    -----------
    repayment_rate : float
        The fraction of payments the customer has paid on time (0 to 1).
    dispute_count : int
        Total number of disputes raised by the customer.
    default_rate : float
        Fraction of payments defaulted by the customer (0 to 1).

    Returns:
    --------
    float
        Trust score for the customer (0 to 100), rounded to 2 decimal places.
    """
    score = (repayment_rate * 0.5 + (1 - default_rate) * 0.3 + (1 - dispute_count / 10) * 0.2) * 100
    return round(score, 2)


def calculate_merchant_trust_score(
    repayment_rate: float,
    dispute_rate: float,
    default_rate: float,
    transaction_volume: float,
    engagement_score: float,
    compliance_score: float,
    responsiveness_score: float,
    exclusivity_flag: int
) -> float:
    """
    Calculate the Trust Score for a merchant based on multiple performance metrics.

    Example weighting:
        - RepaymentRate: 30%
        - DefaultRate: 20%
        - DisputeRate: 10%
        - EngagementScore: 15%
        - ComplianceScore: 15%
        - ResponsivenessScore: 10%
        - ExclusivityFlag: +5 bonus points if 1

    Parameters:
    -----------
    repayment_rate : float
        Fraction of payments received on time (0 to 1).
    dispute_rate : float
        Fraction of disputed transactions (0 to 1).
    default_rate : float
        Fraction of payments defaulted (0 to 1).
    transaction_volume : float
        Total transaction volume (used optionally in scoring formula).
    engagement_score : float
        Engagement score of the merchant (0 to 1).
    compliance_score : float
        Compliance score of the merchant (0 to 1).
    responsiveness_score : float
        Responsiveness score of the merchant (0 to 1).
    exclusivity_flag : int
        1 if merchant is exclusive, 0 otherwise.

    Returns:
    --------
    float
        Trust score for the merchant (0 to 100), rounded to 2 decimals.
    """
    score = (
        repayment_rate * 0.3 +
        (1 - default_rate) * 0.2 +
        (1 - dispute_rate) * 0.1 +
        engagement_score * 0.15 +
        compliance_score * 0.15 +
        responsiveness_score * 0.1
    ) * 100

    # Add bonus for exclusivity
    if exclusivity_flag == 1:
        score += 5

    # Cap at 100
    return round(min(score, 100), 2)


def assign_loyalty_tier(trust_score: float) -> str:
    """
    Assign a loyalty tier based on the trust score.

    Parameters:
    -----------
    trust_score : float
        Trust score of the customer or merchant (0 to 100).

    Returns:
    --------
    str
        Loyalty tier as one of: "Gold", "Silver", "Bronze".
    """
    if trust_score >= 90:
        return "Gold"
    elif trust_score >= 80:
        return "Silver"
    else:
        return "Bronze"
