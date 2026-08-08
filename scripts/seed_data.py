#!/usr/bin/env python3
"""Seed database with sample stops for all hubs"""

import asyncio
import asyncpg
import random
from datetime import datetime, timedelta

# Hub configurations
HUBS = {
    1: {
        "name": "Delhi Hub",
        "depot": (28.6139, 77.2090),
        "stops": [
            {"lat": 28.6289, "lon": 77.2065, "address": "Connaught Place", "cod": 5000},
            {"lat": 28.5355, "lon": 77.3910, "address": "Noida Sector 18", "cod": 12000},
            {"lat": 28.4595, "lon": 77.0266, "address": "Gurgaon Cyber City", "cod": 25000},
            {"lat": 28.7041, "lon": 77.1025, "address": "Delhi University", "cod": 3000},
            {"lat": 28.5244, "lon": 77.1855, "address": "Nehru Place", "cod": 15000},
            {"lat": 28.6692, "lon": 77.4538, "address": "Ghaziabad", "cod": 8000},
            {"lat": 28.4089, "lon": 77.3178, "address": "Faridabad", "cod": 10000},
            {"lat": 28.6517, "lon": 77.2219, "address": "Civil Lines", "cod": 6000},
        ],
        "vehicles": [
            {"plate": "DL01AB1234", "type": "van", "capacity": 100, "cod_limit": 50000},
            {"plate": "DL02CD5678", "type": "truck", "capacity": 200, "cod_limit": 50000},
            {"plate": "DL03EF9012", "type": "van", "capacity": 100, "cod_limit": 50000},
        ]
    },
    2: {
        "name": "Mumbai Hub",
        "depot": (19.0760, 72.8777),
        "stops": [
            {"lat": 19.0728, "lon": 72.8826, "address": "Fort", "cod": 8000},
            {"lat": 19.0176, "lon": 72.8561, "address": "Colaba", "cod": 15000},
            {"lat": 19.1136, "lon": 72.8697, "address": "Dadar", "cod": 6000},
            {"lat": 19.0596, "lon": 72.8295, "address": "Bandra", "cod": 20000},
            {"lat": 18.9220, "lon": 72.8347, "address": "Andheri", "cod": 10000},
            {"lat": 19.2183, "lon": 72.9781, "address": "Thane", "cod": 12000},
            {"lat": 19.2015, "lon": 73.0967, "address": "Navi Mumbai", "cod": 9000},
            {"lat": 19.0330, "lon": 73.0297, "address": "Vashi", "cod": 7000},
        ],
        "vehicles": [
            {"plate": "MH01AB1234", "type": "van", "capacity": 100, "cod_limit": 50000},
            {"plate": "MH02CD5678", "type": "truck", "capacity": 200, "cod_limit": 50000},
            {"plate": "MH03EF9012", "type": "van", "capacity": 100, "cod_limit": 50000},
        ]
    },
    3: {
        "name": "Bangalore Hub",
        "depot": (12.9716, 77.5946),
        "stops": [
            {"lat": 12.9716, "lon": 77.5946, "address": "MG Road", "cod": 10000},
            {"lat": 12.9698, "lon": 77.7499, "address": "Whitefield", "cod": 18000},
            {"lat": 13.0358, "lon": 77.5970, "address": "Yelahanka", "cod": 8000},
            {"lat": 12.9352, "lon": 77.6245, "address": "Koramangala", "cod": 15000},
            {"lat": 12.9279, "lon": 77.6271, "address": "HSR Layout", "cod": 12000},
            {"lat": 13.0116, "lon": 77.5509, "address": "Malleswaram", "cod": 6000},
            {"lat": 12.9611, "lon": 77.6387, "address": "Indiranagar", "cod": 9000},
            {"lat": 12.8406, "lon": 77.6595, "address": "Electronic City", "cod": 20000},
        ],
        "vehicles": [
            {"plate": "KA01AB1234", "type": "van", "capacity": 100, "cod_limit": 50000},
            {"plate": "KA02CD5678", "type": "truck", "capacity": 200, "cod_limit": 50000},
            {"plate": "KA03EF9012", "type": "van", "capacity": 100, "cod_limit": 50000},
        ]
    }
}


async def seed_data():
    # Use the docker-compose database connection
    conn = await asyncpg.connect(
        "postgresql://routemind:secure_password_change_me@localhost:5432/routemind_db"
    )

    try:
        total_vehicles = 0
        total_stops = 0
        
        for hub_id, hub_data in HUBS.items():
            print(f"\n📍 Seeding {hub_data['name']}...")
            
            # Insert vehicles for this hub
            for v in hub_data["vehicles"]:
                await conn.execute(
                    """INSERT INTO vehicles (plate_number, capacity_kg, is_active, hub_id)
                       VALUES ($1, $2, $3, $4) ON CONFLICT (plate_number) DO NOTHING""",
                    v["plate"], v["capacity"], True, hub_id
                )
                total_vehicles += 1

            # Insert stops for this hub
            for s in hub_data["stops"]:
                tw_start = datetime.now() + timedelta(hours=1)
                tw_end = datetime.now() + timedelta(hours=8)

                await conn.execute(
                    """INSERT INTO stops (address, lat, lon, time_window_start, time_window_end, is_completed,
                                          hub_id, priority, package_count, zone, total_weight_kg)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)""",
                    s["address"], s["lat"], s["lon"], tw_start, tw_end, False, hub_id,
                    "medium", 5, "central", 50.0
                )
                total_stops += 1
            
            print(f"   ✓ {len(hub_data['vehicles'])} vehicles")
            print(f"   ✓ {len(hub_data['stops'])} stops")

        print(f"\n✅ ALL DATA SEEDED SUCCESSFULLY!")
        print(f"   📦 Total: {total_vehicles} vehicles, {total_stops} stops across 3 hubs")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_data())