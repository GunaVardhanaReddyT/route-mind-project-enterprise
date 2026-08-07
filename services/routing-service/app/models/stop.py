from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.db.base import Base

class Stop(Base):
    __tablename__ = "stops"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    cod_amount = Column(Float, default=0.0)
    time_window_start = Column(DateTime, nullable=True)
    time_window_end = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    hub_id = Column(Integer, nullable=False)