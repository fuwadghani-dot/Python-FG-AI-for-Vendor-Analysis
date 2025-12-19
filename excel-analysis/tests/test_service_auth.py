from fastapi.testclient import TestClient
import os
from excel_analysis.scripts import service


def test_service_auth_runs_with_token(monkeypatch):
    client = TestClient(service.app)

    # set a token and monkeypatch runner.run_once to avoid heavy work
    monkeypatch.setenv("SERVICE_TOKEN", "secrettoken")

    called = {"ok": False}

    def fake_run(workbook):
        called["ok"] = True
        return "/tmp/fake.xlsx"

    monkeypatch.setattr(service, "runner", type("R", (), {"run_once": staticmethod(fake_run)})())

    # without auth - should return 401
    r = client.post("/run", json={"workbook": "Data AI for Vendor analysis.xlsx"})
    assert r.status_code == 401

    # with wrong token
    r = client.post("/run", json={"workbook": "Data AI for Vendor analysis.xlsx"}, headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 403

    # with correct token
    r = client.post("/run", json={"workbook": "Data AI for Vendor analysis.xlsx"}, headers={"Authorization": "Bearer secrettoken"})
    assert r.status_code == 200
    assert called["ok"]
