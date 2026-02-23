"""Integration tests for DER management endpoints."""

import json


SAMPLE_DER = {
    "name": "Solar-Panel-Test",
    "mrid_id": "SP-TEST-001",
    "location": "Test Rooftop",
    "type": "solar",
}


class TestRegisterDER:

    def test_register_success(self, client):
        resp = client.post("/api/ders", json=SAMPLE_DER)
        assert resp.status_code == 201

        data = resp.get_json()
        assert data["name"] == SAMPLE_DER["name"]
        assert data["mrid_id"] == SAMPLE_DER["mrid_id"]
        assert data["type"] == SAMPLE_DER["type"]
        assert data["location"] == SAMPLE_DER["location"]
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_returns_409(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        resp = client.post("/api/ders", json=SAMPLE_DER)
        assert resp.status_code == 409
        assert "already exists" in resp.get_json()["error"]

    def test_register_missing_name_returns_400(self, client):
        resp = client.post("/api/ders", json={"mrid_id": "X", "type": "solar"})
        assert resp.status_code == 400
        assert "name" in resp.get_json()["errors"]

    def test_register_missing_type_returns_400(self, client):
        resp = client.post("/api/ders", json={"name": "X", "mrid_id": "X"})
        assert resp.status_code == 400
        assert "type" in resp.get_json()["errors"]

    def test_register_without_location(self, client):
        der = {"name": "No-Location", "mrid_id": "NL-001", "type": "wind"}
        resp = client.post("/api/ders", json=der)
        assert resp.status_code == 201
        assert resp.get_json()["location"] is None


class TestListDERs:

    def test_list_empty(self, client):
        resp = client.get("/api/ders")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_registered_ders(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        client.post("/api/ders", json={
            "name": "Wind-Test", "mrid_id": "WT-001", "type": "wind",
        })

        resp = client.get("/api/ders")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2


class TestUpdateDER:

    def test_update_success(self, client):
        client.post("/api/ders", json=SAMPLE_DER)

        resp = client.put("/api/ders/Solar-Panel-Test", json={
            "location": "Updated Rooftop",
        })
        assert resp.status_code == 200
        assert resp.get_json()["location"] == "Updated Rooftop"

    def test_update_nonexistent_returns_404(self, client):
        resp = client.put("/api/ders/Does-Not-Exist", json={"type": "wind"})
        assert resp.status_code == 404


class TestDeleteDER:

    def test_delete_success(self, client):
        client.post("/api/ders", json=SAMPLE_DER)

        resp = client.delete("/api/ders/Solar-Panel-Test")
        assert resp.status_code == 200

        resp = client.get("/api/ders")
        assert len(resp.get_json()) == 0

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete("/api/ders/Does-Not-Exist")
        assert resp.status_code == 404


class TestGetDERData:

    def test_get_data_nonexistent_der_returns_404(self, client):
        resp = client.get("/api/ders/Does-Not-Exist/data")
        assert resp.status_code == 404

    def test_get_data_empty_returns_empty_list(self, client):
        client.post("/api/ders", json=SAMPLE_DER)
        resp = client.get("/api/ders/Solar-Panel-Test/data")
        assert resp.status_code == 200
        assert resp.get_json() == []
