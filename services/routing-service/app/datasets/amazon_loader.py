"""
Amazon Last Mile Routing Challenge Dataset Loader
https://registry.opendata.aws/amazon-last-mile-challenges/

Optional: Load real-world routing data from Amazon's public dataset
"""

import json
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class AmazonDatasetLoader:
    """
    Load data from Amazon Last Mile Routing Research Challenge
    
    Dataset contains:
    - 6,000+ historical routes
    - 1M+ stops
    - 2.5M+ packages
    - 17 depots
    """
    
    BASE_URL = "https://amazon-last-mile-challenges.s3.amazonaws.com/almrrc2021"
    
    @staticmethod
    def load_route_data(route_id: str) -> Optional[Dict]:
        """
        Load a specific route from Amazon dataset
        
        Note: This is a demonstration. In production, you'd download
        the dataset once and load from local storage.
        """
        try:
            url = f"{AmazonDatasetLoader.BASE_URL}/model_build_inputs/route_data_{route_id}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Amazon dataset route {route_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load Amazon dataset: {e}")
            return None
    
    @staticmethod
    def convert_to_routemind_format(amazon_data: Dict) -> Dict:
        """
        Convert Amazon dataset format to RouteMind format
        
        Amazon format:
        {
            "stops": {
                "stop_id": {
                    "lat": float,
                    "lng": float,
                    "type": "Dropoff" | "Pickup",
                    "zone_id": str
                }
            }
        }
        
        RouteMind format:
        {
            "stops": [{"id": int, "lat": float, "lon": float, "cod_amount": float}],
            "depot": (lat, lon)
        }
        """
        stops = []
        depot = None
        
        for stop_id, stop_data in amazon_data.get("stops", {}).items():
            if stop_data.get("type") == "Station":
                # This is the depot
                depot = (stop_data["lat"], stop_data["lng"])
            else:
                stops.append({
                    "id": len(stops) + 1,
                    "lat": stop_data["lat"],
                    "lon": stop_data["lng"],
                    "cod_amount": 5000,  # Default COD for Amazon data
                    "address": f"Amazon Stop {stop_id}",
                    "zone_id": stop_data.get("zone_id")
                })
        
        return {
            "stops": stops,
            "depot": depot if depot else (stops[0]["lat"], stops[0]["lon"]) if stops else (0, 0)
        }
    
    @staticmethod
    def get_sample_routes() -> List[str]:
        """Get list of sample route IDs for demonstration"""
        return [
            "RouteID_0001a3c2-4a1e-4c91-a2db-1234567890ab",
            "RouteID_0002b4d3-5b2f-5d92-b3ec-2345678901bc",
            # Add more as needed
        ]


# Example usage
if __name__ == "__main__":
    loader = AmazonDatasetLoader()
    
    # Note: Actual route IDs from the dataset
    # For demo, this would need the actual dataset downloaded
    print("Amazon Dataset Loader - Ready")
    print("To use: download dataset from https://registry.opendata.aws/amazon-last-mile-challenges/")
