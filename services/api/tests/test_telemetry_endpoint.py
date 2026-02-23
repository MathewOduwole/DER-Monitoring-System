"""Integration tests for the telemetry endpoint.

Since telemetry publishing depends on Kafka (which is disabled in test mode),
I'm verifying the validation and error-handling paths here. The full
end-to-end Kafka flow is covered by the simulation script and manual testing.
"""

from datetime import datetime, timezone


class TestSubmitTelemetry:

    def test_valid_payload_returns_503_without_kafka(self, client):
        """In test mode Kafka is disabled, so a valid payload returns 503."""
        payload = {
            "der_name": "Test-DER",
            "active_power": 100.0,
            "reactive_power": 10.0,
            "voltage": 230.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post("/api/telemetry", json=payload)
        assert resp.status_code == 503
        assert "not available" in resp.get_json()["error"]

    def test_missing_fields_returns_400(self, client):
        resp = client.post("/api/telemetry", json={"der_name": "X"})
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert "active_power" in errors
        assert "voltage" in errors

    def test_missing_der_name_returns_400(self, client):
        payload = {
            "active_power": 100.0,
            "reactive_power": 10.0,
            "voltage": 230.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post("/api/telemetry", json=payload)
        assert resp.status_code == 400
        assert "der_name" in resp.get_json()["errors"]

    def test_invalid_timestamp_returns_400(self, client):
        payload = {
            "der_name": "X",
            "active_power": 100.0,
            "reactive_power": 10.0,
            "voltage": 230.0,
            "timestamp": "not-a-date",
        }
        resp = client.post("/api/telemetry", json=payload)
        assert resp.status_code == 400


class TestHealthEndpoint:

    def test_health_returns_status(self, client):
        resp = client.get("/health")
        assert resp.status_code in (200, 503)
        data = resp.get_json()
        assert "status" in data
        assert "database" in data
