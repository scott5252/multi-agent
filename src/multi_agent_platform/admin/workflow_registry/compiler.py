from __future__ import annotations

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument
from multi_agent_platform.runtime.workflow_bundle import CompiledWorkflowBundle


def compile_workflow_blueprint(
    *,
    workflow_lineage_id: str,
    revision_sha256: str,
    document: WorkflowDraftDocument,
) -> CompiledWorkflowBundle:
    return CompiledWorkflowBundle(
        workflow_lineage_id=workflow_lineage_id,
        source_revision_sha256=revision_sha256,
        workflow_key=document.workflow_key,
        workflow_kind=document.workflow_kind.value,
        document=document.model_dump(mode="json"),
    )
