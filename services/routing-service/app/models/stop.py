from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base

class Stop(Base):
    __tablename__ = "stops"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    cod_amount = Column(Float, default=0.0)
    time_window_start = Column(String, nullable=True)
    time_window_end = Column(String, nullable=True)
    priority = Column(String, default="medium")
    package_count = Column(Integer, default=1)
    total_weight_kg = Column(Float, default=10.0)
    zone = Column(String, default="unknown")
    is_completed = Column(Boolean, default=False)
    hub_id = Column(Integer, nullable=False)
