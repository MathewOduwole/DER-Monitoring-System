import json
import logging
import signal
import sys

from confluent_kafka import Consumer, KafkaError

from app.config import TelemetryConfig
from app.processor import TelemetryProcessor

logger = logging.getLogger(__name__)


class TelemetryConsumer:
    """Kafka consumer that processes DER telemetry events.

    I'm running this as a standalone service (separate from the API) so that
    event processing scales independently and doesn't block HTTP request handling.
    """

    def __init__(self):
        self._config = {
            "bootstrap.servers": TelemetryConfig.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": TelemetryConfig.KAFKA_GROUP_ID,
            "auto.offset.reset": TelemetryConfig.KAFKA_AUTO_OFFSET_RESET,
            "enable.auto.commit": True,
        }
        self._topic = TelemetryConfig.KAFKA_TOPIC
        self._consumer = None
        self._processor = TelemetryProcessor()
        self._running = False

    def start(self):
        self._consumer = Consumer(self._config)
        self._consumer.subscribe([self._topic])
        self._running = True

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        logger.info(
            "Telemetry consumer started - topic: %s, group: %s",
            self._topic, TelemetryConfig.KAFKA_GROUP_ID,
        )

        self._poll_loop()

    def _poll_loop(self):
        while self._running:
            msg = self._consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Consumer error: %s", msg.error())
                continue

            try:
                event = json.loads(msg.value().decode("utf-8"))
                self._processor.process(event)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in message: %s", msg.value())
            except Exception:
                logger.exception("Unexpected error processing message")

    def _shutdown(self, signum, frame):
        logger.info("Shutting down telemetry consumer (signal %d)...", signum)
        self._running = False
        if self._consumer:
            self._consumer.close()
        sys.exit(0)
