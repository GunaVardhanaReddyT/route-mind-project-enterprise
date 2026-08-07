from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.route import Route
from app.schemas.route import RouteResponse
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=List[RouteResponse])
async def get_routes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Route))
    routes = result.scalars().all()
    return routes