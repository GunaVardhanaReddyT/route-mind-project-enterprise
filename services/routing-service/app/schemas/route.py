from pydantic import BaseModel
from typing import List, Optional


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
    stops: List[int]

    class Config:
        from_attributes = True