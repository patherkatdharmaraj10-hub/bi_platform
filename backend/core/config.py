from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "BI Platform"
    APP_ENV: str = "development"
    SECRET_KEY: str = "bi-platform-secret-key-2024"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # PostgreSQL connection
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Fif1%40ar4myyy@localhost:5432/biplatform"

    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()