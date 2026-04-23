from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftCreateRequest,
    WorkflowDraftDocument,
)


def test_workflow_draft_create_request_parses_platform_scope(
    sample_workflow_document,
) -> None:
    payload = WorkflowDraftCreateRequest(
        scope_type="platform",
        workflow_kind="main_workflow",
        slug="customer-intake",
        display_name="Customer Intake",
        document=sample_workflow_document,
    )
    assert payload.scope_type == "platform"
    assert payload.document.entry_node_key == "triage-node"


def test_workflow_document_rejects_duplicate_role_keys(
    sample_workflow_document,
) -> None:
    duplicate = sample_workflow_document.model_dump(mode="json")
    duplicate["roles"] = [duplicate["roles"][0], duplicate["roles"][0]]
    with pytest.raises(ValidationError):
        WorkflowDraftDocument.model_validate(duplicate)
