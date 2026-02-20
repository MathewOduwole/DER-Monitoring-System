import logging
from datetime import datetime

from sqlalchemy import text

from app.db import get_session

logger = logging.getLogger(__name__)

# I'm defining sensible validation ranges for each telemetry attribute.
# These guard against corrupt or nonsensical readings before they reach the database.
VALID_RANGES = {
    "active_power": (-10000.0, 10000.0),
    "reactive_power": (-10000.0, 10000.0),
    "voltage": (0.0, 500.0),
}


class TelemetryProcessor:
    """Validates and stores incoming telemetry events."""

    def process(self, event: dict) -> bool:
        if not self._validate(event):
            return False

        return self._store(event)

    def _validate(self, event: dict) -> bool:
        required_fields = ["der_name", "active_power", "reactive_power", "voltage", "timestamp"]
        for field in required_fields:
            if field not in event:
                logger.warning("Missing required field: %s", field)
                return False

        for field, (low, high) in VALID_RANGES.items():
            value = event.get(field)
            if not isinstance(value, (int, float)):
                logger.warning("Invalid type for %s: %s", field, type(value).__name__)
                return False
            if not (low <= value <= high):
                logger.warning(
                    "Value out of range for %s: %.2f (expected %.2f to %.2f)",
                    field, value, low, high,
                )
                return False

        return True

    def _store(self, event: dict) -> bool:
        session = get_session()
        try:
            result = session.execute(
                text("SELECT id FROM ders WHERE name = :name"),
                {"name": event["der_name"]},
            )
            row = result.fetchone()
            if row is None:
                logger.warning("DER not found: %s", event["der_name"])
                return False

            der_id = row[0]
            timestamp = event["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            session.execute(
                text(
                    "INSERT INTO telemetry_data (der_id, active_power, reactive_power, voltage, timestamp) "
                    "VALUES (:der_id, :active_power, :reactive_power, :voltage, :timestamp)"
                ),
                {
                    "der_id": der_id,
                    "active_power": event["active_power"],
                    "reactive_power": event["reactive_power"],
                    "voltage": event["voltage"],
                    "timestamp": timestamp,
                },
            )
            session.commit()
            logger.debug("Telemetry stored for DER %s", event["der_name"])
            return True
        except Exception:
            session.rollback()
            logger.exception("Failed to store telemetry for DER %s", event["der_name"])
            return False
        finally:
            session.close()
