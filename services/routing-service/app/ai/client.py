import boto3
import json
import logging
from typing import Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BedrockClient:
    """AWS Bedrock client for LLM explanations using Kimi K2.5"""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = settings.BEDROCK_MODEL_ID  # "moonshotai.kimi-k2.5"
        self.total_cost = 0.0

    async def generate_explanation(
            self,
            old_routes: List[Dict],
            new_routes: List[Dict],
            stops: List[Dict],
            vehicles: List[Dict]
    ) -> Dict:
        """Generate AI explanation for route optimization using Kimi K2.5"""

        total_distance = sum(r.get("distance_km", 0) for r in new_routes)
        
        prompt = f"""You are a logistics supervisor assistant. Explain the route optimization results.

CONTEXT:
- Total routes generated: {len(new_routes)}
- Total distance: {total_distance:.2f} km
- Constraints applied: COD Limit (₹50k), Zone Timing, Odd-Even Plate

Provide a 2-3 sentence professional explanation about:
1. How routes were optimized
2. Which Indian constraints were respected
3. Efficiency achieved

Keep it professional and concise."""

        try:
            # Kimi K2.5 uses OpenAI-compatible format (NOT Anthropic)
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                })
            )

            result = json.loads(response["body"].read())
            
            # Kimi K2.5 returns OpenAI-style response
            explanation = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not explanation:
                explanation = "Routes optimized using OR-Tools with Indian constraints (COD ₹50k, Zone Timing, Odd-Even)."

            # Approximate cost for Kimi K2.5
            cost = 0.001
            self.total_cost += cost

            return {"explanation": explanation, "cost": cost}

        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            return {
                "explanation": "Routes optimized using classical OR-Tools solver with Indian constraints (COD, Zone Timing, Odd-Even).",
                "cost": 0.0
            }

    async def generate_change_explanation(
            self,
            route_id: int,
            new_stop: Optional[Dict],
            failed_stop_id: Optional[int],
            reason: str
    ) -> Dict:
        """Generate explanation for route change using Kimi K2.5"""

        change_type = "new pickup" if new_stop else "failed delivery"

        prompt = f"""You are explaining a route re-plan to a logistics supervisor.

CHANGE DETAILS:
- Route ID: {route_id}
- Change Type: {change_type}
- Reason: {reason}

Explain in 1-2 sentences:
1. What changed
2. Why the re-plan was necessary
3. What the driver should know

Be clear and actionable."""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                })
            )

            result = json.loads(response["body"].read())
            explanation = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not explanation:
                explanation = f"Route re-planned due to {reason}. Driver notified of changes."

            cost = 0.001
            self.total_cost += cost

            return {"explanation": explanation, "cost": cost}

        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            return {
                "explanation": f"Route re-planned due to {reason}. Driver notified of changes.",
                "cost": 0.0
            }