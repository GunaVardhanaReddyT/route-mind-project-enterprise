import boto3
import json
import logging
from typing import Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BedrockClient:
    """AWS Bedrock client for LLM explanations"""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        self.total_cost = 0.0

    async def generate_explanation(
            self,
            old_routes: List[Dict],
            new_routes: List[Dict],
            stops: List[Dict],
            vehicles: List[Dict]
    ) -> Dict:
        """Generate AI explanation for route optimization"""

        prompt = f"""You are a logistics supervisor assistant. Explain the route optimization results.

CONTEXT:
- Total routes generated: {len(new_routes)}
- Constraints applied: COD Limit (₹50k), Zone Timing, Odd-Even Plate

OPTIMIZATION SUMMARY:
{json.dumps(new_routes, indent=2)}

Provide a 2-3 sentence explanation for the supervisor about:
1. How routes were optimized
2. Which Indian constraints were respected
3. Estimated efficiency gain

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
            explanation = result["content"][0]["text"]

            # Calculate cost (Haiku: $0.00025/1K input, $0.00125/1K output)
            input_tokens = len(prompt) / 4
            output_tokens = len(explanation) / 4
            cost = (input_tokens * 0.00025 / 1000) + (output_tokens * 0.00125 / 1000)
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
        """Generate explanation for route change"""

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
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )

            result = json.loads(response["body"].read())
            explanation = result["content"][0]["text"]

            cost = 0.001  # Approximate cost
            self.total_cost += cost

            return {"explanation": explanation, "cost": cost}

        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            return {
                "explanation": f"Route re-planned due to {reason}. Driver notified of changes.",
                "cost": 0.0
            }