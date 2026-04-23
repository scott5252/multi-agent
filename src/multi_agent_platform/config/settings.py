from __future__ import annotations

from enum import StrEnum
from functools import cached_property
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from multi_agent_platform.auth.principal import AuthMode


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


class LocalPrincipalCatalogEntry(BaseModel):
    catalog_key: str
    display_name: str
    tenant_id: UUID | None = None
    org_id: str | None = None
    role_codes: tuple[str, ...] = Field(default_factory=tuple)
    permission_codes: tuple[str, ...] = Field(default_factory=tuple)
    enabled: bool = True


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
    auth_mode: AuthMode = AuthMode.LOCAL_PRINCIPAL

    auth0_domain: str | None = None
    auth0_issuer: str | None = None
    auth0_audience: str | None = None
    auth0_algorithms: tuple[str, ...] = ("RS256",)
    auth0_required_org_claim: bool = True
    auth0_jwks_path: str = "/.well-known/jwks.json"

    local_principal_header: str = "X-Local-Principal"
    local_principal_cookie_name: str = "map_local_principal"
    local_principal_catalog_json: dict[str, LocalPrincipalCatalogEntry] = Field(
        default_factory=dict
    )

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

    @model_validator(mode="after")
    def validate_auth_configuration(self) -> Settings:
        if self.auth_mode is AuthMode.AUTH0:
            required = {
                "auth0_domain": self.auth0_domain,
                "auth0_issuer": self.auth0_issuer,
                "auth0_audience": self.auth0_audience,
            }
            missing = sorted(name for name, value in required.items() if not value)
            if missing:
                joined = ", ".join(missing)
                raise ValueError(
                    f"auth0 mode requires the following settings: {joined}"
                )
        elif self.app_env is AppEnvironment.PRODUCTION:
            raise ValueError("local_principal auth mode is not allowed in production")

        if not self.local_principal_header.startswith("X-"):
            raise ValueError("local_principal_header must be an X- prefixed header")
        return self

    @cached_property
    def database_migration_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            return self.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")
        return self.database_url

    @cached_property
    def auth0_jwks_url(self) -> str | None:
        if self.auth0_domain is None:
            return None
        return f"https://{self.auth0_domain.rstrip('/')}{self.auth0_jwks_path}"

    @cached_property
    def profiles(self) -> dict[ProcessRole, ProcessProfile]:
        return {
            ProcessRole.API: ProcessProfile(
                process_role=ProcessRole.API,
                required_dependencies=(
                    "config",
                    "auth",
                    "database",
                    "migrations",
                    "worker",
                ),
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

    @cached_property
    def web_admin_root(self) -> Path:
        return Path(__file__).resolve().parents[1] / "web_admin"

    @cached_property
    def web_admin_templates_dir(self) -> Path:
        return self.web_admin_root / "templates"

    @cached_property
    def web_admin_static_dir(self) -> Path:
        return self.web_admin_root / "static"

    @cached_property
    def workflow_registry_artifact_prefix(self) -> str:
        return "workflow-registry"

    def ensure_directories(self) -> None:
        self.filesystem_storage_root.mkdir(parents=True, exist_ok=True)
        Path(".data").mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings()
