from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import (
    PromptReferenceCandidate,
    ScopeSelector,
    ScopeType,
)
from multi_agent_platform.config.resolver import ResolutionError, resolve_prompt


def _candidate(scope: ScopeSelector):
    return PromptReferenceCandidate(
        version_id=uuid4(),
        tenant_id=scope.tenant_id,
        scope=scope,
        activation_reason="test",
        prompt_id=uuid4(),
        prompt_version_id=uuid4(),
        prompt_digest="abc",
    )


def test_prompt_resolution_does_not_use_tenant_global_prompts() -> None:
    tenant_id = uuid4()
    with pytest.raises(ResolutionError) as exc_info:
        resolve_prompt(
            [_candidate(ScopeSelector(tenant_id=tenant_id))],
            ScopeSelector(tenant_id=tenant_id),
        )

    assert exc_info.value.category.value == "missing_prompt_version"


def test_prompt_resolution_uses_step_agent_workflow_precedence() -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
    request = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_id,
        agent_key="agent",
        step_key="step",
    )
    resolved = resolve_prompt(
        [
            _candidate(
                ScopeSelector(tenant_id=tenant_id, workflow_lineage_id=workflow_id)
            ),
            _candidate(
                ScopeSelector(
                    tenant_id=tenant_id,
                    workflow_lineage_id=workflow_id,
                    agent_key="agent",
                )
            ),
            _candidate(request),
        ],
        request,
    )

    assert resolved.source_scope is ScopeType.STEP
