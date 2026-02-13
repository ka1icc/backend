"""ORM models for flight search results."""

from app.extensions import db


class FlightResult(db.Model):
    """Single flight itinerary option from a partner XML response."""

    __tablename__ = 'flight_results'

    id = db.Column(db.Integer, primary_key=True)
    source_file = db.Column(db.String(50), nullable=False, index=True)
    is_round_trip = db.Column(db.Boolean, nullable=False, default=False)

    price = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(5), nullable=False, default='SGD')
    duration_minutes = db.Column(db.Integer, nullable=False)
    route_key = db.Column(db.String(512), nullable=False, index=True)

    onward_segments = db.Column(db.JSON, nullable=False)
    return_segments = db.Column(db.JSON, nullable=True, default=list)

    def to_dict(self):
        """Serialize to a JSON-friendly dictionary."""
        return {
            'id': self.id,
            'source_file': self.source_file,
            'is_round_trip': self.is_round_trip,
            'price': float(self.price),
            'currency': self.currency,
            'duration_minutes': self.duration_minutes,
            'route_key': self.route_key,
            'onward_segments': self.onward_segments,
            'return_segments': self.return_segments or [],
        }
