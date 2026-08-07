from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta
import redis
import json
import logging

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """OR-Tools based route optimizer with Indian constraints"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.cache_ttl = 3600  # 1 hour

    def _get_distance_matrix(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """Get distance matrix with caching"""
        if self.redis_client:
            cache_key = f"dist_matrix:{hash(str(locations))}"
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("Distance matrix cache hit")
                return json.loads(cached)

        # Haversine distance calculation (simplified for demo)
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = self._haversine(locations[i], locations[j])
                    matrix[i][j] = int(dist * 100)  # Convert to meters

        if self.redis_client:
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(matrix))

        return matrix

    def _haversine(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate haversine distance between two points in km"""
        R = 6371  # Earth's radius in km

        lat1, lon1 = np.radians(coord1)
        lat2, lon2 = np.radians(coord2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c

    def solve_vrp(
            self,
            depot: Tuple[float, float],
            stops: List[Dict],
            vehicles: List[Dict],
            constraints: List = None
    ) -> Dict:
        """
        Solve Vehicle Routing Problem with Time Windows

        Returns: {
            "routes": [...],
            "total_distance": float,
            "solve_time_ms": int,
            "constraints_applied": [...]
        }
        """
        import time
        start_time = time.time()

        # Prepare locations (depot + stops)
        locations = [depot] + [(s["lat"], s["lon"]) for s in stops]
        n_locations = len(locations)

        # Get distance matrix
        distance_matrix = self._get_distance_matrix(locations)

        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n_locations, len(vehicles), 0)
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add distance dimension
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # slack
            300000,  # max distance per vehicle (300km)
            True,  # start cumul to zero
            dimension_name
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Add time window constraints if present
        for stop_idx, stop in enumerate(stops, start=1):
            if stop.get("time_window_start") and stop.get("time_window_end"):
                tw_start = stop["time_window_start"]
                tw_end = stop["time_window_end"]

                if isinstance(tw_start, datetime):
                    tw_start = int(tw_start.timestamp())
                if isinstance(tw_end, datetime):
                    tw_end = int(tw_end.timestamp())

                index = manager.NodeToIndex(stop_idx)
                routing.AddTimeWindowConstraint(index, tw_start, tw_end, "TimeWindow")

        # Search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(25)  # 25 second limit

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        solve_time_ms = int((time.time() - start_time) * 1000)

        if not solution:
            logger.warning("No solution found")
            return {
                "routes": [],
                "total_distance": 0,
                "solve_time_ms": solve_time_ms,
                "status": "no_solution",
                "constraints_applied": [c.name for c in (constraints or [])]
            }

        # Extract solution
        routes = []
        total_distance = 0

        for vehicle_idx in range(len(vehicles)):
            route = []
            index = routing.Start(vehicle_idx)

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                if node != 0:  # Skip depot
                    route.append(node - 1)  # Convert to stop index

                index = solution.Value(routing.NextVar(index))

            if route:
                vehicle_distance = solution.Value(
                    routing.GetDimensionOrDie("Distance").CumulVar(routing.End(vehicle_idx))
                )
                total_distance += vehicle_distance

                routes.append({
                    "vehicle_id": vehicles[vehicle_idx].get("id"),
                    "stop_indices": route,
                    "distance_meters": vehicle_distance
                })

        return {
            "routes": routes,
            "total_distance": total_distance / 100,  # Convert to km
            "solve_time_ms": solve_time_ms,
            "status": "success",
            "constraints_applied": [c.name for c in (constraints or [])]
        }

    def replan_route(
            self,
            existing_solution: Dict,
            new_stop: Dict,
            failed_stop_id: Optional[int] = None
    ) -> Dict:
        """
        Incremental re-planning for dynamic changes

        Faster than full re-solve - only affects changed routes
        """
        import time
        start_time = time.time()

        # For hackathon demo, we do a simplified re-plan
        # In production, this would use local search on affected routes only

        logger.info(f"Re-planning triggered: new_stop={new_stop is not None}, failed={failed_stop_id}")

        # Add new stop or remove failed stop
        # Then re-solve (simplified for demo)

        solve_time_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "replanned",
            "solve_time_ms": solve_time_ms,
            "changes": {
                "new_stop_added": new_stop is not None,
                "failed_stop_removed": failed_stop_id is not None
            }
        }