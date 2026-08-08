"""
OpenStreetMap Distance Calculator
Uses OSRM (Open Source Routing Machine) for real road distances

Optional enhancement: Replace Haversine with actual road network distances
"""

import logging
import requests
from typing import Tuple, List, Optional, Dict
import time

logger = logging.getLogger(__name__)


class OSRMDistanceCalculator:
    """
    Calculate real road distances using OpenStreetMap data via OSRM
    
    Public OSRM instance: http://router.project-osrm.org
    For production, host your own OSRM instance
    """
    
    def __init__(self, osrm_url: str = "http://router.project-osrm.org"):
        self.osrm_url = osrm_url
        self.cache = {}  # Simple in-memory cache
        
    def get_distance_matrix(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Get distance matrix using OSRM table service
        
        Args:
            locations: List of (lat, lon) tuples
            
        Returns:
            Distance matrix in meters
        """
        n = len(locations)
        
        # Check cache
        cache_key = str(locations)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Format: lon,lat;lon,lat;...
            coords = ";".join([f"{lon},{lat}" for lat, lon in locations])
            url = f"{self.osrm_url}/table/v1/driving/{coords}"
            
            params = {
                "annotations": "distance,duration"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data["code"] == "Ok":
                    # Extract distance matrix (in meters)
                    distance_matrix = [[int(dist) for dist in row] for row in data["distances"]]
                    
                    # Cache result
                    self.cache[cache_key] = distance_matrix
                    
                    return distance_matrix
                else:
                    logger.warning(f"OSRM returned error: {data.get('message')}")
                    return self._fallback_haversine(locations)
            else:
                logger.warning(f"OSRM HTTP error: {response.status_code}")
                return self._fallback_haversine(locations)
                
        except requests.Timeout:
            logger.warning("OSRM request timeout, using Haversine fallback")
            return self._fallback_haversine(locations)
        except Exception as e:
            logger.error(f"OSRM request failed: {e}, using Haversine fallback")
            return self._fallback_haversine(locations)
    
    def _fallback_haversine(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """Fallback to Haversine distance if OSRM fails"""
        import numpy as np
        from math import sin, cos, sqrt, atan2, radians
        
        n = len(locations)
        lats = np.array([loc[0] for loc in locations])
        lons = np.array([loc[1] for loc in locations])
        
        lat_rad = np.radians(lats)
        lon_rad = np.radians(lons)
        
        dlat = lat_rad[:, np.newaxis] - lat_rad
        dlon = lon_rad[:, np.newaxis] - lon_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat_rad[:, np.newaxis]) * np.cos(lat_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        distance_matrix = (6371 * c * 1000).astype(int).tolist()
        
        return distance_matrix
    
    def calculate_distance_matrix(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """Alias for get_distance_matrix for compatibility"""
        return self.get_distance_matrix(locations)
    
    @staticmethod
    def get_route(start: Tuple[float, float], end: Tuple[float, float]) -> Optional[Dict]:
        """
        Get detailed route between two points
        
        Returns route geometry, distance, duration
        """
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
            params = {"overview": "full", "geometries": "geojson"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["code"] == "Ok":
                    route = data["routes"][0]
                    return {
                        "distance_m": route["distance"],
                        "duration_s": route["duration"],
                        "geometry": route["geometry"]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"OSRM route request failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    calc = OSRMDistanceCalculator()
    
    # Delhi locations
    depot = (28.6139, 77.2090)  # Connaught Place
    stop1 = (28.5355, 77.3910)  # Noida
    stop2 = (28.4595, 77.0266)  # Gurgaon
    
    locations = [depot, stop1, stop2]
    
    print("Calculating distances using OpenStreetMap...")
    matrix = calc.get_distance_matrix(locations)
    
    print(f"Distance depot → stop1: {matrix[0][1] / 1000:.2f} km")
    print(f"Distance depot → stop2: {matrix[0][2] / 1000:.2f} km")
