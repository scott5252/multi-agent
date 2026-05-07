from __future__ import annotations

from multi_agent_platform.config.settings import Settings


def test_settings_parse_and_normalize_urls(settings: Settings) -> None:
    assert settings.app_env == "test"
    assert settings.auth_mode == "local_principal"
    assert settings.database_url.startswith("sqlite+aiosqlite:///")
    assert settings.database_migration_url.startswith("sqlite:///")


def test_process_profiles_include_api_and_worker(settings: Settings) -> None:
    assert settings.profiles["api"].readiness_policy == "strict"
    assert settings.profiles["api"].required_dependencies[1] == "auth"
    assert settings.profiles["worker"].required_dependencies[-1] == "runtime"


def test_settings_expose_web_admin_paths(settings: Settings) -> None:
    assert settings.web_admin_static_dir.name == "static"
    assert settings.workflow_registry_artifact_prefix == "workflow-registry"
    assert settings.runtime_checkpoint_database_url == settings.database_url


def test_channel_settings_defaults_and_bounds() -> None:
    settings = Settings(_env_file=None, app_env="test")

    assert settings.telegram_link_token_ttl_seconds == 600
    assert settings.channel_artifact_url_ttl_seconds == 900
    assert settings.channel_artifact_url_max_ttl_seconds == 3600
    assert settings.channel_sse_heartbeat_seconds == 15
    assert settings.channel_rate_limit_per_minute == 120


def test_channel_artifact_ttl_must_not_exceed_max() -> None:
    try:
        Settings(
            _env_file=None,
            app_env="test",
            channel_artifact_url_ttl_seconds=120,
            channel_artifact_url_max_ttl_seconds=60,
        )
    except ValueError as exc:
        assert "artifact URL TTL" in str(exc)
    else:
        raise AssertionError("settings should reject invalid artifact TTL bounds")
