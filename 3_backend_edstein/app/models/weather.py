"""Weather persistence model."""
from datetime import datetime

from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WeatherRecord(Base):
    """Stored temperature observation for caching and by_time lookup."""

    __tablename__ = "weather_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    epoch_time: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    weather_text: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
