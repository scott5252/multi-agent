from __future__ import annotations

from multi_agent_platform.admin.skill_registry.quarantine import (
    quarantine_target,
    resolve_quarantine,
)


def test_quarantine_blocks_lifecycle_use_until_resolved() -> None:
    decision = quarantine_target(
        target_type="installation",
        target_id="install-1",
        reason="unsafe fixture",
        actor_principal_id="platform-admin",
    )

    assert decision.blocks_new_installs is True
    assert decision.blocks_readiness is True
    assert decision.blocks_bindings is True
    assert decision.blocks_runtime is True

    resolved = resolve_quarantine(
        decision,
        actor_principal_id="platform-admin",
        reason="fixture removed",
    )

    assert resolved.state == "resolved"
    assert resolved.blocks_runtime is False
