from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.models.stop import Stop
from app.models.route import Route, RouteStop
from app.solver.engine import RouteOptimizer
from app.ai.client import BedrockClient
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
optimizer = RouteOptimizer(redis_url=settings.REDIS_URL)
bedrock = BedrockClient(region=settings.AWS_REGION, access_key=settings.AWS_ACCESS_KEY_ID,
                        secret_key=settings.AWS_SECRET_ACCESS_KEY, model_id=settings.BEDROCK_MODEL_ID)


@router.post("/optimize")
async def optimize_routes(hub_id: int = 1, use_ai_explanation: bool = True, db: AsyncSession = Depends(get_db)):
    vehicles_result = await db.execute(select(Vehicle).where(Vehicle.hub_id == hub_id, Vehicle.is_active == True))
    vehicles = [
        {"id": v.id, "plate_number": v.plate_number, "type": getattr(v, 'type', 'van'), "lat": 28.6139, "lon": 77.2090}
        for v in vehicles_result.scalars().all()]

    stops_result = await db.execute(select(Stop).where(Stop.hub_id == hub_id, Stop.is_completed == False))
    stops = [{"id": s.id, "lat": s.lat, "lon": s.lon, "cod_amount": s.cod_amount} for s in stops_result.scalars().all()]

    if not vehicles:
        raise HTTPException(status_code=400, detail="No active vehicles")
    if not stops:
        raise HTTPException(status_code=400, detail="No pending stops")

    solution = optimizer.solve_vrp(depot=(28.6139, 77.2090), stops=stops, vehicles=vehicles)

    explanation = None
    ai_cost = 0.0
    if use_ai_explanation and solution["status"] == "success":
        ai_result = bedrock.generate_explanation(routes=solution["routes"], constraints=solution["constraints_applied"],
                                                 total_distance=solution["total_distance_km"])
        explanation = ai_result["explanation"]
        ai_cost = ai_result["cost"]

    return {**solution, "explanation": explanation, "ai_cost_usd": ai_cost}


@router.post("/replan")
async def replan_route(route_id: int, new_stop_id: Optional[int] = None, failed_stop_id: Optional[int] = None,
                       reason: str = "traffic", db: AsyncSession = Depends(get_db)):
    replan_result = optimizer.replan_route(existing_routes=[], new_stop=None, failed_stop_id=failed_stop_id,
                                           reason=reason)
    ai_result = bedrock.generate_change_explanation(route_id=route_id, new_stop=None, failed_stop_id=failed_stop_id,
                                                    reason=reason)
    return {**replan_result, "explanation": ai_result["explanation"], "ai_cost_usd": ai_result["cost"]}