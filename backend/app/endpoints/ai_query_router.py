import pandas as pd
import json
import logging
from fastapi import APIRouter, Body
from typing import Dict, Any

from ..utils import call_ai
from .customers_router import prepare_customer_metrics
from .merchants_router import prepare_merchant_metrics

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
def query_entities(query: str = Body(..., embed=True)) -> Dict[str, Any]:
    """
    Natural language query API.
    - Detects if the query is about customers or merchants
    - Prepares metrics accordingly
    - Runs AI analysis with strict JSON output
    """

    # Step 1: Classify entity type
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

    if isinstance(entity_type, str):
        entity_type = entity_type.strip().lower()
    else:
        entity_type = "customers"

    logger.info(f"Detected entity type: {entity_type}")

    # Step 2: Prepare metrics
    if entity_type == "merchants":
        df = pd.read_csv("app/data/merchants_loyalty.csv")
        prepared_data = prepare_merchant_metrics(df)
    else:
        df = pd.read_csv("app/data/payments.csv")
        prepared_data = prepare_customer_metrics(df)

    # ✅ Ensure prepared_data is JSON serializable
    if isinstance(prepared_data, pd.DataFrame):
        prepared_data = prepared_data.to_dict(orient="records")

    # Step 3: Build analysis prompt (show preview only)
    preview = prepared_data[:5] if isinstance(prepared_data, list) else []
    analysis_prompt = f"""
    You are a JSON-only data analyst.
    
    User query: "{query}"
    
    Data sample:
    {json.dumps(preview, indent=2)}
    
    ⚠️ IMPORTANT:
    - Respond with STRICT VALID JSON only.
    - Do NOT include markdown, explanations, or text outside JSON.
    - If sorting/filtering is requested, include the transformed data in JSON.
    """

    # Step 4: Call AI
    result = call_ai(
        task="analysis",
        entity_type=entity_type,
        data={
            "query": query,
            "records": prepared_data[:200] if isinstance(prepared_data, list) else prepared_data
        },  # cap records for tokens
        default_response={"message": "Unable to process query."},
        system=analysis_prompt
    )

    return {
        "entity": entity_type,
        "query": query,
        "result": result
    }
