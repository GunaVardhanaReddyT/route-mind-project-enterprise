from fastapi import FastAPI
from app.api.v1 import optimizer, routes, metrics, hubs, live
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# CRITICAL: Import all models before creating tables
from app.models import vehicle, stop, route

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Core routing endpoints
app.include_router(live.router, prefix=f"{settings.API_V1_PREFIX}", tags=["live"])
app.include_router(optimizer.router, prefix=f"{settings.API_V1_PREFIX}/optimizer", tags=["optimizer"])
app.include_router(routes.router, prefix=f"{settings.API_V1_PREFIX}/routes", tags=["routes"])
app.include_router(metrics.router, prefix=f"{settings.API_V1_PREFIX}", tags=["metrics"])
app.include_router(hubs.router, prefix=f"{settings.API_V1_PREFIX}", tags=["hubs"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "routing"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "routing"}