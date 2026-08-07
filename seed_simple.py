#!/usr/bin/env python3
"""Simple seed script - run from host or container"""

import asyncio
import sys
import os

# Add the routing service to path
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://routemind:secure_password_change_me@db:5432/routemind_db')

# Sample Delhi coordinates
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
    {"plate": "DL01AB1234", "capacity": 100, "cod_limit": 50000},
    {"plate": "DL02CD5678", "capacity": 200, "cod_limit": 50000},
    {"plate": "DL03EF9012", "capacity": 100, "cod_limit": 50000},
]


async def seed_data():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Insert vehicles
            for v in SAMPLE_VEHICLES:
                await session.execute(
                    """INSERT INTO vehicles (plate_number, capacity, cod_limit, is_active, hub_id)
                       VALUES (:plate, :capacity, :cod_limit, true, 1)
                       ON CONFLICT (plate_number) DO NOTHING""",
                    {"plate": v["plate"], "capacity": v["capacity"], "cod_limit": v["cod_limit"]}
                )
            
            # Insert stops
            for s in SAMPLE_STOPS:
                tw_start = datetime.now() + timedelta(hours=1)
                tw_end = datetime.now() + timedelta(hours=8)
                
                await session.execute(
                    """INSERT INTO stops (address, lat, lon, cod_amount, time_window_start, 
                                          time_window_end, is_completed, hub_id)
                       VALUES (:address, :lat, :lon, :cod, :tw_start, :tw_end, false, 1)""",
                    {
                        "address": s["address"], 
                        "lat": s["lat"], 
                        "lon": s["lon"], 
                        "cod": s["cod"],
                        "tw_start": tw_start,
                        "tw_end": tw_end
                    }
                )
            
            await session.commit()
            print(f" Data seeded successfully!")
            print(f"   - {len(SAMPLE_VEHICLES)} vehicles added")
            print(f"   - {len(SAMPLE_STOPS)} stops added")
            
        except Exception as e:
            print(f" Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
