from __future__ import annotations

from pathlib import Path

import pytest

from multi_agent_platform.config.settings import Settings


def make_settings(tmp_path: Path) -> Settings:
    database_path = tmp_path / "platform.db"
    return Settings(
        app_env="test",
        database_url=f"sqlite+aiosqlite:///{database_path}",
        filesystem_storage_root=tmp_path / "artifacts",
        static_secrets_json={"example/api-key": "fixture-secret"},
    )


@pytest.fixture
def settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    resolved = make_settings(tmp_path)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", resolved.database_url)
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(resolved.filesystem_storage_root))
    monkeypatch.setenv("STATIC_SECRETS_JSON", '{"example/api-key":"fixture-secret"}')
    monkeypatch.setenv("SECRET_PROVIDER", "static")
    monkeypatch.setenv("STORAGE_PROVIDER", "filesystem")
    monkeypatch.setenv("AUTH_ENABLED", "false")
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    monkeypatch.setenv("COMMIT_SHA", "test-sha")
    monkeypatch.setenv("BUILD_TIME", "2026-04-22T00:00:00+00:00")
    return Settings()
