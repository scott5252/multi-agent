from __future__ import annotations

from multi_agent_platform.bootstrap.container import (
    build_secret_provider,
    build_storage_provider,
)
from multi_agent_platform.config.settings import Settings


def test_provider_selection_supports_secret_manager_and_s3(tmp_path) -> None:
    settings = Settings(
        _env_file=None,
        secret_provider="secret_manager",
        storage_provider="s3",
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'app.db'}",
        filesystem_storage_root=tmp_path / "artifacts",
    )
    assert build_secret_provider(settings).provider_name == "secret_manager"
    assert build_storage_provider(settings).provider_name == "s3"
