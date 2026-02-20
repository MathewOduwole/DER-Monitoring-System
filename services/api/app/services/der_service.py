import logging

from app.extensions import db
from app.models.der import DER

logger = logging.getLogger(__name__)


class DERService:
    """Business logic for DER management."""

    @staticmethod
    def create(data: dict) -> DER:
        der = DER(
            name=data["name"],
            mrid_id=data["mrid_id"],
            location=data.get("location"),
            type=data["type"],
        )
        db.session.add(der)
        db.session.commit()
        logger.info("DER created: %s", der.name)
        return der

    @staticmethod
    def get_by_name(name: str) -> DER | None:
        return DER.query.filter_by(name=name).first()

    @staticmethod
    def get_all() -> list[DER]:
        return DER.query.order_by(DER.created_at.desc()).all()

    @staticmethod
    def update(der: DER, data: dict) -> DER:
        for key, value in data.items():
            if hasattr(der, key):
                setattr(der, key, value)
        db.session.commit()
        logger.info("DER updated: %s", der.name)
        return der

    @staticmethod
    def delete(der: DER) -> None:
        name = der.name
        db.session.delete(der)
        db.session.commit()
        logger.info("DER deleted: %s", name)
