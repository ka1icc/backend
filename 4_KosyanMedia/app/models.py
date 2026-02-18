"""SQLAlchemy ORM models for Via.com flight data."""

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


class XmlResponse(Base):
    """Parsed XML response from Via.com API."""

    __tablename__ = 'xml_responses'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    request_time = Column(String, default='')
    response_time = Column(String, default='')

    routes = relationship(
        'Route',
        back_populates='xml_response',
        cascade='all, delete-orphan',
    )


class Route(Base):
    """Single itinerary (Flights block) from an API response."""

    __tablename__ = 'routes'

    id = Column(Integer, primary_key=True)
    xml_response_id = Column(
        Integer,
        ForeignKey('xml_responses.id'),
    )
    route_index = Column(Integer, default=0)
    is_round_trip = Column(Boolean, default=False)
    currency = Column(String, default='')
    total_adult = Column(Float, nullable=True)

    xml_response = relationship(
        'XmlResponse',
        back_populates='routes',
    )
    segments = relationship(
        'FlightSegment',
        back_populates='route',
        cascade='all, delete-orphan',
        order_by='FlightSegment.segment_order',
    )


class FlightSegment(Base):
    """One flight leg within a route."""

    __tablename__ = 'flight_segments'

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    direction = Column(String, default='onward')
    segment_order = Column(Integer, default=0)
    carrier_id = Column(String, default='')
    carrier_name = Column(String, default='')
    flight_number = Column(String, default='')
    source = Column(String, default='')
    destination = Column(String, default='')
    departure_ts = Column(String, default='')
    arrival_ts = Column(String, default='')
    class_code = Column(String, default='')
    ticket_type = Column(String, default='')

    route = relationship('Route', back_populates='segments')
