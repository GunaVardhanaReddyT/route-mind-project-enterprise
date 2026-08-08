import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.vehicle import Vehicle
from app.models.stop import Stop
from app.core.config import settings

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Vehicles
        vehicles = [
            Vehicle(plate_number="DL-01-AB-1234", capacity=500, hub_id=1, is_active=True),
            Vehicle(plate_number="DL-01-CD-5678", capacity=500, hub_id=1, is_active=True),
            Vehicle(plate_number="DL-01-EF-9012", capacity=500, hub_id=1, is_active=True)
        ]
        
        # Stops
        stops = [
            Stop(address="Connaught Place, Delhi", lat=28.6315, lon=77.2167, 
                 time_window_start="09:00", time_window_end="13:00", priority="high",
                 package_count=5, total_weight_kg=25.0, zone="central", hub_id=1, is_completed=False),
            Stop(address="Karol Bagh, Delhi", lat=28.6519, lon=77.1900,
                 time_window_start="10:00", time_window_end="14:00", priority="medium",
                 package_count=3, total_weight_kg=15.0, zone="west", hub_id=1, is_completed=False),
            Stop(address="Lajpat Nagar, Delhi", lat=28.5677, lon=77.2431,
                 time_window_start="09:00", time_window_end="12:00", priority="high",
                 package_count=4, total_weight_kg=20.0, zone="south", hub_id=1, is_completed=False),
            Stop(address="Rohini, Delhi", lat=28.7499, lon=77.0687,
                 time_window_start="11:00", time_window_end="15:00", priority="low",
                 package_count=2, total_weight_kg=10.0, zone="north", hub_id=1, is_completed=False),
            Stop(address="Dwarka, Delhi", lat=28.5921, lon=77.0460,
                 time_window_start="09:30", time_window_end="13:30", priority="medium",
                 package_count=4, total_weight_kg=18.0, zone="west", hub_id=1, is_completed=False),
            Stop(address="Vasant Kunj, Delhi", lat=28.5244, lon=77.1586,
                 time_window_start="10:00", time_window_end="14:00", priority="medium",
                 package_count=3, total_weight_kg=14.0, zone="south", hub_id=1, is_completed=False),
            Stop(address="Saket, Delhi", lat=28.5244, lon=77.2066,
                 time_window_start="11:00", time_window_end="15:00", priority="low",
                 package_count=2, total_weight_kg=12.0, zone="south", hub_id=1, is_completed=False),
            Stop(address="Noida Sector 18", lat=28.5706, lon=77.3272,
                 time_window_start="09:00", time_window_end="13:00", priority="high",
                 package_count=5, total_weight_kg=22.0, zone="east", hub_id=1, is_completed=False)
        ]
        
        session.add_all(vehicles)
        session.add_all(stops)
        await session.commit()
        print("✅ Seeded 3 vehicles and 8 stops")

if __name__ == "__main__":
    asyncio.run(seed())
