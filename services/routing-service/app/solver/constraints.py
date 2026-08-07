from abc import ABC, abstractmethod
from typing import Dict
from datetime import time


class BaseConstraint(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        pass


class CODLimitConstraint(BaseConstraint):
    def __init__(self, limit: float = 50000.0):
        self.limit = limit

    @property
    def name(self) -> str:
        return "COD_LIMIT_50K"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        current_cod = vehicle.get("current_cod", 0.0)
        stop_cod = stop.get("cod_amount", 0.0)
        return (current_cod + stop_cod) <= self.limit


class ZoneTimingConstraint(BaseConstraint):
    RESTRICTED_START = time(8, 0)
    RESTRICTED_END = time(22, 0)

    @property
    def name(self) -> str:
        return "ZONE_TIMING_RESTRICTION"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        vehicle_type = vehicle.get("type", "van")
        if vehicle_type != "truck":
            return True
        return True  # Simplified for demo


class OddEvenConstraint(BaseConstraint):
    @property
    def name(self) -> str:
        return "ODD_EVEN_PLATE"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        return True  # Simplified for demo


CONSTRAINT_REGISTRY = {
    "cod_limit": CODLimitConstraint,
    "zone_timing": ZoneTimingConstraint,
    "odd_even": OddEvenConstraint,
}


def get_constraint(name: str, **kwargs) -> BaseConstraint:
    if name not in CONSTRAINT_REGISTRY:
        raise ValueError(f"Unknown constraint: {name}")
    return CONSTRAINT_REGISTRY[name](**kwargs)