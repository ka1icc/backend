"""
Weather cache service: in-memory TTL cache + DB persistence.
Reduces load on AccuWeather API (target ~5 RPS).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from cachetools import TTLCache
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.weather import WeatherRecord
from app.services.accuweather import AccuWeatherClient


class WeatherCacheService:
    """Fetches weather from AccuWeather, caches in memory and DB."""

    def __init__(self):
        self._client = AccuWeatherClient()
        self._current_cache: TTLCache[str, dict[str, Any]] = TTLCache(
            maxsize=10,
            ttl=settings.current_weather_cache_ttl,
        )
        self._historical_cache: TTLCache[str, list[dict[str, Any]]] = (
            TTLCache(
                maxsize=10,
                ttl=settings.historical_weather_cache_ttl,
            )
        )

    def _cache_key(self) -> str:
        return settings.location_key or "default"

    async def get_current(self, db: AsyncSession) -> dict[str, Any] | None:
        """Current temperature. Uses cache, then API; fallback to latest from 24h."""
        key = self._cache_key()
        if key in self._current_cache:
            return self._current_cache[key]
        data = await self._client.get_current_conditions()
        if data:
            temp_c = AccuWeatherClient.parse_temperature_c(data)
            epoch_time = AccuWeatherClient.parse_epoch_time(data)
            local_dt = AccuWeatherClient.parse_local_observation_datetime(data)
            out = {
                "temperature_c": temp_c,
                "observed_at_epoch": epoch_time,
                "observed_at_iso": local_dt,
            }
            self._current_cache[key] = out
            try:
                if temp_c is not None and epoch_time is not None:
                    record = WeatherRecord(
                        location_key=settings.location_key,
                        epoch_time=epoch_time,
                        observed_at=datetime.fromtimestamp(
                            epoch_time, tz=timezone.utc
                        ),
                        temperature_c=temp_c,
                        weather_text=data.get("WeatherText"),
                        created_at=datetime.now(timezone.utc),
                    )
                    db.add(record)
                    await db.flush()
            except Exception:
                pass
            return out
        # Fallback: use the most recent observation from historical 24h
        hist = await self.get_historical_24h(db)
        if not hist:
            return None
        # Sort by epoch_time descending, take latest
        latest = max(hist, key=lambda h: h["epoch_time"])
        out = {
            "temperature_c": latest["temperature_c"],
            "observed_at_epoch": latest["epoch_time"],
            "observed_at_iso": latest.get("observed_at_iso"),
        }
        self._current_cache[key] = out
        return out

    async def get_historical_24h(
        self, db: AsyncSession
    ) -> list[dict[str, Any]]:
        """Hourly temperature for last 24h. Uses cache, then API; persists to DB."""
        key = self._cache_key()
        if key in self._historical_cache:
            return self._historical_cache[key]
        raw = await self._client.get_historical_24h()
        result: list[dict[str, Any]] = []
        now_utc = datetime.now(timezone.utc)
        for item in raw:
            temp_c = AccuWeatherClient.parse_temperature_c(item)
            epoch_time = AccuWeatherClient.parse_epoch_time(item)
            local_dt = AccuWeatherClient.parse_local_observation_datetime(item)
            if temp_c is not None and epoch_time is not None:
                result.append({
                    "epoch_time": epoch_time,
                    "temperature_c": temp_c,
                    "observed_at_iso": local_dt,
                })
        try:
            for item in raw:
                temp_c = AccuWeatherClient.parse_temperature_c(item)
                epoch_time = AccuWeatherClient.parse_epoch_time(item)
                if temp_c is not None and epoch_time is not None:
                    rec = WeatherRecord(
                        location_key=settings.location_key,
                        epoch_time=epoch_time,
                        observed_at=datetime.fromtimestamp(
                            epoch_time, tz=timezone.utc
                        ),
                        temperature_c=temp_c,
                        weather_text=item.get("WeatherText"),
                        created_at=now_utc,
                    )
                    db.add(rec)
            await db.flush()
        except Exception:
            pass
        self._historical_cache[key] = result
        return result

    async def get_historical_max(self, db: AsyncSession) -> float | None:
        """Max temperature over last 24h."""
        hist = await self.get_historical_24h(db)
        if not hist:
            return None
        vals = [h["temperature_c"] for h in hist]
        return max(vals)

    async def get_historical_min(self, db: AsyncSession) -> float | None:
        """Min temperature over last 24h."""
        hist = await self.get_historical_24h(db)
        if not hist:
            return None
        vals = [h["temperature_c"] for h in hist]
        return min(vals)

    async def get_historical_avg(self, db: AsyncSession) -> float | None:
        """Average temperature over last 24h."""
        hist = await self.get_historical_24h(db)
        if not hist:
            return None
        vals = [h["temperature_c"] for h in hist]
        return sum(vals) / len(vals)

    async def get_by_time(
        self,
        db: AsyncSession,
        epoch_time: int,
    ) -> dict[str, Any] | None:
        """
        Find temperature closest to the given Unix timestamp.
        From stored data; None if no data (caller returns 404).
        """
        stmt = (
            select(WeatherRecord)
            .where(
                WeatherRecord.location_key == settings.location_key,
            )
            .order_by(func.abs(WeatherRecord.epoch_time - epoch_time))
            .limit(1)
        )
        r = await db.execute(stmt)
        row = r.scalar_one_or_none()
        if row is None:
            return None
        obs_iso = row.observed_at.isoformat() if row.observed_at else None
        return {
            "temperature_c": row.temperature_c,
            "epoch_time": row.epoch_time,
            "observed_at_iso": obs_iso,
        }
