from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app import db, seed
from app.config import settings
from app.main import app


@pytest.fixture()
def anonymous_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / 'labos-test.db'
    storage_path = tmp_path / 'storage'
    storage_path.mkdir(parents=True, exist_ok=True)
    test_engine = create_engine(
        f'sqlite:///{db_path}',
        echo=False,
        connect_args={'check_same_thread': False},
    )
    monkeypatch.setattr(db, 'engine', test_engine)
    monkeypatch.setattr(seed, 'engine', test_engine)
    monkeypatch.setattr(settings, 'storage_path', str(storage_path))

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture()
def client(anonymous_client: TestClient):
    response = anonymous_client.post(
        '/api/v1/auth/login',
        json={
            'username': settings.bootstrap_admin_username,
            'password': settings.bootstrap_admin_password,
        },
    )
    assert response.status_code == 200
    return anonymous_client
