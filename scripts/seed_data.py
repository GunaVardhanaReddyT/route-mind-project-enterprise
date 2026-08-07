#!/usr/bin/env python3
"""Seed database with sample Amazon dataset stops"""

import asyncio
import asyncpg
import random
from datetime import datetime, timedelta

# Sample Delhi coordinates (Amazon dataset adapted for India)
DELHI_DEPOT = (28.6139, 77.2090)

SAMPLE_STOPS = [
    {"lat": 28.6289, "lon": 77.2065, "address": "Connaught Place", "cod": 5000},
    {"lat": 28.5355, "lon": 77.3910, "address": "Noida Sector 18", "cod": 12000},
    {"lat": 28.4595, "lon": 77.0266, "address": "Gurgaon Cyber City", "cod": 25000},
    {"lat": 28.7041, "lon": 77.1025, "address": "Delhi University", "cod": 3000},
    {"lat": 28.5244, "lon": 77.1855, "address": "Nehru Place", "cod": 15000},
    {"lat": 28.6692, "lon": 77.4538, "address": "Ghaziabad", "cod": 8000},
    {"lat": 28.4089, "lon": 77.3178, "address": "Faridabad", "cod": 10000},
    {"lat": 28.6517, "lon": 77.2219, "address": "Civil Lines", "cod": 6000},
    {"lat": 28.5706, "lon": 77.3272, "address": "Mayur Vihar", "cod": 4000},
    {"lat": 28.6304, "lon": 77.2177, "address": "Kashmere Gate", "cod": 7000},
]

SAMPLE_VEHICLES = [
    {"plate": "DL01AB1234", "type": "van", "capacity": 100, "cod_limit": 50000},
    {"plate": "DL02CD5678", "type": "truck", "capacity": 200, "cod_limit": 50000},
    {"plate": "DL03EF9012", "type": "van", "capacity": 100, "cod_limit": 50000},
]


async def seed_data():
    conn = await asyncpg.connect(
        "postgresql+asyncpg://routemind:RouteMind2024SecurePass@localhost:5432/routemind_db"
    )

    # Insert vehicles
    for i, v in enumerate(SAMPLE_VEHICLES, start=1):
        await conn.execute(
            """INSERT INTO vehicles (plate_number, type, capacity, cod_limit, is_active, hub_id)
               VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (plate_number) DO NOTHING""",
            v["plate"], v["type"], v["capacity"], v["cod_limit"], True, 1
        )

    # Insert stops
    for i, s in enumerate(SAMPLE_STOPS, start=1):
        tw_start = datetime.now() + timedelta(hours=1)
        tw_end = datetime.now() + timedelta(hours=8)

        await conn.execute(
            """INSERT INTO stops (address, lat, lon, cod_amount, time_window_start, time_window_end, is_completed,
                                  hub_id)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8) ON CONFLICT DO NOTHING""",
            s["address"], s["lat"], s["lon"], s["cod"], tw_start, tw_end, False, 1
        )

    print("✅ Data seeded successfully!")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_data())