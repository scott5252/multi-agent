from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.telegram_config import (
    TenantTelegramConfigUpdateRequest,
)


def test_telegram_config_update_accepts_known_commands(seeded_tenant) -> None:
    payload = TenantTelegramConfigUpdateRequest(
        tenant_id=seeded_tenant.tenant_id,
        enabled=True,
        protected_commands=("/run", "/status"),
    )

    assert payload.protected_commands == ("/run", "/status")


def test_telegram_config_update_rejects_unknown_commands(seeded_tenant) -> None:
    with pytest.raises(ValidationError):
        TenantTelegramConfigUpdateRequest(
            tenant_id=seeded_tenant.tenant_id,
            enabled=True,
            protected_commands=("/debug-private-message",),
        )
