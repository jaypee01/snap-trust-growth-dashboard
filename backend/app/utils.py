import os
import math
import json
from typing import List, Dict, Union
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------
# Centralized AI Call (Summary & Recommendations only)
# ------------------------------
def call_ai(
    task: str,
    entity_type: str,
    data: Dict,
    default_response: Union[str, List[Dict]]
) -> Union[str, List[Dict]]:
    """
    Unified AI call wrapper for summaries and recommendations only.
    """
    if not client.api_key:
        return default_response

    if task == "summary":
        prompt = f"""
        Summarize the following {entity_type} details in 2-3 sentences for business reporting:

        {data}
        """
    elif task == "recommendations":
        prompt = f"""
        Provide 3-5 actionable recommendations for this {entity_type} to improve trust,
        loyalty, engagement, or financial performance.

        Format as JSON array of objects:
        [
            {{
                "title": "Short title",
                "description": "Detailed explanation of the recommendation"
            }}
        ]

        Profile:
        {data}
        """
    else:
        return default_response

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5,
        )
        content = response.choices[0].message.content.strip()

        if task == "recommendations":
            try:
                parsed = json.loads(content)
                clean_recs = [
                    {
                        "title": rec.get("title", "").strip(),
                        "description": rec.get("description", "").strip()
                    }
                    for rec in parsed if isinstance(rec, dict)
                ]
                return clean_recs if clean_recs else default_response
            except Exception:
                return default_response
        else:
            return content
    except Exception:
        return default_response


# ------------------------------
# Customer Trust & Loyalty (Formula only)
# ------------------------------
def get_customer_trust_loyalty(
    repayment_rate: float,
    dispute_count: int,
    default_rate: float
) -> Dict[str, Union[float, str]]:
    trust_score = calculate_customer_trust_score(repayment_rate, dispute_count, default_rate)
    return {
        "TrustScore": trust_score,
        "LoyaltyTier": assign_loyalty_tier(trust_score)
    }


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
# Merchant Trust & Loyalty (Formula only)
# ------------------------------
def get_merchant_trust_loyalty(
    repayment_rate: float,
    dispute_rate: float,
    default_rate: float,
    transaction_volume: float,
    engagement_score: float,
    compliance_score: float,
    responsiveness_score: float,
    exclusivity_flag: int
) -> Dict[str, Union[float, str]]:
    trust_score = calculate_merchant_trust_score(
        repayment_rate, dispute_rate, default_rate,
        transaction_volume, engagement_score,
        compliance_score, responsiveness_score,
        exclusivity_flag
    )
    return {
        "TrustScore": trust_score,
        "LoyaltyTier": assign_loyalty_tier(trust_score)
    }


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
# Summary Generation (AI + fallback)
# ------------------------------
def generate_summary(entity_type: str, data: Dict) -> str:
    name = data.get("CustomerName") or data.get("MerchantName") or "Entity"
    default_response = f"{name} has a TrustScore of {data.get('TrustScore', 'N/A')} and is in the {data.get('LoyaltyTier', 'N/A')} tier."

    return call_ai(
        task="summary",
        entity_type=entity_type,
        data=data,
        default_response=default_response
    )


# ------------------------------
# Customer Recommendations (AI + fallback)
# ------------------------------
def generate_customer_recommendations(customer_data: Dict) -> List[Dict]:
    def default_recommendations():
        recs = []
        if customer_data.get("TrustScore", 0) < 80:
            recs.append({
                "title": "Improve Repayments",
                "description": "Focus on timely repayments to improve your TrustScore."
            })
        else:
            recs.append({
                "title": "Premium Offers",
                "description": "Eligible for higher loan limits and premium offers."
            })
        if customer_data.get("DisputeCount", 0) > 0:
            recs.append({
                "title": "Reduce Disputes",
                "description": "Reduce disputes for smoother transactions."
            })
        recs.append({
            "title": "Engage with Top Merchants",
            "description": "Explore merchants with high engagement scores for rewards."
        })
        return recs

    return call_ai(
        task="recommendations",
        entity_type="customer",
        data=customer_data,
        default_response=default_recommendations()
    )


# ------------------------------
# Merchant Recommendations (AI + fallback)
# ------------------------------
def generate_merchant_recommendations(merchant_data: Dict) -> List[Dict]:
    def default_recommendations():
        recs = []
        if merchant_data.get("TrustScore", 0) < 80:
            recs.append({
                "title": "Improve TrustScore",
                "description": "Improve repayment rate and reduce defaults to increase TrustScore."
            })
        recs.append({
            "title": "Enhance Engagement",
            "description": "Enhance engagement and responsiveness scores for better customer satisfaction."
        })
        recs.append({
            "title": "Ensure Compliance",
            "description": "Ensure compliance metrics are consistently met."
        })
        return recs

    return call_ai(
        task="recommendations",
        entity_type="merchant",
        data=merchant_data,
        default_response=default_recommendations()
    )
