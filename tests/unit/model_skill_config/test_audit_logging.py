from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import ConfigKind
from multi_agent_platform.config.provenance import audit_diff_summary


def test_audit_diff_summary_covers_history_actions_without_secret_values() -> None:
    for action in (
        "create",
        "activate",
        "deactivate",
        "rollback",
        "migration",
        "validation_failure",
        "authorization_failure",
        "runtime_policy_denied",
    ):
        summary = audit_diff_summary(
            action=action,
            config_kind=ConfigKind.CREDENTIAL_REQUIREMENT,
            prior_version_id=uuid4(),
            new_version_id=uuid4(),
            summary={"token": "raw", "reason": "safe"},
        )

        assert summary["action"] == action
        assert "raw" not in str(summary)
        assert "***REDACTED***" in str(summary)
