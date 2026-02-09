"""Pydantic schemas for weather API responses."""
from pydantic import BaseModel, Field


class CurrentWeatherResponse(BaseModel):
    """Response for /weather/current."""

    temperature_c: float = Field(
        ..., description="Current temperature in Celsius"
    )
    observed_at_epoch: int = Field(
        ..., description="Observation time as Unix timestamp"
    )


class HourlyTemperature(BaseModel):
    """Single hourly temperature in historical data."""

    epoch_time: int
    temperature_c: float
    observed_at_iso: str | None = None


class HistoricalWeatherResponse(BaseModel):
    """Response for /weather/historical — hourly temps for last 24h."""

    hourly: list[HourlyTemperature] = Field(default_factory=list)


class AggregatedTempResponse(BaseModel):
    """Response for /weather/historical/max, min, avg."""

    value_c: float = Field(
        ..., description="Max, min, or average temperature in Celsius"
    )
    kind: str = Field(..., description="max, min, or avg")


class TemperatureByTimeResponse(BaseModel):
    """Response for /weather/by_time."""

    temperature_c: float
    epoch_time: int
    observed_at_iso: str | None = None
