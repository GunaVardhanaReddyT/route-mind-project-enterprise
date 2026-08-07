from sqlalchemy import Column, Integer, String, Boolean, Float
from app.db.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, default=100)
    cod_limit = Column(Float, default=50000.0)
    is_active = Column(Boolean, default=True)
    hub_id = Column(Integer, nullable=False)