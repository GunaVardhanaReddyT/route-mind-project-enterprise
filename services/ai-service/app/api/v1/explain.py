from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import boto3
import json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = settings.BEDROCK_MODEL_ID

    def generate_explanation(self, routes: List[Dict], constraints: List[str]) -> str:
        prompt = f"""You are a logistics supervisor assistant. Explain the route optimization results.

CONTEXT:
- Total routes: {len(routes)}
- Constraints: {', '.join(constraints)}

Provide a 2-3 sentence explanation about efficiency and constraints respected.
Keep it professional and concise."""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )

            result = json.loads(response["body"].read())
            return result["content"][0]["text"]

        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            return "Routes optimized using OR-Tools with Indian constraints (COD, Zone Timing, Odd-Even)."


@router.post("/explain")
async def explain_routes(
        routes: List[Dict],
        constraints: List[str] = ["COD_LIMIT", "ZONE_TIMING", "ODD_EVEN"]
):
    """Generate AI explanation for route optimization"""
    client = BedrockClient()
    explanation = client.generate_explanation(routes, constraints)

    return {
        "explanation": explanation,
        "constraints": constraints,
        "model": settings.BEDROCK_MODEL_ID
    }


@router.post("/explain-change")
async def explain_change(
        route_id: int,
        change_type: str,
        reason: str
):
    """Generate explanation for route change"""
    change_desc = "new pickup" if change_type == "new" else "failed delivery"

    prompt = f"""Route {route_id} re-planned due to {change_desc} ({reason}).
    Explain in 1-2 sentences what changed and what the driver should know."""

    client = BedrockClient()

    try:
        response = client.client.invoke_model(
            modelId=client.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        result = json.loads(response["body"].read())
        explanation = result["content"][0]["text"]

        return {
            "route_id": route_id,
            "change_type": change_type,
            "reason": reason,
            "explanation": explanation
        }

    except Exception as e:
        logger.error(f"Bedrock call failed: {e}")
        return {
            "route_id": route_id,
            "explanation": f"Route re-planned due to {reason}. Driver notified."
        }