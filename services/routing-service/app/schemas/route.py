from sqlalchemy import Column, Integer, ForeignKey, String
from app.db.base import Base

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    status = Column(String, default="planned") # planned, active, completed
    hub_id = Column(Integer, nullable=False)

class RouteStop(Base):
    __tablename__ = "route_stops"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    sequence = Column(Integer, nullable=False)