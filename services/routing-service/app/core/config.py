from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RouteMind Routing"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    REDIS_URL: str
    AWS_REGION: str = "ap-south-1"

    # Security (To verify JWT from Auth Service)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()