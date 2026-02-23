"""Integration tests for chart management endpoints."""

from datetime import datetime, timedelta, timezone


SAMPLE_DER = {
    "name": "Solar-Chart-Test",
    "mrid_id": "SC-001",
    "location": "Roof",
    "type": "solar",
}


def _make_chart_payload(der_names, days=1):
    now = datetime.now(timezone.utc)
    return {
        "name": "Test Chart",
        "der_names": der_names,
        "start_date": (now - timedelta(days=days)).isoformat(),
        "end_date": now.isoformat(),
    }


class TestCreateChart:

    def test_create_success(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"])

        resp = client.post("/api/charts", json=payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test Chart"
        assert data["der_names"] == ["Solar-Chart-Test"]

    def test_create_with_nonexistent_der_returns_400(self, client):
        payload = _make_chart_payload(["Ghost-DER"])
        resp = client.post("/api/charts", json=payload)
        assert resp.status_code == 400
        assert "not found" in resp.get_json()["error"]

    def test_create_exceeding_three_ders_returns_400(self, client):
        for i in range(4):
            client.post("/api/ders", json={
                "name": f"DER-{i}", "mrid_id": f"D-{i}", "type": "solar",
            })
        payload = _make_chart_payload(["DER-0", "DER-1", "DER-2", "DER-3"])
        resp = client.post("/api/charts", json=payload)
        assert resp.status_code == 400

    def test_create_exceeding_fourteen_days_returns_400(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"], days=15)
        resp = client.post("/api/charts", json=payload)
        assert resp.status_code == 400

    def test_create_missing_name_returns_400(self, client):
        resp = client.post("/api/charts", json={
            "der_names": ["x"],
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": datetime.now(timezone.utc).isoformat(),
        })
        assert resp.status_code == 400


class TestGetChart:

    def test_get_chart_with_data(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"])
        create_resp = client.post("/api/charts", json=payload)
        chart_id = create_resp.get_json()["id"]

        resp = client.get(f"/api/charts/{chart_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "series" in data
        assert "Solar-Chart-Test" in data["series"]

    def test_get_nonexistent_chart_returns_404(self, client):
        resp = client.get("/api/charts/99999")
        assert resp.status_code == 404


class TestUpdateChart:

    def test_update_name(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"])
        create_resp = client.post("/api/charts", json=payload)
        chart_id = create_resp.get_json()["id"]

        resp = client.put(f"/api/charts/{chart_id}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Updated Name"

    def test_update_nonexistent_returns_404(self, client):
        resp = client.put("/api/charts/99999", json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteChart:

    def test_delete_success(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"])
        create_resp = client.post("/api/charts", json=payload)
        chart_id = create_resp.get_json()["id"]

        resp = client.delete(f"/api/charts/{chart_id}")
        assert resp.status_code == 200

        resp = client.get(f"/api/charts/{chart_id}")
        assert resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/api/charts/99999")
        assert resp.status_code == 404


class TestListCharts:

    def test_list_empty(self, client):
        resp = client.get("/api/charts")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_created_charts(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        payload = _make_chart_payload(["Solar-Chart-Test"])
        client.post("/api/charts", json=payload)

        resp = client.get("/api/charts")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1
