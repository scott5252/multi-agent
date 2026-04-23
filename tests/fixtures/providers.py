from __future__ import annotations

import pytest

from multi_agent_platform.secrets.providers.static import StaticSecretProvider
from multi_agent_platform.storage.providers.filesystem import FilesystemStorageProvider


@pytest.fixture
def static_secret_provider() -> StaticSecretProvider:
    return StaticSecretProvider({"example/api-key": "fixture-secret"})


@pytest.fixture
def filesystem_storage_provider(tmp_path) -> FilesystemStorageProvider:
    return FilesystemStorageProvider(tmp_path / "artifacts")


@pytest.fixture
def workflow_registry_artifact_prefix(settings) -> str:
    return settings.workflow_registry_artifact_prefix
