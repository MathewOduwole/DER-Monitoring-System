"""Unit tests for the telemetry processor validation logic."""

import pytest
from unittest.mock import patch, MagicMock

from app.processor import TelemetryProcessor


@pytest.fixture
def processor():
    return TelemetryProcessor()


def _valid_event():
    return {
        "der_name": "Test-DER",
        "active_power": 200.0,
        "reactive_power": 15.0,
        "voltage": 230.0,
        "timestamp": "2026-02-20T12:00:00+00:00",
    }


class TestValidation:

    def test_valid_event_passes(self, processor):
        assert processor._validate(_valid_event()) is True

    def test_missing_field_fails(self, processor):
        event = _valid_event()
        del event["voltage"]
        assert processor._validate(event) is False

    def test_voltage_below_range_fails(self, processor):
        event = _valid_event()
        event["voltage"] = -5.0
        assert processor._validate(event) is False

    def test_voltage_above_range_fails(self, processor):
        event = _valid_event()
        event["voltage"] = 600.0
        assert processor._validate(event) is False

    def test_active_power_below_range_fails(self, processor):
        event = _valid_event()
        event["active_power"] = -20000.0
        assert processor._validate(event) is False

    def test_active_power_above_range_fails(self, processor):
        event = _valid_event()
        event["active_power"] = 20000.0
        assert processor._validate(event) is False

    def test_non_numeric_value_fails(self, processor):
        event = _valid_event()
        event["voltage"] = "not_a_number"
        assert processor._validate(event) is False

    def test_boundary_values_pass(self, processor):
        event = _valid_event()
        event["active_power"] = -10000.0
        event["reactive_power"] = 10000.0
        event["voltage"] = 0.0
        assert processor._validate(event) is True

        event["voltage"] = 500.0
        assert processor._validate(event) is True
