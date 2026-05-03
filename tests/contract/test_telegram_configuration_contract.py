from __future__ import annotations

from pathlib import Path


def test_telegram_configuration_contract_covers_required_routes() -> None:
    contract = Path(
        "specs/017-telegram-configuration-console/contracts/"
        "telegram-configuration.openapi.yaml"
    ).read_text(encoding="utf-8")

    for route in (
        "/admin/telegram/api/readiness",
        "/admin/telegram/api/config",
        "/admin/telegram/api/webhook/validate",
        "/admin/telegram/api/link-tokens",
        "/admin/telegram/api/identities",
        "/admin/telegram/api/diagnostics",
    ):
        assert route in contract
