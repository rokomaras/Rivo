from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    ENV: str = "dev"
    DATABASE_URL: str

    # Override JWT_SECRET with a strong random value in production via .env
    JWT_SECRET: str = "changeme-replace-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    JWT_REFRESH_SECRET: str = "changeme-refresh-secret-in-production"
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    JWT_ISSUER: str = "rivo-api"


settings = Settings()