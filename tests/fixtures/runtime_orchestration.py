from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.compiler import PublishedWorkflowBundle
from multi_agent_platform.runtime.orchestration.contracts import HandoffContract


@pytest.fixture
def published_workflow_bundle() -> PublishedWorkflowBundle:
    return PublishedWorkflowBundle(
        published_workflow_version_id=uuid4(),
        workflow={"workflow_key": "durable-demo"},
        contracts={"handoff": {"version": "1"}},
        retry_policy={"max_attempts": 3},
        checkpoint_policy={"semantic_boundaries": True},
    )


@pytest.fixture
def handoff_contract() -> HandoffContract:
    return HandoffContract(
        contract_id="handoff",
        contract_version="1",
        json_schema={
            "type": "object",
            "required": ["message"],
            "properties": {"message": {"type": "string"}},
        },
    )
