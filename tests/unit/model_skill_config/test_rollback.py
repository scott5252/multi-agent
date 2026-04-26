from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import ConfigKind
from multi_agent_platform.config.rollback import RollbackError, plan_rollback


def test_plan_rollback_rejects_stale_expected_version() -> None:
    with pytest.raises(RollbackError) as exc_info:
        plan_rollback(
            config_kind=ConfigKind.MODEL_ROUTING,
            scope_hash="scope",
            current_active_version_id=uuid4(),
            expected_active_version_id=uuid4(),
            target_version_id=uuid4(),
            target_scope_hash="scope",
            reason="restore",
        )

    assert exc_info.value.category.value == "stale_configuration"


def test_plan_rollback_builds_same_scope_plan() -> None:
    current = uuid4()
    target = uuid4()

    plan = plan_rollback(
        config_kind=ConfigKind.MODEL_ROUTING,
        scope_hash="scope",
        current_active_version_id=current,
        expected_active_version_id=current,
        target_version_id=target,
        target_scope_hash="scope",
        reason="restore",
    )

    assert plan.from_version_id == current
    assert plan.to_version_id == target
