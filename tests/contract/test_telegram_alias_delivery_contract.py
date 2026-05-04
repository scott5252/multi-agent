from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_telegram_alias_delivery_contract_contains_required_paths() -> None:
    openapi = create_app().openapi()
    paths = openapi["paths"]

    for path in (
        "/admin/telegram/api/aliases",
        "/channels/telegram/webhook/{secret}",
    ):
        assert path in paths

    alias_schema = openapi["components"]["schemas"]["TelegramCommandAliasResponse"]
    for field in (
        "alias_text",
        "alias_normalized",
        "published_workflow_version_id",
        "protected",
        "enabled",
        "revision_token",
    ):
        assert field in alias_schema["properties"]
