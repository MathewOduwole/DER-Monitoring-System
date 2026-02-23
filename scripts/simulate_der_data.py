"""
DER Telemetry Data Simulator

I wrote this script to generate realistic telemetry data for testing and demo
purposes. It registers a set of sample DERs (if they don't already exist) and
continuously publishes sinusoidal power/voltage readings with random noise,
simulating real-world sensor behaviour over time.

Usage:
    python simulate_der_data.py                        # defaults: 3 DERs, 5s interval
    python simulate_der_data.py --ders 5 --interval 2  # 5 DERs, every 2 seconds
    python simulate_der_data.py --backfill-hours 24     # seed 24h of historical data first
"""

import argparse
import logging
import math
import random
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://localhost:5001"

SAMPLE_DERS = [
    {"name": "Solar-Panel-01", "mrid_id": "SP-001", "location": "Building A Rooftop", "type": "solar"},
    {"name": "Solar-Panel-02", "mrid_id": "SP-002", "location": "Building C Rooftop", "type": "solar"},
    {"name": "Wind-Turbine-01", "mrid_id": "WT-001", "location": "North Field", "type": "wind"},
    {"name": "Battery-Storage-01", "mrid_id": "BS-001", "location": "Substation East", "type": "battery"},
    {"name": "Wind-Turbine-02", "mrid_id": "WT-002", "location": "South Ridge", "type": "wind"},
]


class DERSimulator:
    """Generates and publishes realistic DER telemetry readings."""

    def __init__(self, api_url: str, der_count: int = 3):
        self.api_url = api_url.rstrip("/")
        self.ders = SAMPLE_DERS[:der_count]
        self._start_time = time.time()

    def register_ders(self):
        """Register sample DERs, skipping any that already exist."""
        for der in self.ders:
            try:
                resp = requests.post(f"{self.api_url}/api/ders", json=der, timeout=10)
                if resp.status_code == 201:
                    logger.info("Registered DER: %s", der["name"])
                elif resp.status_code == 409:
                    logger.info("DER already exists: %s", der["name"])
                else:
                    logger.warning(
                        "Unexpected response registering %s: %d %s",
                        der["name"], resp.status_code, resp.text,
                    )
            except requests.ConnectionError:
                logger.error("Cannot reach API at %s", self.api_url)
                sys.exit(1)

    def generate_reading(self, der: dict, timestamp: datetime) -> dict:
        """Produce a single telemetry reading with realistic patterns.

        I'm using sinusoidal curves to mimic daily generation cycles: solar
        panels peak at midday, wind turbines have more irregular output, and
        batteries oscillate between charge and discharge. Gaussian noise is
        layered on top so the data isn't unnaturally smooth.
        """
        elapsed_hours = (timestamp - datetime(2026, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600
        hour_of_day = timestamp.hour + timestamp.minute / 60.0

        der_type = der["type"]

        if der_type == "solar":
            # Solar peaks around midday, zero at night
            solar_factor = max(0, math.sin(math.pi * (hour_of_day - 6) / 12))
            active_power = solar_factor * random.uniform(180, 320)
            reactive_power = solar_factor * random.uniform(-5, 15)
            voltage = 230 + solar_factor * 15 + random.gauss(0, 2)

        elif der_type == "wind":
            # Wind is more variable — slower sinusoid with higher noise
            wind_base = 0.5 + 0.5 * math.sin(elapsed_hours / 8)
            gust = random.gauss(0, 0.2)
            wind_factor = max(0, min(1, wind_base + gust))
            active_power = wind_factor * random.uniform(100, 500)
            reactive_power = wind_factor * random.uniform(-20, 30)
            voltage = 228 + wind_factor * 12 + random.gauss(0, 3)

        elif der_type == "battery":
            # Battery alternates between charging (negative) and discharging (positive)
            charge_cycle = math.sin(elapsed_hours / 4)
            active_power = charge_cycle * random.uniform(50, 200)
            reactive_power = random.uniform(-10, 10)
            voltage = 235 + charge_cycle * 8 + random.gauss(0, 1.5)

        else:
            active_power = random.uniform(50, 300)
            reactive_power = random.uniform(-10, 20)
            voltage = 230 + random.gauss(0, 5)

        return {
            "der_name": der["name"],
            "active_power": round(active_power, 2),
            "reactive_power": round(reactive_power, 2),
            "voltage": round(voltage, 2),
            "timestamp": timestamp.isoformat(),
        }

    def publish_reading(self, reading: dict) -> bool:
        try:
            resp = requests.post(
                f"{self.api_url}/api/telemetry",
                json=reading,
                timeout=10,
            )
            return resp.status_code == 202
        except requests.ConnectionError:
            logger.warning("API connection lost, will retry...")
            return False

    def backfill(self, hours: int, interval_seconds: int = 60):
        """Seed historical data so charts have content from the start.

        I'm generating one reading per minute for the backfill window,
        which gives a good density for 14-day chart visualisations
        without being overwhelming.
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=hours)
        current = start
        total = 0

        logger.info(
            "Backfilling %d hours of data (%s to %s)...",
            hours, start.isoformat(), now.isoformat(),
        )

        while current <= now:
            for der in self.ders:
                reading = self.generate_reading(der, current)
                if self.publish_reading(reading):
                    total += 1
            current += timedelta(seconds=interval_seconds)

        logger.info("Backfill complete: %d readings published.", total)

    def run_live(self, interval: int):
        """Continuously publish readings at the given interval."""
        logger.info(
            "Starting live simulation for %d DERs, publishing every %ds...",
            len(self.ders), interval,
        )

        try:
            while True:
                now = datetime.now(timezone.utc)
                for der in self.ders:
                    reading = self.generate_reading(der, now)
                    success = self.publish_reading(reading)
                    status = "ok" if success else "FAILED"
                    logger.info(
                        "[%s] %s | P=%.1fW Q=%.1fvar V=%.1fV",
                        status, der["name"],
                        reading["active_power"],
                        reading["reactive_power"],
                        reading["voltage"],
                    )
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user.")


def parse_args():
    parser = argparse.ArgumentParser(description="DER Telemetry Data Simulator")
    parser.add_argument(
        "--api-url", default=DEFAULT_API_URL,
        help=f"Base URL of the DER API (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--ders", type=int, default=3, choices=range(1, 6),
        help="Number of DERs to simulate (1-5, default: 3)",
    )
    parser.add_argument(
        "--interval", type=int, default=5,
        help="Seconds between readings in live mode (default: 5)",
    )
    parser.add_argument(
        "--backfill-hours", type=int, default=0,
        help="Hours of historical data to seed before live mode (default: 0)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    simulator = DERSimulator(api_url=args.api_url, der_count=args.ders)
    simulator.register_ders()

    if args.backfill_hours > 0:
        simulator.backfill(hours=args.backfill_hours)

    simulator.run_live(interval=args.interval)


if __name__ == "__main__":
    main()
