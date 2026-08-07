from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime, time


class BaseConstraint(ABC):
    """Base class for all routing constraints"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        """Return True if valid, False if violation"""
        pass


class CODLimitConstraint(BaseConstraint):
    """Indian Constraint: Cash on Delivery limit per vehicle"""

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
    """Indian Constraint: Truck restrictions in metro zones"""

    # Trucks banned in metros 8 AM - 10 PM
    RESTRICTED_START = time(8, 0)
    RESTRICTED_END = time(22, 0)

    @property
    def name(self) -> str:
        return "ZONE_TIMING_RESTRICTION"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        vehicle_type = vehicle.get("type", "van")
        if vehicle_type != "truck":
            return True  # Only trucks restricted

        arrival_time = context.get("arrival_time")
        if not arrival_time:
            return True

        if isinstance(arrival_time, datetime):
            arrival_time = arrival_time.time()

        # Check if arrival is during restricted hours
        return not (self.RESTRICTED_START <= arrival_time <= self.RESTRICTED_END)


class OddEvenConstraint(BaseConstraint):
    """Indian Constraint: Odd-even plate restriction"""

    @property
    def name(self) -> str:
        return "ODD_EVEN_PLATE"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        plate_number = vehicle.get("plate_number", "")
        date = context.get("date", datetime.now())

        if isinstance(date, datetime):
            date = date.date()

        # Extract last digit of plate
        last_digit = None
        for char in reversed(plate_number):
            if char.isdigit():
                last_digit = int(char)
                break

        if last_digit is None:
            return True

        day_of_month = date.day
        plate_parity = last_digit % 2
        date_parity = day_of_month % 2

        return plate_parity == date_parity


class TimeWindowConstraint(BaseConstraint):
    """Constraint: Delivery must be within time window"""

    @property
    def name(self) -> str:
        return "TIME_WINDOW"

    def check(self, vehicle: Dict, stop: Dict, context: Dict) -> bool:
        tw_start = stop.get("time_window_start")
        tw_end = stop.get("time_window_end")
        arrival = context.get("arrival_time")

        if not tw_start or not tw_end or not arrival:
            return True

        return tw_start <= arrival <= tw_end


# Registry for easy constraint loading
CONSTRAINT_REGISTRY = {
    "cod_limit": CODLimitConstraint,
    "zone_timing": ZoneTimingConstraint,
    "odd_even": OddEvenConstraint,
    "time_window": TimeWindowConstraint,
}


def get_constraint(name: str, **kwargs) -> BaseConstraint:
    """Factory function to create constraints"""
    if name not in CONSTRAINT_REGISTRY:
        raise ValueError(f"Unknown constraint: {name}")
    return CONSTRAINT_REGISTRY[name](**kwargs)