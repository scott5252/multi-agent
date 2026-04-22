from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app


def test_readiness_fails_when_migrations_are_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'missing.db'}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health/ready")
    assert response.status_code == 503


def test_readiness_fails_when_worker_dependencies_are_unhealthy(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'worker.db'}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    app = create_app()
    with TestClient(app) as client:
        client.app.state.container.worker_dependencies_ready = False
        response = client.get("/health/ready")
    assert response.status_code == 503
