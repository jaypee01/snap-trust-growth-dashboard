import pandas as pd
import json
import re
import logging
from fastapi import APIRouter, Body
from typing import Dict, Any, Union

from ..utils import call_ai
from .customers_router import prepare_customer_metrics
from .merchants_router import prepare_merchant_metrics

logger = logging.getLogger(__name__)
router = APIRouter()


# -----------------------------
# Helper functions
# -----------------------------
def _prepare_data(entity_type: str) -> list:
    """Load and prepare data for the given entity type, ensure JSON-serializable"""
    if entity_type == "merchants":
        df = pd.read_csv("app/data/merchants_loyalty.csv")
        prepared_data = prepare_merchant_metrics(df)
    else:
        df = pd.read_csv("app/data/payments.csv")
        prepared_data = prepare_customer_metrics(df)

    if isinstance(prepared_data, pd.DataFrame):
        prepared_data = prepared_data.to_dict(orient="records")
    return prepared_data


def _build_prompt(query: str, preview_data: list, system: str = "") -> str:
    """Build AI analysis prompt with a preview of data"""
    return f"""
{system}

User query: "{query}"

Data sample (for reference):
{json.dumps(preview_data, indent=2)}

⚠️ IMPORTANT:
- Respond with clean, structured, readable data.
- Output can be JSON, HTML table, or text, depending on request.
- Do NOT include markdown, explanations, or extra text outside output.
"""


def safe_parse_json(ai_output: str, default_response: Any):
    """
    Try to parse AI output as JSON after cleaning.
    Returns default_response if parsing fails.
    """
    try:
        clean_output = re.sub(r"^```.*|```$", "", ai_output.strip(), flags=re.DOTALL)
        clean_output = clean_output.replace("'", '"')
        return json.loads(clean_output)
    except json.JSONDecodeError:
        clean_output = re.sub(r",(\s*[\]}])", r"\1", clean_output)
        try:
            return json.loads(clean_output)
        except Exception:
            logger.warning("Failed to parse AI JSON, returning default response.")
            return default_response


# -----------------------------
# Generic AI query (auto-detect entity)
# -----------------------------
@router.post("/ai-query")
def query_entities(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    classify_prompt = """
You are a classifier. Given a user query, decide if it is about 'customers' or 'merchants'.
Respond with ONLY one word: 'customers' or 'merchants'.
"""
    entity_type = call_ai(
        task="classification",
        entity_type="auto",
        data={"query": query},
        default_response="customers",
        system=classify_prompt
    )
    entity_type = entity_type.strip().lower() if isinstance(entity_type, str) else "customers"
    logger.info(f"Detected entity type: {entity_type}")

    prepared_data = _prepare_data(entity_type)
    preview = prepared_data[:5]
    prompt = _build_prompt(query, preview, system="You are a helpful financial data analyst.")

    ai_response = call_ai(
        task="analysis",
        entity_type=entity_type,
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    if isinstance(ai_response, str):
        ai_response = safe_parse_json(ai_response, {"message": ai_response})

    return {"entity": entity_type, "query": query, "result": ai_response}


# -----------------------------
# Customer-specific query
# -----------------------------
@router.post("/customers/ai-query")
def query_customers(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    prepared_data = _prepare_data("customers")
    preview = prepared_data[:5]
    prompt = _build_prompt(query, preview, system="You are a helpful financial data analyst.")

    ai_response = call_ai(
        task="analysis",
        entity_type="customers",
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    if isinstance(ai_response, str):
        ai_response = safe_parse_json(ai_response, {"message": ai_response})

    return {"entity": "customers", "query": query, "result": ai_response}


# -----------------------------
# Merchant-specific query
# -----------------------------
@router.post("/merchants/ai-query")
def query_merchants(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    prepared_data = _prepare_data("merchants")
    preview = prepared_data[:5]
    prompt = _build_prompt(query, preview, system="You are a helpful financial data analyst.")

    ai_response = call_ai(
        task="analysis",
        entity_type="merchants",
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    if isinstance(ai_response, str):
        ai_response = safe_parse_json(ai_response, {"message": ai_response})

    return {"entity": "merchants", "query": query, "result": ai_response}
