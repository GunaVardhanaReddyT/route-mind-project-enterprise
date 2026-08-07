from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from fastapi import Query
import logging
import boto3
import json

from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.models.stop import Stop
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/optimize")
async def optimize_routes(hub_id: int = 1, use_ai_explanation: bool = True, db: AsyncSession = Depends(get_db)):
    # Fetch vehicles
    vehicles_result = await db.execute(select(Vehicle).where(Vehicle.hub_id == hub_id, Vehicle.is_active == True))
    vehicles = [{"id": v.id, "plate_number": v.plate_number, "lat": 28.6139, "lon": 77.2090} for v in
                vehicles_result.scalars().all()]

    # Fetch stops
    stops_result = await db.execute(select(Stop).where(Stop.hub_id == hub_id, Stop.is_completed == False))
    stops = [{"id": s.id, "lat": s.lat, "lon": s.lon, "cod_amount": s.cod_amount} for s in stops_result.scalars().all()]

    if not vehicles:
        raise HTTPException(status_code=400, detail="No active vehicles")
    if not stops:
        raise HTTPException(status_code=400, detail="No pending stops")

    # OR-Tools solve
    from app.solver.engine import RouteOptimizer
    optimizer = RouteOptimizer(redis_url=settings.REDIS_URL)
    solution = optimizer.solve_vrp(depot=(28.6139, 77.2090), stops=stops, vehicles=vehicles)

    # Generate AI explanation using Kimi K2
    explanation = None
    ai_cost = 0.0

    if use_ai_explanation and solution.get("status") == "success":
        if settings.BEDROCK_API_KEY:
            try:
                import requests
                
                prompt = f"""You are a logistics supervisor assistant. Explain the route optimization results.

CONTEXT:
- Total routes: {len(solution.get('routes', []))}
- Total distance: {solution.get('total_distance_km', 0):.2f} km
- Solve time: {solution.get('solve_time_ms', 0)} ms
- Constraints: COD Limit (₹50k), Zone Timing (8AM-10PM truck restriction), Odd-Even Plate

Provide a 2-3 sentence explanation about:
1. How routes were optimized
2. Which Indian constraints were respected
3. Efficiency achieved

Keep it professional and concise."""

                # Bedrock API endpoint for Kimi K2.5
                api_url = f"https://bedrock-runtime.{settings.AWS_REGION}.amazonaws.com/model/{settings.BEDROCK_MODEL_ID}/invoke"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.BEDROCK_API_KEY}"
                }
                
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                response = requests.post(api_url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    explanation = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not explanation:
                        explanation = f"Routes optimized using OR-Tools. {len(solution.get('routes', []))} routes created covering {solution.get('total_distance_km', 0):.2f} km."
                    ai_cost = 0.001
                else:
                    logger.warning(f"Bedrock API call failed: {response.status_code} - {response.text}")
                    explanation = f"Routes optimized using OR-Tools with Indian constraints (COD ₹50k, Zone Timing, Odd-Even). AI explanation unavailable."
                    
            except Exception as e:
                logger.warning(f"Bedrock API key method failed: {e}")
                explanation = f"Routes optimized using OR-Tools with Indian constraints. {len(solution.get('routes', []))} routes created."
                ai_cost = 0.0
                
        elif settings.AWS_ACCESS_KEY_ID and settings.AWS_ACCESS_KEY_ID != "your_key":
            # Use AWS IAM credentials (old method)
            try:
                bedrock_client = boto3.client(
                    "bedrock-runtime",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )

                prompt = f"""You are a logistics supervisor assistant. Explain the route optimization results.

CONTEXT:
- Total routes: {len(solution.get('routes', []))}
- Total distance: {solution.get('total_distance_km', 0):.2f} km
- Solve time: {solution.get('solve_time_ms', 0)} ms
- Constraints: COD Limit (₹50k), Zone Timing (8AM-10PM truck restriction), Odd-Even Plate

Provide a 2-3 sentence explanation about:
1. How routes were optimized
2. Which Indian constraints were respected
3. Efficiency achieved

Keep it professional and concise."""

                response = bedrock_client.invoke_model(
                    modelId=settings.BEDROCK_MODEL_ID,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500,
                        "temperature": 0.7
                    })
                )

                result = json.loads(response["body"].read())
                explanation = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                if not explanation:
                    explanation = result.get("content", [{}])[0].get("text", "") if "content" in result else str(result)

                ai_cost = 0.001

            except Exception as e:
                logger.warning(f"AWS Bedrock call failed: {e}")
                explanation = f"Routes optimized using OR-Tools with Indian constraints (COD ₹50k, Zone Timing, Odd-Even). AI explanation unavailable."
                ai_cost = 0.0
        else:
            logger.info("No AI credentials configured, using fallback explanation")
            explanation = f"Routes optimized using OR-Tools solver. {len(solution.get('routes', []))} routes created covering {solution.get('total_distance_km', 0):.2f} km. Indian constraints enforced: COD Limit (₹50k), Zone Timing, Odd-Even."
    else:
        explanation = f"Routes optimized using OR-Tools solver. {len(solution.get('routes', []))} routes created covering {solution.get('total_distance_km', 0):.2f} km. Constraints applied: COD Limit (₹50k), Zone Timing, Odd-Even."

    return {
        **solution,
        "explanation": explanation,
        "ai_cost_usd": ai_cost,
        "model_used": settings.BEDROCK_MODEL_ID
    }


