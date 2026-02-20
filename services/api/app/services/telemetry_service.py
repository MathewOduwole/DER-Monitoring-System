import logging
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.telemetry import TelemetryData
from app.models.der import DER

logger = logging.getLogger(__name__)

MAX_QUERY_DAYS = 14


class TelemetryService:
    """Business logic for telemetry data operations."""

    @staticmethod
    def get_time_series(der_name: str, start: datetime = None, end: datetime = None) -> list[dict]:
        der = DER.query.filter_by(name=der_name).first()
        if der is None:
            return None

        if end is None:
            end = datetime.now(timezone.utc)
        if start is None:
            start = end - timedelta(days=MAX_QUERY_DAYS)

        date_range = end - start
        if date_range > timedelta(days=MAX_QUERY_DAYS):
            start = end - timedelta(days=MAX_QUERY_DAYS)

        records = (
            TelemetryData.query
            .filter(
                TelemetryData.der_id == der.id,
                TelemetryData.timestamp >= start,
                TelemetryData.timestamp <= end,
            )
            .order_by(TelemetryData.timestamp.asc())
            .all()
        )
        return [r.to_dict() for r in records]

    @staticmethod
    def store(der_id: int, data: dict) -> TelemetryData:
        record = TelemetryData(
            der_id=der_id,
            active_power=data["active_power"],
            reactive_power=data["reactive_power"],
            voltage=data["voltage"],
            timestamp=data["timestamp"],
        )
        db.session.add(record)
        db.session.commit()
        return record
