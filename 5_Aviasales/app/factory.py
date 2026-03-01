"""Flask application factory."""

import logging

from flask import Flask

from app.config import Config
from app.extensions import db
from app.models import FlightResult
from app.routes.flights import flights_bp
from app.services.xml_parser import load_xml_into_db

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    application = Flask(__name__)
    application.config.from_object(Config)
    application.json.sort_keys = False
    application.json.compact = False

    db.init_app(application)

    with application.app_context():
        db.create_all()

    application.register_blueprint(flights_bp, url_prefix='/api')

    _load_initial_data(application)

    return application


def _load_initial_data(application: Flask) -> None:
    """Load XML data into the database on first startup."""
    with application.app_context():
        existing = FlightResult.query.count()
        if existing == 0:
            data_dir = application.config['XML_DATA_DIR']
            count = load_xml_into_db(data_dir)
            logger.info('Loaded %d flight options into DB', count)
