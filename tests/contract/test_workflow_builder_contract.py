from __future__ import annotations

from pathlib import Path

CONTRACT = Path(
    "specs/013-admin-workflow-builder/contracts/workflow-builder.openapi.yaml"
)


def test_workflow_builder_contract_lists_builder_endpoints() -> None:
    text = CONTRACT.read_text()

    for path in (
        "/admin/workflows/editor-metadata",
        "/admin/workflows/editor-lookups",
        "/admin/workflows/drafts/{workflow_draft_id}/graph-preview",
        "/admin/workflows/drafts/{workflow_draft_id}/revisions",
        "/admin/workflows/drafts/{workflow_draft_id}/publish-gate",
        "/admin/workflows/drafts/{workflow_draft_id}/publish",
    ):
        assert path in text


def test_workflow_builder_contract_names_publish_gate_fields() -> None:
    text = CONTRACT.read_text()

    for field in (
        "publish_gate_id",
        "workflow_draft_revision_id",
        "reference_readiness",
        "required_test_summary",
        "digest",
    ):
        assert field in text
