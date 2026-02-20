from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError

from app.schemas.telemetry_schema import TelemetryEventSchema

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/api/telemetry")

event_schema = TelemetryEventSchema()


@telemetry_bp.route("", methods=["POST"])
def submit_telemetry():
    try:
        data = event_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    kafka_producer = current_app.config.get("KAFKA_PRODUCER")
    topic = current_app.config.get("KAFKA_TOPIC_TELEMETRY", "der-telemetry")

    if kafka_producer is None:
        return jsonify({"error": "Kafka producer not available."}), 503

    event_payload = {
        "der_name": data["der_name"],
        "active_power": data["active_power"],
        "reactive_power": data["reactive_power"],
        "voltage": data["voltage"],
        "timestamp": data["timestamp"].isoformat(),
    }

    kafka_producer.publish(
        topic=topic,
        key=data["der_name"],
        value=event_payload,
    )

    return jsonify({"message": "Telemetry event published."}), 202
