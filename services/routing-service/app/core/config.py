from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "RouteMind Routing"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    REDIS_URL: str
    AWS_REGION: str = "us-east-2"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Bedrock Model Config (Optional - has defaults)
    BEDROCK_MODEL_ID: str = "moonshotai.kimi-k2.5"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()