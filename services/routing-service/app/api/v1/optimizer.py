from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.models.stop import Stop
from app.models.route import Route, RouteStop
from app.schemas.route import RouteResponse, RouteCreate, OptimizationResult
from app.solver.engine import RouteOptimizer
from app.solver.constraints import get_constraint
from app.ai.client import BedrockClient

logger = logging.getLogger(__name__)

router = APIRouter()
optimizer = RouteOptimizer()
bedrock = BedrockClient()


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_routes(
        hub_id: int,
        db: AsyncSession = Depends(get_db),
        use_ai_explanation: bool = True
):
    """
    Generate optimized routes for a hub

    Respects Indian constraints:
    - COD limits (₹50k per vehicle)
    - Zone timing (truck restrictions)
    - Odd-even plate rules
    """
    # Fetch vehicles and stops
    vehicles_result = await db.execute(
        select(Vehicle).where(Vehicle.hub_id == hub_id, Vehicle.is_active == True)
    )
    vehicles = [v.__dict__ for v in vehicles_result.scalars().all()]

    stops_result = await db.execute(
        select(Stop).where(Stop.hub_id == hub_id, Stop.is_completed == False)
    )
    stops = [s.__dict__ for s in stops_result.scalars().all()]

    if not vehicles:
        raise HTTPException(status_code=400, detail="No active vehicles for hub")

    if not stops:
        raise HTTPException(status_code=400, detail="No pending stops for hub")

    # Get depot location (first vehicle's hub for demo)
    depot = (vehicles[0].get("lat", 28.6139), vehicles[0].get("lon", 77.2090))

    # Load Indian constraints
    constraints = [
        get_constraint("cod_limit", limit=50000.0),
        get_constraint("zone_timing"),
        get_constraint("odd_even"),
        get_constraint("time_window"),
    ]

    # Solve VRP
    solution = optimizer.solve_vrp(
        depot=depot,
        stops=stops,
        vehicles=vehicles,
        constraints=constraints
    )

    if solution["status"] != "success":
        raise HTTPException(status_code=500, detail="Optimization failed")

    # Save routes to DB
    saved_routes = []
    for route_data in solution["routes"]:
        route = Route(
            vehicle_id=route_data["vehicle_id"],
            hub_id=hub_id,
            status="planned"
        )
        db.add(route)
        await db.flush()

        for stop_idx, seq in enumerate(route_data["stop_indices"]):
            route_stop = RouteStop(
                route_id=route.id,
                stop_id=stops[seq]["id"],
                sequence=stop_idx
            )
            db.add(route_stop)

        saved_routes.append(route_data)

    await db.commit()

    # Generate AI explanation
    explanation = None
    ai_cost = 0.0

    if use_ai_explanation:
        try:
            explanation_response = await bedrock.generate_explanation(
                old_routes=[],
                new_routes=solution["routes"],
                stops=stops,
                vehicles=vehicles
            )
            explanation = explanation_response["explanation"]
            ai_cost = explanation_response["cost"]
        except Exception as e:
            logger.warning(f"AI explanation failed: {e}")
            explanation = "Routes optimized using OR-Tools with Indian constraints."

    return {
        "routes": saved_routes,
        "total_distance_km": solution["total_distance"],
        "solve_time_ms": solution["solve_time_ms"],
        "constraints_applied": solution["constraints_applied"],
        "explanation": explanation,
        "ai_cost_usd": ai_cost,
        "status": "success"
    }


@router.post("/replan", response_model=OptimizationResult)
async def replan_route(
        route_id: int,
        new_stop_id: Optional[int] = None,
        failed_stop_id: Optional[int] = None,
        reason: str = "traffic",
        db: AsyncSession = Depends(get_db)
):
    """
    Re-plan a route due to dynamic change

    Latency: < 30 seconds (guardrail requirement)
    """
    import time
    start_time = time.time()

    # Fetch existing route
    route_result = await db.execute(
        select(Route).where(Route.id == route_id)
    )
    route = route_result.scalar_one_or_none()

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Get new stop if provided
    new_stop = None
    if new_stop_id:
        stop_result = await db.execute(
            select(Stop).where(Stop.id == new_stop_id)
        )
        new_stop = stop_result.scalar_one_or_none()

    # Incremental re-plan
    replan_result = optimizer.replan_route(
        existing_solution={"route_id": route_id},
        new_stop=new_stop.__dict__ if new_stop else None,
        failed_stop_id=failed_stop_id
    )

    solve_time_ms = int((time.time() - start_time) * 1000)

    # Check latency guardrail
    if solve_time_ms > 30000:
        logger.warning(f"Re-plan exceeded 30s guardrail: {solve_time_ms}ms")

    # Generate explanation for supervisor
    explanation = await bedrock.generate_change_explanation(
        route_id=route_id,
        new_stop=new_stop.__dict__ if new_stop else None,
        failed_stop_id=failed_stop_id,
        reason=reason
    )

    return {
        "routes": [replan_result],
        "total_distance_km": 0,
        "solve_time_ms": solve_time_ms,
        "constraints_applied": ["cod_limit", "zone_timing"],
        "explanation": explanation["explanation"],
        "ai_cost_usd": explanation["cost"],
        "status": "replanned",
        "changes": replan_result["changes"]
    }