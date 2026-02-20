import logging

from flask import Flask
from flask_cors import CORS

from app.config import get_config
from app.extensions import db, ma
from app.kafka.producer import KafkaProducerClient
from app.routes.der_routes import der_bp
from app.routes.telemetry_routes import telemetry_bp
from app.routes.chart_routes import chart_bp
from app.routes.health_routes import health_bp


def create_app(config_override=None) -> Flask:
    app = Flask(__name__)

    config = config_override or get_config()
    app.config.from_object(config)

    _configure_logging(app)

    CORS(app)
    db.init_app(app)
    ma.init_app(app)

    _init_kafka(app)
    _register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app


def _configure_logging(app: Flask):
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _init_kafka(app: Flask):
    if app.config.get("TESTING"):
        app.config["KAFKA_PRODUCER"] = None
        return

    try:
        producer = KafkaProducerClient(app.config["KAFKA_BOOTSTRAP_SERVERS"])
        app.config["KAFKA_PRODUCER"] = producer
    except Exception as exc:
        logging.getLogger(__name__).warning("Kafka producer init failed: %s", exc)
        app.config["KAFKA_PRODUCER"] = None


def _register_blueprints(app: Flask):
    app.register_blueprint(health_bp)
    app.register_blueprint(der_bp)
    app.register_blueprint(telemetry_bp)
    app.register_blueprint(chart_bp)
