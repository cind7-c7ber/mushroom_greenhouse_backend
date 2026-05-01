from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    IMAGE_BUCKET: str = "growth-images"

    # Database
    DATABASE_URL: str

    # HTTP telemetry source
    TELEMETRY_SOURCE_URL: str

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