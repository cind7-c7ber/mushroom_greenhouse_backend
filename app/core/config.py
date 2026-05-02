from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    IMAGE_BUCKET: str = "greenhouse-images"

    # Database
    DATABASE_URL: str

    # HTTP telemetry source
    TELEMETRY_SOURCE_URL: str

    # Polling
    POLLING_ENABLED: bool = False
    POLLING_INTERVAL_SECONDS: int = 30

    # JWT Token authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Cloud Deployment
    BACKEND_ENV: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"
    ENABLE_DOCS: bool = True

    # MQTT (legacy / transition only)
    ENABLE_MQTT: bool = False
    MQTT_BROKER: str | None = None
    MQTT_PORT: int = 1883
    MQTT_KEEPALIVE: int = 60
    MQTT_TOPICS: list[str] = ["acity_greenhouse/paakwasi/data"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()