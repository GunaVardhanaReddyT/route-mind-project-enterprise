"""
Hub Configuration - Dynamic depot locations
"""

HUB_DEPOTS = {
    1: {
        "lat": 28.6139,
        "lon": 77.2090,
        "label": "Delhi NCR Hub",
        "city": "Delhi"
    },
    2: {
        "lat": 19.0760,
        "lon": 72.8777,
        "label": "Mumbai Hub",
        "city": "Mumbai"
    },
    3: {
        "lat": 12.9716,
        "lon": 77.5946,
        "label": "Bangalore Hub",
        "city": "Bangalore"
    }
}

def get_depot_coords(hub_id: int):
    """Get depot coordinates for a hub"""
    depot = HUB_DEPOTS.get(hub_id, HUB_DEPOTS[1])
    return (depot["lat"], depot["lon"])

def get_depot_info(hub_id: int):
    """Get full depot information for visualization"""
    return HUB_DEPOTS.get(hub_id, HUB_DEPOTS[1])
