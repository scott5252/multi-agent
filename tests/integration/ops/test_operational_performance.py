from __future__ import annotations

import time

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app


def test_liveness_endpoint_returns_quickly(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'perf.db'}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    app = create_app()
    with TestClient(app) as client:
        started = time.perf_counter()
        response = client.get("/health/live")
        elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert elapsed < 0.5
