import pandas as pd
import json
import logging
from fastapi import APIRouter, Body
from typing import Dict, Any, Union

from ..utils import call_ai
from .customers_router import prepare_customer_metrics
from .merchants_router import prepare_merchant_metrics

logger = logging.getLogger(__name__)
router = APIRouter()


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


# -----------------------------
# Generic NLP query endpoint
# -----------------------------
@router.post("/merchants/ai-query")
def query_entities(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    """
    Natural language query API.
    Auto-classifies entity type (customer or merchant)
    and returns analysis in readable format.
    """
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

    result = call_ai(
        task="analysis",
        entity_type=entity_type,
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    return {"entity": entity_type, "query": query, "result": result}


# -----------------------------
# Customer-specific query endpoint
# -----------------------------
@router.post("/customers/ai-query")
def query_customers(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    """Customer-specific natural language query"""
    prepared_data = _prepare_data("customers")
    preview = prepared_data[:5]

    prompt = _build_prompt(query, preview, system="You are a helpful financial data analyst.")

    result = call_ai(
        task="analysis",
        entity_type="customers",
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    return {"entity": "customers", "query": query, "result": result}


# -----------------------------
# Merchant-specific query endpoint
# -----------------------------
@router.post("/merchants")
def query_merchants(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    """Merchant-specific natural language query"""
    prepared_data = _prepare_data("merchants")
    preview = prepared_data[:5]

    prompt = _build_prompt(query, preview, system="You are a helpful financial data analyst.")

    result = call_ai(
        task="analysis",
        entity_type="merchants",
        data={"query": query, "records": prepared_data[:200]},
        default_response={"message": "Unable to process query."},
        system=prompt
    )

    return {"entity": "merchants", "query": query, "result": result}
