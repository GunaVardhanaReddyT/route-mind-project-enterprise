from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import explain

app = FastAPI(title="RouteMind AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(explain.router, prefix="/api/v1", tags=["explain"])

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai"}

@app.get("/api/v1/status")
async def status():
    return {
        "service": "ai",
        "version": settings.VERSION,
        "bedrock_region": settings.AWS_REGION
    }