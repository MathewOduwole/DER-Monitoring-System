import json
import logging

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    """Wrapper around confluent-kafka Producer for publishing telemetry events."""

    def __init__(self, bootstrap_servers: str):
        self._config = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "der-api-producer",
            "acks": "all",
        }
        self._producer = None

    def _ensure_producer(self):
        if self._producer is None:
            self._producer = Producer(self._config)
            logger.info("Kafka producer initialised: %s", self._config["bootstrap.servers"])

    def _delivery_callback(self, err, msg):
        if err:
            logger.error("Kafka delivery failed: %s", err)
        else:
            logger.debug(
                "Kafka message delivered to %s [%d] @ %d",
                msg.topic(), msg.partition(), msg.offset(),
            )

    def publish(self, topic: str, key: str, value: dict):
        self._ensure_producer()
        self._producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(value).encode("utf-8"),
            callback=self._delivery_callback,
        )
        self._producer.poll(0)

    def flush(self, timeout: float = 5.0):
        if self._producer:
            self._producer.flush(timeout)

    def close(self):
        self.flush()
        self._producer = None
        logger.info("Kafka producer closed.")
