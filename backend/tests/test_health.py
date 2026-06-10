"""Smoke tests for the app skeleton: it boots and basic probes respond."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz(client: TestClient) -> None:
    resp = client.get("/readyz")
    assert resp.status_code == 200


def test_openapi_available(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "OpportunityPulse API"


def test_admin_health_shape(client: TestClient) -> None:
    resp = client.get("/admin/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "pipeline" in body and "sources" in body and "eval" in body
