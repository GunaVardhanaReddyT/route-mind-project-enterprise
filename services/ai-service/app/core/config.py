from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RouteMind AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    AWS_REGION: str = "us-east-2"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    BEDROCK_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()