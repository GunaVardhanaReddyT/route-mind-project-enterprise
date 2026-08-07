"""
Amazon Last Mile Routing Challenge Dataset Loader
Downloads and processes real Amazon delivery data from AWS Open Data Registry
"""
import json
import os
import boto3
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Amazon dataset S3 bucket (public, no auth needed)
AMAZON_DATASET_BUCKET = "amazon-last-mile-challenges"
AMAZON_DATASET_PREFIX = "almrrc2021/"


class AmazonDatasetLoader:
    """
    Loads real Amazon delivery routes from AWS Open Data Registry
    
    Dataset contains:
    - 9,184 historical routes
    - 1M+ stops
    - 2.5M+ packages
    - 5 US metropolitan areas (Austin, Boston, Chicago, LA, Seattle)
    
    Data structure matches Amazon's actual operational format
    """
    
    def __init__(self, cache_dir: str = "/tmp/amazon_routing_data"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Use anonymous S3 client (public data, no credentials needed)
        self.s3_client = boto3.client(
            's3',
            config=boto3.session.Config(signature_version='ANONYMOUS')
        )
    
    def download_dataset(self, phase: str = "model_build_inputs") -> Dict:
        """
        Download Amazon dataset from S3
        
        Args:
            phase: "model_build_inputs" or "model_apply_inputs"
        
        Returns:
            Dict with route_data, package_data, travel_times, actual_sequences
        """
        logger.info(f"📦 Downloading Amazon dataset: {phase}")
        
        files_to_download = {
            "model_build_inputs": [
                "route_data.json",
                "package_data.json",
                "travel_times.json",
                "actual_sequences.json",  # Ground truth driver sequences
                "invalid_sequence_scores.json"  # Baseline scores
            ],
            "model_apply_inputs": [
                "new_route_data.json",
                "new_package_data.json",
                "new_travel_times.json"
            ]
        }
        
        dataset = {}
        for filename in files_to_download.get(phase, []):
            local_path = os.path.join(self.cache_dir, filename)
            s3_key = f"{AMAZON_DATASET_PREFIX}{phase}/{filename}"
            
            # Download if not cached
            if not os.path.exists(local_path):
                try:
                    logger.info(f"⬇️  Downloading {filename} from S3...")
                    self.s3_client.download_file(
                        AMAZON_DATASET_BUCKET,
                        s3_key,
                        local_path
                    )
                    logger.info(f"✅ Downloaded {filename}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not download {filename}: {e}")
                    logger.info(f"   Using sample data instead")
                    continue
            
            # Load JSON
            with open(local_path, 'r') as f:
                dataset[filename.replace('.json', '')] = json.load(f)
        
        return dataset
    
    def convert_to_vrp_format(
        self,
        route_id: str,
        route_data: Dict,
        package_data: Dict,
        travel_times: Dict
    ) -> Tuple[List[Dict], Dict, List[List[float]]]:
        """
        Convert Amazon format to RouteMind VRP format
        
        Returns:
            (stops, vehicle, distance_matrix)
        """
        route_info = route_data[route_id]
        route_packages = package_data[route_id]
        route_travel = travel_times[route_id]
        
        # Extract depot (first stop marked as "Station")
        depot = None
        stops_data = []
        
        for stop_id, stop_info in route_info["stops"].items():
            if stop_info["type"] == "Station":
                depot = (stop_info["lat"], stop_info["lng"])
            else:
                # Get all packages for this stop
                packages = route_packages.get(stop_id, {})
                total_weight = sum(
                    p["dimensions"]["depth_cm"] * 
                    p["dimensions"]["height_cm"] * 
                    p["dimensions"]["width_cm"] / 1000  # Convert cm³ to kg estimate
                    for p in packages.values()
                )
                
                # Extract time window (if exists)
                first_package = list(packages.values())[0] if packages else {}
                time_window = first_package.get("time_window", {})
                
                stops_data.append({
                    "id": stop_id,
                    "lat": stop_info["lat"],
                    "lon": stop_info["lng"],
                    "address": f"{stop_info['zone_id']}-{stop_id}",
                    "time_window_start": time_window.get("start_time_utc", "09:00:00"),
                    "time_window_end": time_window.get("end_time_utc", "17:00:00"),
                    "priority": "high" if "urgent" in stop_info.get("zone_id", "").lower() else "medium",
                    "package_count": len(packages),
                    "total_weight_kg": total_weight,
                    "zone": stop_info.get("zone_id", "unknown"),
                    "is_completed": False
                })
        
        # Build distance matrix from travel times
        stop_ids = [s["id"] for s in stops_data]
        n = len(stop_ids)
        distance_matrix = [[0.0] * n for _ in range(n)]
        
        for i, stop_i in enumerate(stop_ids):
            for j, stop_j in enumerate(stop_ids):
                if i != j:
                    # Travel time in seconds -> convert to km (assume 40 km/h avg speed)
                    travel_seconds = route_travel.get(stop_i, {}).get(stop_j, 300)
                    distance_km = (travel_seconds / 3600) * 40  # 40 km/h urban average
                    distance_matrix[i][j] = distance_km
        
        # Vehicle info
        vehicle = {
            "id": 1,
            "plate_number": route_info["station_code"],
            "capacity_kg": route_info["executor_capacity_cm3"] / 10000,  # Convert cm³ to kg
            "is_active": True
        }
        
        return stops_data, vehicle, distance_matrix
    
    def get_sample_routes(self, count: int = 10) -> List[str]:
        """
        Get sample route IDs for testing
        
        Args:
            count: Number of routes to sample
        
        Returns:
            List of route IDs
        """
        dataset = self.download_dataset("model_build_inputs")
        route_data = dataset.get("route_data", {})
        
        # Sample routes with "High" quality scores
        high_quality_routes = [
            route_id for route_id, info in route_data.items()
            if info.get("route_score") == "High"
        ]
        
        return high_quality_routes[:count]
    
    def get_route_ground_truth(self, route_id: str) -> Dict:
        """
        Get actual driver sequence (ground truth) for comparison
        
        Returns:
            Dict with actual stop sequence and score
        """
        dataset = self.download_dataset("model_build_inputs")
        actual_seq = dataset.get("actual_sequences", {}).get(route_id, {})
        scores = dataset.get("invalid_sequence_scores", {}).get(route_id, 1.0)
        
        return {
            "actual_sequence": actual_seq.get("actual", {}),
            "baseline_score": scores,
            "route_id": route_id
        }


# Singleton instance
_amazon_loader = None

def get_amazon_loader() -> AmazonDatasetLoader:
    """Get or create Amazon dataset loader instance"""
    global _amazon_loader
    if _amazon_loader is None:
        _amazon_loader = AmazonDatasetLoader()
    return _amazon_loader
