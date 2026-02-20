from datetime import datetime, timezone

from app.extensions import db


class TelemetryData(db.Model):
    """Time-series telemetry data for a DER."""

    __tablename__ = "telemetry_data"

    id = db.Column(db.Integer, primary_key=True)
    der_id = db.Column(
        db.Integer,
        db.ForeignKey("ders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    active_power = db.Column(db.Float, nullable=False)
    reactive_power = db.Column(db.Float, nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.Index("idx_telemetry_der_timestamp", "der_id", timestamp.desc()),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "der_id": self.der_id,
            "active_power": self.active_power,
            "reactive_power": self.reactive_power,
            "voltage": self.voltage,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self):
        return f"<TelemetryData der_id={self.der_id} ts={self.timestamp}>"