@router.post("/replan")
async def replan_route(
        route_id: int = Query(...),
        new_stop_id: Optional[int] = Query(None),
        failed_stop_id: Optional[int] = Query(None),
        reason: str = Query("traffic"),
        hub_id: int = Query(1),
        db: AsyncSession = Depends(get_db)
):
    """Re-plan routes when a stop fails or new pickup is added"""
    
    # Fetch current vehicles and stops
    vehicles_result = await db.execute(select(Vehicle).where(Vehicle.hub_id == hub_id, Vehicle.is_active == True))
    vehicles = [{"id": v.id, "plate_number": v.plate_number} for v in vehicles_result.scalars().all()]

    # Fetch all stops
    stops_result = await db.execute(select(Stop).where(Stop.hub_id == hub_id))
    all_stops = [{"id": s.id, "lat": s.lat, "lon": s.lon, "cod_amount": s.cod_amount} 
                 for s in stops_result.scalars().all()]

    # Get new stop if provided
    new_stop = None
    if new_stop_id:
        new_stop_result = await db.execute(select(Stop).where(Stop.id == new_stop_id))
        stop_obj = new_stop_result.scalar_one_or_none()
        if stop_obj:
            new_stop = {"id": stop_obj.id, "lat": stop_obj.lat, "lon": stop_obj.lon, "cod_amount": stop_obj.cod_amount}

    if not vehicles:
        raise HTTPException(status_code=400, detail="No active vehicles")

    # Re-solve
    from app.solver.engine import RouteOptimizer
    optimizer = RouteOptimizer(redis_url=settings.REDIS_URL)
    
    replan_result = optimizer.replan_route(
        existing_routes=[],
        depot=(28.6139, 77.2090),
        all_stops=all_stops,
        vehicles=vehicles,
        new_stop=new_stop,
        failed_stop_id=failed_stop_id,
        reason=reason
    )

    # Generate explanation for change
    explanation = None
    ai_cost = 0.0
    
    # Check if AWS credentials are configured
    if not settings.AWS_ACCESS_KEY_ID or settings.AWS_ACCESS_KEY_ID == "your_key":
        change_type = "new pickup" if new_stop_id else "failed delivery"
        explanation = f"Route {route_id} re-planned due to {change_type} ({reason}). {replan_result.get('changes', {}).get('affected_routes', 0)} routes affected. Total distance: {replan_result.get('total_distance_km', 0):.2f} km. Driver will be notified of sequence changes."
    else:
        try:
            bedrock_client = boto3.client(
                "bedrock-runtime",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            change_type = "new pickup" if new_stop_id else "failed delivery"
            prompt = f"""Explain this route re-plan to a logistics supervisor:
- Route ID: {route_id}
- Change: {change_type}
- Reason: {reason}

In 1-2 sentences, explain what changed and what the driver should know."""

            response = bedrock_client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                })
            )

            result = json.loads(response["body"].read())
            explanation = result.get("choices", [{}])[0].get("message", {}).get("content",
                                                                                f"Route re-planned due to {reason}.")
            ai_cost = 0.001

        except Exception as e:
            logger.warning(f"Kimi K2 explanation failed: {e}")
            change_type = "new pickup" if new_stop_id else "failed delivery"
            explanation = f"Route {route_id} re-planned due to {change_type}. Driver notified."
            ai_cost = 0.0

    return {
        **replan_result,
        "explanation": explanation,
        "ai_cost_usd": ai_cost,
        "model_used": settings.BEDROCK_MODEL_ID if explanation and ai_cost > 0 else "none"
    }