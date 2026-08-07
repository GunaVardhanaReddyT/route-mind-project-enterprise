from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class StopBase(BaseModel):
    address: str
    lat: float
    lon: float
    cod_amount: float = 0.0


class StopResponse(StopBase):
    id: int

    class Config:
        from_attributes = True


class RouteBase(BaseModel):
    vehicle_id: int
    status: str = "planned"
    hub_id: int


class RouteCreate(RouteBase):
    stop_ids: List[int]


class RouteResponse(RouteBase):
    id: int

    class Config:
        from_attributes = True


class OptimizationResult(BaseModel):
    routes: List[Dict[str, Any]]
    total_distance_km: float
    solve_time_ms: int
    constraints_applied: List[str]
    explanation: Optional[str]
    ai_cost_usd: float
    status: str
    changes: Optional[Dict[str, Any]] = None