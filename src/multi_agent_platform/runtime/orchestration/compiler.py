from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.runtime.orchestration.contracts import sha256_digest
from multi_agent_platform.runtime.orchestration.models import RuntimeExecutionBundle


@dataclass(slots=True, frozen=True)
class PublishedWorkflowBundle:
    published_workflow_version_id: UUID
    workflow: dict[str, object]
    contracts: dict[str, object]
    retry_policy: dict[str, object]
    checkpoint_policy: dict[str, object]

    @property
    def digest(self) -> str:
        return sha256_digest(
            {
                "published_workflow_version_id": str(
                    self.published_workflow_version_id
                ),
                "workflow": self.workflow,
                "contracts": self.contracts,
                "retry_policy": self.retry_policy,
                "checkpoint_policy": self.checkpoint_policy,
            }
        )


def clone_execution_bundle(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    published_bundle: PublishedWorkflowBundle,
) -> RuntimeExecutionBundle:
    return RuntimeExecutionBundle(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=published_bundle.published_workflow_version_id,
        bundle_digest=published_bundle.digest,
        workflow_version=published_bundle.workflow,
        contract_versions=published_bundle.contracts,
        checkpoint_policy=published_bundle.checkpoint_policy,
    )


def compile_graph_config(workflow_run_id: UUID) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": str(workflow_run_id)}}
