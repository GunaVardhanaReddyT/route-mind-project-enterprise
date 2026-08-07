#!/usr/bin/env python3
"""Seed all hubs with data - Delhi, Mumbai, Bangalore"""

import asyncio
import sys
import os

sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://routemind:secure_password_change_me@db:5432/routemind_db')

# Hub 1: Delhi NCR
DELHI_STOPS = [
    {"lat": 28.6289, "lon": 77.2065, "address": "Connaught Place, Delhi", "cod": 5000},
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

DELHI_VEHICLES = [
    {"plate": "DL01AB1234", "capacity": 100, "cod_limit": 50000},
    {"plate": "DL02CD5678", "capacity": 200, "cod_limit": 50000},
    {"plate": "DL03EF9012", "capacity": 100, "cod_limit": 50000},
]

# Hub 2: Mumbai
MUMBAI_STOPS = [
    {"lat": 19.0760, "lon": 72.8777, "address": "Mumbai CST", "cod": 8000},
    {"lat": 19.1136, "lon": 72.8697, "address": "Andheri East", "cod": 15000},
    {"lat": 18.9220, "lon": 72.8347, "address": "BKC Bandra", "cod": 20000},
    {"lat": 19.0176, "lon": 72.8561, "address": "Lower Parel", "cod": 12000},
    {"lat": 19.2183, "lon": 72.9781, "address": "Thane", "cod": 10000},
    {"lat": 19.1197, "lon": 72.9064, "address": "Powai", "cod": 9000},
    {"lat": 18.9894, "lon": 72.8355, "address": "Worli", "cod": 11000},
    {"lat": 19.0330, "lon": 72.8569, "address": "Mahalaxmi", "cod": 6000},
    {"lat": 19.0896, "lon": 72.8656, "address": "Santacruz", "cod": 7000},
    {"lat": 19.0728, "lon": 72.8826, "address": "Dadar", "cod": 5000},
]

MUMBAI_VEHICLES = [
    {"plate": "MH01AB1234", "capacity": 150, "cod_limit": 50000},
    {"plate": "MH02CD5678", "capacity": 200, "cod_limit": 50000},
    {"plate": "MH03EF9012", "capacity": 100, "cod_limit": 50000},
]

# Hub 3: Bangalore
BANGALORE_STOPS = [
    {"lat": 12.9716, "lon": 77.5946, "address": "MG Road, Bangalore", "cod": 9000},
    {"lat": 12.9352, "lon": 77.6245, "address": "Koramangala", "cod": 14000},
    {"lat": 13.0358, "lon": 77.5970, "address": "Indiranagar", "cod": 12000},
    {"lat": 12.9698, "lon": 77.7500, "address": "Whitefield", "cod": 18000},
    {"lat": 12.9279, "lon": 77.6271, "address": "BTM Layout", "cod": 8000},
    {"lat": 13.0117, "lon": 77.5498, "address": "Yeshwanthpur", "cod": 10000},
    {"lat": 12.9698, "lon": 77.6480, "address": "HSR Layout", "cod": 11000},
    {"lat": 12.9141, "lon": 77.6411, "address": "Jayanagar", "cod": 7000},
    {"lat": 13.0475, "lon": 77.5871, "address": "Hebbal", "cod": 13000},
    {"lat": 12.9591, "lon": 77.6412, "address": "Marathahalli", "cod": 9500},
]

BANGALORE_VEHICLES = [
    {"plate": "KA01AB1234", "capacity": 120, "cod_limit": 50000},
    {"plate": "KA02CD5678", "capacity": 180, "cod_limit": 50000},
    {"plate": "KA03EF9012", "capacity": 150, "cod_limit": 50000},
]


async def seed_hub(session, hub_id, stops, vehicles, hub_name):
    """Seed a single hub with stops and vehicles"""
    try:
        # Insert vehicles
        for v in vehicles:
            await session.execute(
                text("""INSERT INTO vehicles (plate_number, capacity, cod_limit, is_active, hub_id)
                   VALUES (:plate, :capacity, :cod_limit, true, :hub_id)
                   ON CONFLICT (plate_number) DO NOTHING"""),
                {"plate": v["plate"], "capacity": v["capacity"], "cod_limit": v["cod_limit"], "hub_id": hub_id}
            )
        
        # Insert stops
        for s in stops:
            tw_start = datetime.now() + timedelta(hours=1)
            tw_end = datetime.now() + timedelta(hours=8)
            
            await session.execute(
                text("""INSERT INTO stops (address, lat, lon, cod_amount, time_window_start, 
                                      time_window_end, is_completed, hub_id)
                   VALUES (:address, :lat, :lon, :cod, :tw_start, :tw_end, false, :hub_id)"""),
                {
                    "address": s["address"], 
                    "lat": s["lat"], 
                    "lon": s["lon"], 
                    "cod": s["cod"],
                    "tw_start": tw_start,
                    "tw_end": tw_end,
                    "hub_id": hub_id
                }
            )
        
        print(f"✅ {hub_name}: {len(vehicles)} vehicles, {len(stops)} stops")
        
    except Exception as e:
        print(f"❌ Error seeding {hub_name}: {e}")
        raise


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Clear existing data
            print("🗑️  Clearing existing data...")
            await session.execute(text("DELETE FROM stops"))
            await session.execute(text("DELETE FROM vehicles"))
            await session.commit()
            
            print("📍 Seeding all hubs...")
            
            # Seed Hub 1: Delhi
            await seed_hub(session, 1, DELHI_STOPS, DELHI_VEHICLES, "Hub 1 - Delhi NCR")
            
            # Seed Hub 2: Mumbai
            await seed_hub(session, 2, MUMBAI_STOPS, MUMBAI_VEHICLES, "Hub 2 - Mumbai")
            
            # Seed Hub 3: Bangalore
            await seed_hub(session, 3, BANGALORE_STOPS, BANGALORE_VEHICLES, "Hub 3 - Bangalore")
            
            await session.commit()
            
            print("\n🎉 All hubs seeded successfully!")
            print(f"   Total: {len(DELHI_VEHICLES) + len(MUMBAI_VEHICLES) + len(BANGALORE_VEHICLES)} vehicles")
            print(f"   Total: {len(DELHI_STOPS) + len(MUMBAI_STOPS) + len(BANGALORE_STOPS)} stops")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
