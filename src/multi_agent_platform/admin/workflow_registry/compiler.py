from __future__ import annotations

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument
from multi_agent_platform.runtime.workflow_bundle import CompiledWorkflowBundle


def compile_workflow_blueprint(
    *,
    workflow_lineage_id: str,
    revision_sha256: str,
    document: WorkflowDraftDocument,
    version_sequence: int,
    display_version: str,
    compiler_version: str,
) -> CompiledWorkflowBundle:
    skill_dependencies: list[dict[str, object]] = []
    for role in document.roles:
        for binding in role.skill_bindings:
            skill_dependencies.append(
                {
                    "binding_key": binding.binding_key,
                    "role_key": role.role_key,
                    "skill_slug": binding.skill_slug,
                    "skill_version": binding.skill_version,
                    "binding_mode": binding.binding_mode.value,
                    "expected_runtime_refs": list(binding.expected_runtime_refs),
                }
            )
    contract_dependencies = [
        {
            "contract_key": contract.contract_key,
            "semantic_version": contract.semantic_version,
            "json_schema": contract.json_schema,
        }
        for contract in document.contracts
    ]
    subworkflow_dependencies = [
        {
            "alias": reference.alias,
            "workflow_version_ref": reference.workflow_version_ref,
            "input_contract_key": reference.input_contract_key,
            "output_contract_key": reference.output_contract_key,
        }
        for reference in document.subworkflow_refs
    ]
    return CompiledWorkflowBundle(
        workflow_lineage_id=workflow_lineage_id,
        source_revision_sha256=revision_sha256,
        workflow_key=document.workflow_key,
        workflow_kind=document.workflow_kind.value,
        version_sequence=version_sequence,
        display_version=display_version,
        compiler_version=compiler_version,
        dependencies={
            "skills": skill_dependencies,
            "contracts": contract_dependencies,
            "subworkflows": subworkflow_dependencies,
            "join_policies": [
                policy.model_dump(mode="json") for policy in document.join_policies
            ],
            "approval_gates": [
                gate.model_dump(mode="json") for gate in document.approval_gates
            ],
        },
        run_version_blueprint={
            "entry_node_key": document.entry_node_key,
            "node_count": len(document.nodes),
            "edge_count": len(document.edges),
        },
        document=document.model_dump(mode="json"),
    )
