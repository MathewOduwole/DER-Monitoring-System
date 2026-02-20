import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import TelemetryConfig

logger = logging.getLogger(__name__)

engine = create_engine(TelemetryConfig.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Session:
    return SessionLocal()
