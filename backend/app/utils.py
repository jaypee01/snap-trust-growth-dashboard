import math
from typing import List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------
# Customer Trust Score
# ------------------------------
def calculate_customer_trust_score(
    repayment_rate: float,
    dispute_count: int,
    default_rate: float
) -> float:
    normalized_dispute = min(dispute_count / 10, 1)
    score = (repayment_rate * 0.5 +
             (1 - default_rate) * 0.3 +
             (1 - normalized_dispute) * 0.2) * 100
    return round(score, 2)

# ------------------------------
# Merchant Trust Score
# ------------------------------
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
    score = (
        repayment_rate * 0.3 +
        (1 - default_rate) * 0.2 +
        (1 - dispute_rate) * 0.1 +
        engagement_score * 0.15 +
        compliance_score * 0.15 +
        responsiveness_score * 0.1
    ) * 100

    if exclusivity_flag == 1:
        score += 5
    if transaction_volume > 1000:
        score += min(math.log(transaction_volume, 10), 5)
    return round(min(score, 100), 2)

# ------------------------------
# Loyalty Tier Assignment
# ------------------------------
def assign_loyalty_tier(trust_score: float) -> str:
    if trust_score >= 95:
        return "Platinum"
    elif trust_score >= 90:
        return "Gold"
    elif trust_score >= 80:
        return "Silver"
    else:
        return "Bronze"

# ------------------------------
# Risk Score Assignment
# ------------------------------
def assign_risk_score(
    trust_score: float,
    default_rate: float,
    dispute_rate_or_count: float
) -> str:
    if trust_score >= 85 and default_rate < 0.1 and dispute_rate_or_count < 0.1:
        return "Low"
    elif trust_score >= 70:
        return "Medium"
    else:
        return "High"

# ------------------------------
# Summary Generation
# ------------------------------
def generate_summary(entity_type: str, data: Dict) -> str:
    if not client.api_key:
        return default_summary(entity_type, data)

    prompt = f"""
    Summarize the following {entity_type} details in 2-3 sentences for business reporting:

    {data}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant creating concise business summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return default_summary(entity_type, data)

def default_summary(entity_type: str, data: Dict) -> str:
    name = data.get("CustomerName") or data.get("MerchantName") or "Entity"
    score = data.get("TrustScore", "N/A")
    tier = data.get("LoyaltyTier", "N/A")
    return f"{name} has a TrustScore of {score} and is in the {tier} tier."

# ------------------------------
# Customer Recommendations
# ------------------------------
def generate_customer_recommendations(customer_data: Dict) -> List[str]:
    def default_recommendations():
        recommendations = []
        if customer_data.get("TrustScore", 0) < 80:
            recommendations.append("Focus on timely repayments to improve your TrustScore.")
        else:
            recommendations.append("Eligible for higher loan limits and premium offers.")
        if customer_data.get("DisputeCount", 0) > 0:
            recommendations.append("Reduce disputes for smoother transactions.")
        recommendations.append("Explore merchants with high engagement scores for rewards.")
        return recommendations

    if not client.api_key:
        return default_recommendations()

    prompt = f"""
    Provide 3-5 actionable recommendations for this customer to improve trust, loyalty,
    or financial engagement based on their profile:

    {customer_data}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant generating actionable advice for customers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.6
        )
        text = response.choices[0].message.content.strip()
        recommendations = [line.strip("-• ") for line in text.splitlines() if line.strip()]
        return recommendations if recommendations else default_recommendations()
    except Exception:
        return default_recommendations()

# ------------------------------
# Merchant Recommendations
# ------------------------------
def generate_merchant_recommendations(merchant_data: Dict) -> List[str]:
    def default_recommendations():
        recommendations = []
        if merchant_data.get("TrustScore", 0) < 80:
            recommendations.append("Improve repayment rate and reduce defaults to increase TrustScore.")
        recommendations.append("Enhance engagement and responsiveness scores for better customer satisfaction.")
        recommendations.append("Ensure compliance metrics are consistently met.")
        return recommendations

    if not client.api_key:
        return default_recommendations()

    prompt = f"""
    Provide 3-5 actionable recommendations for this merchant to improve trust, loyalty,
    engagement, or financial performance based on their profile:

    {merchant_data}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant generating actionable advice for merchants."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.6
        )
        text = response.choices[0].message.content.strip()
        recommendations = [line.strip("-• ") for line in text.splitlines() if line.strip()]
        return recommendations if recommendations else default_recommendations()
    except Exception:
        return default_recommendations()
