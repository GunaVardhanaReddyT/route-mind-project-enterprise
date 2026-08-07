from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import explain
from app.core.config import settings

app = FastAPI(title="RouteMind AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(explain.router, prefix=f"{settings.API_V1_PREFIX}/explain", tags=["explanation"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai"}