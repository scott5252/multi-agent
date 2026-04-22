from __future__ import annotations

from enum import StrEnum
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    CI = "ci"
    PRODUCTION = "production"


class ProcessRole(StrEnum):
    API = "api"
    WORKER = "worker"
    CLI = "cli"


class SecretProviderKind(StrEnum):
    STATIC = "static"
    ENV = "env"
    SECRET_MANAGER = "secret_manager"


class StorageProviderKind(StrEnum):
    FILESYSTEM = "filesystem"
    S3 = "s3"


class ProcessProfile(BaseModel):
    process_role: ProcessRole
    required_dependencies: tuple[str, ...]
    readiness_policy: str
    scope_type: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnvironment = AppEnvironment.LOCAL
    app_name: str = "multi-agent-platform"
    app_version: str = "0.1.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"
    auth_enabled: bool = False

    database_url: str = "sqlite+aiosqlite:///./.data/multi_agent_platform.db"
    database_echo: bool = False

    secret_provider: SecretProviderKind = SecretProviderKind.STATIC
    static_secrets_json: dict[str, str] = Field(default_factory=dict)
    env_secret_prefix: str = "MAP_SECRET_"
    secret_manager_prefix: str = "secret-manager/"

    storage_provider: StorageProviderKind = StorageProviderKind.FILESYSTEM
    filesystem_storage_root: Path = Path(".data/artifacts")
    s3_bucket: str = "multi-agent-platform"
    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"

    metrics_enabled: bool = True
    tracing_enabled: bool = False

    worker_poll_interval_seconds: float = 0.1
    worker_lease_seconds: int = 60

    commit_sha: str = "dev"
    build_time: str = "1970-01-01T00:00:00+00:00"

    @cached_property
    def database_migration_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            return self.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")
        return self.database_url

    @cached_property
    def profiles(self) -> dict[ProcessRole, ProcessProfile]:
        return {
            ProcessRole.API: ProcessProfile(
                process_role=ProcessRole.API,
                required_dependencies=("config", "database", "migrations", "worker"),
                readiness_policy="strict",
                scope_type="platform",
            ),
            ProcessRole.WORKER: ProcessProfile(
                process_role=ProcessRole.WORKER,
                required_dependencies=("config", "database", "queue"),
                readiness_policy="strict",
                scope_type="platform",
            ),
            ProcessRole.CLI: ProcessProfile(
                process_role=ProcessRole.CLI,
                required_dependencies=("config", "database"),
                readiness_policy="best_effort",
                scope_type="platform",
            ),
        }

    def ensure_directories(self) -> None:
        self.filesystem_storage_root.mkdir(parents=True, exist_ok=True)
        Path(".data").mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings()
