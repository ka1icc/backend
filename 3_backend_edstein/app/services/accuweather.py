"""
AccuWeather API client.
Docs: https://developer.accuweather.com/apis
Base API: https://dataservice.accuweather.com
"""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class AccuWeatherClient:
    """Client for AccuWeather Current Conditions API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        location_key: str | None = None,
        timeout: float | None = None,
    ):
        raw_base_url = (base_url or settings.accuweather_base_url).rstrip("/")
        # AccuWeather иногда отдаёт 301 редирект с http -> https.
        # Следуем редиректам и на всякий случай принудительно используем https
        # для dataservice.accuweather.com.
        if raw_base_url.startswith("http://dataservice.accuweather.com"):
            raw_base_url = raw_base_url.replace(
                "http://dataservice.accuweather.com",
                "https://dataservice.accuweather.com",
                1,
            )
        self.base_url = raw_base_url
        self.api_key = api_key or settings.accuweather_api_key
        self.location_key = location_key or settings.location_key
        self.timeout = timeout or settings.accuweather_request_timeout

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _params(self, **kwargs: Any) -> dict[str, Any]:
        params = {"apikey": self.api_key, **kwargs}
        return {k: v for k, v in params.items() if v is not None}

    async def get_current_conditions(self) -> dict[str, Any] | None:
        """
        GET /currentconditions/v1/{locationKey}
        Returns current conditions for the location.
        """
        if not self.api_key:
            return None
        url = self._url(f"currentconditions/v1/{self.location_key}")
        params = self._params()
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            if isinstance(data, list) and data:
                return data[0]
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    async def get_historical_24h(self) -> list[dict[str, Any]]:
        """
        GET /currentconditions/v1/{locationKey}/historical/24
        Returns hourly conditions for the last 24 hours.
        """
        if not self.api_key:
            return []
        url = self._url(
            f"currentconditions/v1/{self.location_key}/historical/24"
        )
        params = self._params()
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def parse_temperature_c(record: dict[str, Any]) -> float | None:
        """Extract temperature in Celsius from API response item."""
        try:
            t = record.get("Temperature") or {}
            m = t.get("Metric") or {}
            v = m.get("Value")
            return float(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def parse_epoch_time(record: dict[str, Any]) -> int | None:
        """Extract EpochTime from API response item."""
        try:
            v = record.get("EpochTime")
            return int(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def parse_local_observation_datetime(record: dict[str, Any]) -> str | None:
        """Extract LocalObservationDateTime from API response item."""
        return record.get("LocalObservationDateTime")
