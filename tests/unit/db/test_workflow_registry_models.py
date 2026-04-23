from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowLineage,
)


async def test_workflow_registry_models_persist_revision_data(session) -> None:
    principal_id = uuid4()
    lineage = WorkflowLineage(
        scope_type="platform",
        tenant_id=None,
        slug="example-workflow",
        display_name="Example Workflow",
        workflow_kind="main_workflow",
        created_by_principal_id=principal_id,
    )
    session.add(lineage)
    await session.flush()
    draft = WorkflowDraft(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="platform",
        tenant_id=None,
        current_revision_number=1,
        created_by_principal_id=principal_id,
        last_edited_by_principal_id=principal_id,
    )
    session.add(draft)
    await session.flush()
    revision = WorkflowDraftRevision(
        workflow_draft_id=draft.workflow_draft_id,
        revision_number=1,
        authoring_document_json={"workflow_key": "example-workflow"},
        document_sha256="abc",
        created_by_principal_id=principal_id,
    )
    session.add(revision)
    await session.flush()
    draft.latest_revision_id = revision.workflow_draft_revision_id
    await session.flush()

    stored = (
        await session.execute(
            select(WorkflowDraftRevision).where(
                WorkflowDraftRevision.workflow_draft_id == draft.workflow_draft_id
            )
        )
    ).scalar_one()
    assert stored.authoring_document_json["workflow_key"] == "example-workflow"
