from pathlib import Path

from app.main import app, health


def test_health_endpoint_returns_expected_status_and_payload(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database_path"] == "db/finally.db"
    assert payload["initialized"] is True


def test_health_startup_initializes_repo_level_database_file(client):
    response = client.get("/api/health")
    assert response.status_code == 200

    repo_root = Path(__file__).resolve().parents[2]
    assert (repo_root / "db" / "finally.db").exists()


def test_health_reports_starting_when_bootstrap_has_not_run():
    if hasattr(app.state, "bootstrap"):
        delattr(app.state, "bootstrap")

    payload = health()

    assert payload["status"] == "starting"
    assert payload["database_path"] == "db/finally.db"
    assert payload["initialized"] is False
