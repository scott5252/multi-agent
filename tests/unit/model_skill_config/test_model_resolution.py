from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import (
    ModelRoutingCandidate,
    ScopeSelector,
    ScopeType,
)
from multi_agent_platform.config.resolver import ResolutionError, resolve_model


def _candidate(scope: ScopeSelector, model_id: str, sequence: int = 1):
    return ModelRoutingCandidate(
        version_id=uuid4(),
        tenant_id=scope.tenant_id,
        scope=scope,
        version_sequence=sequence,
        activation_reason="test",
        model_provider_entry_id=uuid4(),
        provider_key="openai",
        model_id=model_id,
    )


def test_model_resolution_uses_step_agent_workflow_tenant_precedence() -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
    request = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_id,
        agent_key="researcher",
        step_key="summarize",
    )
    candidates = [
        _candidate(ScopeSelector(tenant_id=tenant_id), "tenant"),
        _candidate(
            ScopeSelector(tenant_id=tenant_id, workflow_lineage_id=workflow_id),
            "workflow",
        ),
        _candidate(
            ScopeSelector(
                tenant_id=tenant_id,
                workflow_lineage_id=workflow_id,
                agent_key="researcher",
            ),
            "agent",
        ),
        _candidate(request, "step"),
    ]

    resolved = resolve_model(candidates, request)

    assert resolved.model_id == "step"
    assert resolved.source_scope is ScopeType.STEP


def test_model_resolution_requires_global_default_or_override() -> None:
    with pytest.raises(ResolutionError) as exc_info:
        resolve_model([], ScopeSelector(tenant_id=uuid4()))

    assert exc_info.value.category.value == "missing_global_default"
