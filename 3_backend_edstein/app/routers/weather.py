"""Weather API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.weather import (
    AggregatedTempResponse,
    CurrentWeatherResponse,
    HistoricalWeatherResponse,
    HourlyTemperature,
    TemperatureByTimeResponse,
)
from app.services.weather_cache import WeatherCacheService

router = APIRouter(prefix="/weather", tags=["weather"])
_service = WeatherCacheService()


@router.get("/current", response_model=CurrentWeatherResponse)
async def weather_current(db: AsyncSession = Depends(get_db)):
    """Текущая температура."""
    try:
        data = await _service.get_current(db)
    except Exception:
        raise HTTPException(
            status_code=503, detail="Weather data unavailable"
        )
    if (
        not data
        or data.get("temperature_c") is None
        or data.get("observed_at_epoch") is None
    ):
        raise HTTPException(
            status_code=503, detail="Weather data unavailable"
        )
    return CurrentWeatherResponse(
        temperature_c=data["temperature_c"],
        observed_at_epoch=data["observed_at_epoch"],
    )


# Более специфичные маршруты — первыми, иначе /historical может перехватывать /historical/max
@router.get("/historical/max", response_model=AggregatedTempResponse)
async def weather_historical_max(db: AsyncSession = Depends(get_db)):
    """Максимальная температура за 24 часа."""
    v = await _service.get_historical_max(db)
    if v is None:
        raise HTTPException(
            status_code=503, detail="Historical data unavailable"
        )
    return AggregatedTempResponse(value_c=v, kind="max")


@router.get("/historical/min", response_model=AggregatedTempResponse)
async def weather_historical_min(db: AsyncSession = Depends(get_db)):
    """Минимальная температура за 24 часа."""
    v = await _service.get_historical_min(db)
    if v is None:
        raise HTTPException(
            status_code=503, detail="Historical data unavailable"
        )
    return AggregatedTempResponse(value_c=v, kind="min")


@router.get("/historical/avg", response_model=AggregatedTempResponse)
async def weather_historical_avg(db: AsyncSession = Depends(get_db)):
    """Средняя температура за 24 часа."""
    v = await _service.get_historical_avg(db)
    if v is None:
        raise HTTPException(
            status_code=503, detail="Historical data unavailable"
        )
    return AggregatedTempResponse(value_c=v, kind="avg")


@router.get("/historical", response_model=HistoricalWeatherResponse)
async def weather_historical(db: AsyncSession = Depends(get_db)):
    """Почасовая температура за последние 24 часа."""
    hourly = await _service.get_historical_24h(db)
    items = [
        HourlyTemperature(
            epoch_time=h["epoch_time"],
            temperature_c=h["temperature_c"],
            observed_at_iso=h.get("observed_at_iso"),
        )
        for h in hourly
    ]
    return HistoricalWeatherResponse(hourly=items)


@router.get("/by_time", response_model=TemperatureByTimeResponse)
async def weather_by_time(
    timestamp: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Найти температуру ближайшую к переданному timestamp.
    Например 1621823790 — температура за 2021-05-24 08:00.
    Из имеющихся данных; если такого времени нет — 404.
    """
    data = await _service.get_by_time(db, epoch_time=timestamp)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="No temperature for this timestamp",
        )
    return TemperatureByTimeResponse(
        temperature_c=data["temperature_c"],
        epoch_time=data["epoch_time"],
        observed_at_iso=data.get("observed_at_iso"),
    )
