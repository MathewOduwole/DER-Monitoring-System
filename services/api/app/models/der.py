from datetime import datetime, timezone

from app.extensions import db


class DER(db.Model):
    """Distributed Energy Resource entity."""

    __tablename__ = "ders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    mrid_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    telemetry = db.relationship(
        "TelemetryData",
        backref="der",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mrid_id": self.mrid_id,
            "location": self.location,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<DER {self.name}>"
