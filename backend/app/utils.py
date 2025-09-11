import os
import math
import json
from typing import List, Dict, Union, Any
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    default_response: Union[str, List[Dict], Dict] = None,
    system: str = "You are a helpful financial assistant."
) -> Any:
    """
    Unified AI wrapper for summaries, recommendations, classification, and analysis.
    Ensures AI outputs readable data (JSON, HTML, or plain text) depending on the task.
    """

    logger.info(f"call_ai invoked with task='{task}', entity_type='{entity_type}'")
    try:
        logger.info(f"Input data: {json.dumps(data, indent=2)}")
    except Exception:
        logger.warning("Non-serializable data detected, skipping JSON logging.")

    if not client.api_key:
        logger.warning("OpenAI API key not set. Returning default response.")
        return default_response

    # -----------------------------
    # Build prompt based on task
    # -----------------------------
    if task == "summary":
        prompt = f"""
Summarize the following {entity_type} details in 2-3 sentences for business reporting.

⚠️ IMPORTANT:
- Return plain text or a single JSON object if needed.
- Do NOT include markdown code fences or extra explanation.

Profile:
{data}
"""
    elif task == "recommendations":
        prompt = f"""
Provide 3-5 actionable recommendations for this {entity_type} to improve trust,
loyalty, engagement, or financial performance.

⚠️ IMPORTANT:
- Return ONLY valid JSON (array of objects)
- Do NOT include markdown or explanations
- Each object must have "title" and "description"

Profile:
{data}
"""
    elif task == "classification":
        prompt = f"""
{system}

Query:
{data.get("query", "")}

⚠️ IMPORTANT:
- Respond with ONLY one word: 'customers' or 'merchants'
"""
    elif task == "analysis":
        prompt = f"""
{system}

Query:
{data.get("query", "")}

Data (sample or capped records):
{data.get("records", [])}

⚠️ IMPORTANT:
- Respond with STRICT VALID JSON only.
- Do NOT include markdown, explanations, or extra text.
"""
    else:
        logger.warning(f"Unknown task '{task}'. Returning default response.")
        return default_response

    logger.info(f"Prompt sent to AI:\n{prompt}")

    # -----------------------------
    # Send to AI
    # -----------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"Raw AI response: {content}")

        # -----------------------------
        # Parse response based on task
        # -----------------------------
        if task in ("recommendations", "analysis"):
            # Strip markdown/code fences
            content = content.strip("` \n")
            # Attempt to fix common JSON issues
            try:
                parsed = json.loads(content)
                return parsed if parsed else default_response
            except json.JSONDecodeError:
                # Try a simple fix: remove trailing commas
                import re
                repaired = re.sub(r",\s*([\]}])", r"\1", content)
                try:
                    parsed = json.loads(repaired)
                    return parsed if parsed else default_response
                except Exception:
                    logger.error("Failed to parse AI JSON. Returning default response.")
                    return default_response

        elif task == "classification":
            return content.lower().strip()

        else:  # summary or free text (could be HTML)
            return content

    except Exception as e:
        logger.error(f"Exception calling AI: {e}. Returning default response.")
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

    logger.info("Calling AI for customer recommendations...")
    logger.info(f"Customer input data: {json.dumps(customer_data, indent=2)}")

    raw_recommendations = call_ai(
        task="recommendations",
        entity_type="customer",
        data=customer_data,
        default_response=None  # temporarily set None
    )

    logger.info(f"AI raw output: {raw_recommendations}")

    # If AI response is invalid, fall back
    if not raw_recommendations or not isinstance(raw_recommendations, list):
        logger.warning("AI response invalid or empty, using default recommendations.")
        return default_recommendations()

    valid_recs = []
    for rec in raw_recommendations:
        if isinstance(rec, dict) and "title" in rec and "description" in rec:
            valid_recs.append(rec)
        else:
            logger.warning(f"Malformed AI recommendation: {rec}")

    if not valid_recs:
        logger.warning("No valid AI recommendations, using default.")
        return default_recommendations()

    logger.info(f"Returning {len(valid_recs)} AI-generated recommendations.")
    return valid_recs


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

    logger.info("Calling AI for merchant recommendations...")
    logger.info(f"Merchant input data: {json.dumps(merchant_data, indent=2)}")

    raw_recommendations = call_ai(
        task="recommendations",
        entity_type="merchant",
        data=merchant_data,
        default_response=default_recommendations()
    )

    logger.info(f"AI raw output: {raw_recommendations}")

    # If AI response is invalid, fall back
    if not raw_recommendations or not isinstance(raw_recommendations, list):
        logger.warning("AI response invalid or empty, using default recommendations.")
        return default_recommendations()

    # Keep only valid recommendations (title + description)
    valid_recs = []
    for rec in raw_recommendations:
        if isinstance(rec, dict) and "title" in rec and "description" in rec:
            valid_recs.append({
                "title": rec["title"].strip(),
                "description": rec["description"].strip()
            })
        else:
            logger.warning(f"Malformed AI recommendation: {rec}")

    if not valid_recs:
        logger.warning("No valid AI recommendations, using default.")
        return default_recommendations()

    logger.info(f"Returning {len(valid_recs)} recommendations.")
    return valid_recs
