import os


class TelemetryConfig:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://der_user:der_password@localhost:5432/der_monitoring"
    )
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_TELEMETRY", "der-telemetry")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "der-telemetry-consumer")
    KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
