import logging

from app.consumer import TelemetryConsumer


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    consumer = TelemetryConsumer()
    consumer.start()


if __name__ == "__main__":
    main()
