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
    assert settings.profiles["worker"].required_dependencies[-1] == "queue"


def test_settings_expose_web_admin_paths(settings: Settings) -> None:
    assert settings.web_admin_templates_dir.name == "templates"
    assert settings.web_admin_static_dir.name == "static"
    assert settings.workflow_registry_artifact_prefix == "workflow-registry"
