from fastapi import FastAPI
from app.api.v1 import optimizer
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import routes
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

app.include_router(optimizer.router, prefix=f"{settings.API_V1_PREFIX}/optimizer", tags=["optimizer"])
app.include_router(routes.router, prefix=f"{settings.API_V1_PREFIX}/routes", tags=["routes"])

# Metrics for business impact demonstration
from app.api.v1 import metrics
app.include_router(metrics.router, prefix=f"{settings.API_V1_PREFIX}", tags=["metrics"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "routing"}