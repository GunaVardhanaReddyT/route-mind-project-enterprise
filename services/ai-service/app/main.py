from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="RouteMind AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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