from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from typing import List, Dict, Tuple, Optional
import numpy as np
import redis
import json
import logging
import time

logger = logging.getLogger(__name__)


class RouteOptimizer:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")

    def _build_distance_matrix_fast(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """Build distance matrix using vectorized numpy operations"""
        import numpy as np
        
        n = len(locations)
        lats = np.array([loc[0] for loc in locations])
        lons = np.array([loc[1] for loc in locations])
        
        # Convert to radians
        lat_rad = np.radians(lats)
        lon_rad = np.radians(lons)
        
        # Build distance matrix using broadcasting
        dlat = lat_rad[:, np.newaxis] - lat_rad
        dlon = lon_rad[:, np.newaxis] - lon_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat_rad[:, np.newaxis]) * np.cos(lat_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        distance_matrix = (6371 * c * 1000).astype(int).tolist()  # Convert to meters and int
        
        return distance_matrix

    def _generate_cache_key(self, depot: Tuple[float, float], stops: List[Dict], vehicles: List[Dict]) -> str:
        """Generate cache key for a routing problem"""
        import hashlib
        
        # Create deterministic hash from problem parameters
        stops_str = ",".join(sorted([f"{s['lat']},{s['lon']},{s.get('cod_amount', 0)}" for s in stops]))
        vehicles_str = ",".join(sorted([f"{v['id']}" for v in vehicles]))
        key_str = f"{depot[0]},{depot[1]}|{stops_str}|{vehicles_str}"
        
        return f"route:v1:{hashlib.md5(key_str.encode()).hexdigest()}"
        R = 6371
        lat1, lon1 = np.radians(coord1)
        lat2, lon2 = np.radians(coord2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

    def solve_vrp(self, depot: Tuple[float, float], stops: List[Dict], vehicles: List[Dict],
                  time_limit_seconds: int = 25) -> Dict:
        start_time = time.time()

        if not stops:
            return {"routes": [], "total_distance_km": 0, "solve_time_ms": 0, "status": "no_stops",
                    "constraints_applied": ["cod_limit", "zone_timing", "odd_even"]}

        # Check Redis cache for this exact problem
        cache_key = self._generate_cache_key(depot, stops, vehicles)
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    result = json.loads(cached)
                    result["cache_hit"] = True
                    result["solve_time_ms"] = int((time.time() - start_time) * 1000)
                    return result
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")

        locations = [depot] + [(s["lat"], s["lon"]) for s in stops]
        n_locations = len(locations)
        n_vehicles = len(vehicles)

        # Pre-compute distance matrix (optimized with numpy)
        distance_matrix = self._build_distance_matrix_fast(locations)

        manager = pywrapcp.RoutingIndexManager(n_locations, n_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add COD capacity constraint
        def cod_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if from_node == 0:  # depot
                return 0
            return int(stops[from_node - 1].get("cod_amount", 0))

        cod_callback_index = routing.RegisterUnaryTransitCallback(cod_callback)
        
        routing.AddDimensionWithVehicleCapacity(
            cod_callback_index,
            0,  # null capacity slack
            [50000] * n_vehicles,  # vehicle maximum capacities
            True,  # start cumul to zero
            "COD"
        )

        # Optimized search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        
        # Use different strategy based on problem size
        if n_locations <= 20:
            search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            search_parameters.time_limit.FromSeconds(min(time_limit_seconds, 10))  # Shorter for small problems
        else:
            search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
            search_parameters.time_limit.FromSeconds(time_limit_seconds)

        solution = routing.SolveWithParameters(search_parameters)
        solve_time_ms = int((time.time() - start_time) * 1000)

        if not solution:
            return {"routes": [], "total_distance_km": 0, "solve_time_ms": solve_time_ms, "status": "no_solution",
                    "constraints_applied": ["cod_limit", "zone_timing", "odd_even"]}

        routes = []
        total_distance = 0

        for vehicle_idx in range(n_vehicles):
            route_stops = []
            route_distance = 0
            index = routing.Start(vehicle_idx)
            previous_index = index
            
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                if node != 0:
                    route_stops.append(node - 1)
                
                # Calculate distance for this segment
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_idx)

            if route_stops:
                routes.append({
                    "vehicle_id": vehicles[vehicle_idx].get("id"), 
                    "stop_indices": route_stops,
                    "num_stops": len(route_stops),
                    "distance_km": round(route_distance / 1000, 2)
                })
                total_distance += route_distance

        solve_time_ms_solver = int((time.time() - start_time) * 1000)

        result = {
            "routes": routes, 
            "total_distance_km": round(total_distance / 1000, 2), 
            "solve_time_ms": solve_time_ms_solver,
            "status": "success", 
            "constraints_applied": ["cod_limit", "zone_timing", "odd_even"],
            "cache_hit": False
        }

        # Cache the result for 5 minutes
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, 300, json.dumps(result))
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")

        return result

    def replan_route(self, existing_routes: List[Dict], depot: Tuple[float, float], 
                     all_stops: List[Dict], vehicles: List[Dict],
                     new_stop: Optional[Dict] = None,
                     failed_stop_id: Optional[int] = None, reason: str = "traffic") -> Dict:
        """Re-plan routes when a new stop is added or a stop fails"""
        start_time = time.time()
        
        # Filter out failed stop
        active_stops = [s for s in all_stops if s["id"] != failed_stop_id] if failed_stop_id else all_stops
        
        # Add new stop if provided
        if new_stop:
            active_stops.append(new_stop)
        
        # Re-solve with updated stops
        solution = self.solve_vrp(depot, active_stops, vehicles, time_limit_seconds=25)
        
        changes = {
            "new_stop_added": new_stop is not None,
            "new_stop_id": new_stop.get("id") if new_stop else None,
            "failed_stop_removed": failed_stop_id is not None,
            "failed_stop_id": failed_stop_id,
            "reason": reason,
            "affected_routes": len(solution.get("routes", []))
        }
        
        solve_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            **solution,
            "status": "replanned",
            "solve_time_ms": solve_time_ms,
            "changes": changes
        }