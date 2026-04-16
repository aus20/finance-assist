from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = REPO_ROOT / "db" / "finally.db"


@pytest.fixture()
def client() -> TestClient:
    DATABASE_PATH.unlink(missing_ok=True)
    with TestClient(app) as test_client:
        yield test_client
    DATABASE_PATH.unlink(missing_ok=True)
