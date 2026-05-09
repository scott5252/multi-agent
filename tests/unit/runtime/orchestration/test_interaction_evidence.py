from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
)
from multi_agent_platform.runtime.orchestration.interaction_evidence import (
    interaction_idempotency_key,
    record_runtime_interaction,
    safe_artifact_refs,
    safe_interaction_provenance,
    safe_interaction_summary,
    safe_node_key,
)


def test_interaction_idempotency_key_is_stable_and_bounded() -> None:
    workflow_run_id = uuid4()

    first = interaction_idempotency_key(
        workflow_run_id=workflow_run_id,
        source_node_key="coordinator",
        target_node_key="specialist",
        interaction_kind=RuntimeInteractionKind.HANDOFF,
        stable_ref={"edge": "coordinator-specialist"},
    )
    second = interaction_idempotency_key(
        workflow_run_id=workflow_run_id,
        source_node_key="coordinator",
        target_node_key="specialist",
        interaction_kind=RuntimeInteractionKind.HANDOFF,
        stable_ref={"edge": "coordinator-specialist"},
    )

    assert first == second
    assert len(first) <= 160


def test_safe_interaction_helpers_redact_sensitive_metadata() -> None:
    provenance, classification = safe_interaction_provenance(
        {
            "edge_key": "coordinator-specialist",
            "raw_prompt": "do not persist me",
            "provider_response": {"message": "private response"},
        }
    )

    assert classification == "redacted-summary"
    assert provenance["raw_prompt"]["redacted"] is True
    assert provenance["provider_response"]["redacted"] is True
    assert "do not persist me" not in str(provenance)
    assert (
        safe_interaction_summary("raw prompt: do not show")
        == "Interaction evidence recorded with sensitive details redacted."
    )
    assert safe_interaction_summary("x" * 400).endswith("...")


def test_safe_interaction_helpers_handle_non_dict_and_artifacts() -> None:
    provenance, classification = safe_interaction_provenance({"items": ["secret"]})

    assert classification == "safe-summary"
    assert isinstance(provenance, dict)
    refs = safe_artifact_refs(
        [
            {"secret_value": "do not expose"},
            "artifact:plain",
        ]
    )
    assert refs[0]["secret_value"]["redacted"] is True
    assert refs[1] == "artifact:plain"
    assert safe_node_key("node\nkey") == "nodekey"
    assert safe_node_key("") == "unknown"


@pytest.mark.asyncio
async def test_record_runtime_interaction_uses_repository_idempotency() -> None:
    class FakeRepository:
        def __init__(self) -> None:
            self.calls = 0

        async def record_interaction_evidence(self, **kwargs):
            self.calls += 1
            return kwargs

    repository = FakeRepository()
    workflow_run_id = uuid4()
    key = interaction_idempotency_key(
        workflow_run_id=workflow_run_id,
        source_node_key="source",
        target_node_key="target",
        interaction_kind=RuntimeInteractionKind.CONTEXT_TRANSFER,
        stable_ref="stable",
    )

    result = await record_runtime_interaction(
        repository,  # type: ignore[arg-type]
        tenant_id=uuid4(),
        workflow_run_id=workflow_run_id,
        source_node_key="source",
        target_node_key="target",
        interaction_kind=RuntimeInteractionKind.CONTEXT_TRANSFER,
        status=RuntimeInteractionStatus.SENT,
        safe_summary="Safe context transferred.",
        idempotency_key=key,
        metadata={"safe": "yes"},
    )

    assert repository.calls == 1
    assert result["classification"] == "safe-summary"
    assert result["payload_digest"]
