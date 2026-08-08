"""
Simple VRP solver wrapper for live routing
"""
from app.solver.engine import RouteOptimizer
from app.core.config import settings


def solve_vrp(stops, vehicles, distance_matrix=None, apply_indian_constraints=True):
    """
    Solve VRP problem
    
    Args:
        stops: List of stop dicts with id, lat, lon, etc.
        vehicles: List of vehicle dicts
        distance_matrix: Optional pre-computed distance matrix
        apply_indian_constraints: Whether to apply Indian logistics constraints
    
    Returns:
        Solution dict with routes, total_distance, solve_time_ms
    """
    optimizer = RouteOptimizer(redis_url=settings.REDIS_URL)
    
    # Convert to solver format
    depot = (28.6139, 77.2090)  # Default Delhi hub
    
    solution = optimizer.solve_vrp(
        depot=depot,
        stops=stops,
        vehicles=vehicles
    )
    
    return solution
