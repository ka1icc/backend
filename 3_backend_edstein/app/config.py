"""Application configuration."""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/weather_db"
    )

    # AccuWeather API (https://developer.accuweather.com/apis)
    accuweather_api_key: str = ""
    accuweather_base_url: str = "https://dataservice.accuweather.com"
    location_key: str = "295954"  # Kazan (Казань), hardcoded

    # Cache TTL (seconds) — reduce load on AccuWeather, target ~5 RPS
    current_weather_cache_ttl: int = 300
    historical_weather_cache_ttl: int = 600

    accuweather_request_timeout: float = 5.0


settings = Settings()
