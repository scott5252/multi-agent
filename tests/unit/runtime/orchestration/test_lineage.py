from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.lineage import RunLineage


def test_lineage_requires_parent_child_tenant_match() -> None:
    lineage = RunLineage(
        tenant_id=uuid4(),
        parent_run_id=uuid4(),
        parent_step_id=uuid4(),
        child_run_id=uuid4(),
    )

    with pytest.raises(ValueError, match="share tenant"):
        lineage.assert_same_tenant(uuid4())


def test_lineage_defaults_to_cascade_cancel() -> None:
    tenant_id = uuid4()
    lineage = RunLineage(
        tenant_id=tenant_id,
        parent_run_id=uuid4(),
        parent_step_id=uuid4(),
        child_run_id=uuid4(),
    )

    lineage.assert_same_tenant(tenant_id)
    assert lineage.child_cancellation_policy == "cascade_cancel"
