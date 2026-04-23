from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.validation import (
    validate_authoring_document,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    ApprovalGateDefinition,
    JoinPolicyDefinition,
    SubworkflowReference,
    WorkflowNodeDefinition,
)


def test_validate_authoring_document_flags_non_exact_skill_versions(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.roles[0].skill_bindings[0].skill_version = "latest"

    findings = validate_authoring_document(document)

    assert any(
        finding["category"] == "skill_binding"
        and finding["severity"] == "blocking"
        and finding["field_path"] == "roles[0].skill_bindings[0].skill_version"
        for finding in findings
    )


def test_validate_authoring_document_flags_join_policy_shape_violations(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.join_policies.append(
        JoinPolicyDefinition(
            join_policy_key="review-quorum",
            strategy="quorum",
            required_branches=("branch-a", "branch-b"),
            quorum_count=3,
        )
    )

    findings = validate_authoring_document(document)

    assert any(
        finding["category"] == "join_policy"
        and finding["severity"] == "blocking"
        and finding["field_path"] == "join_policies[0].quorum_count"
        for finding in findings
    )


def test_validate_authoring_document_flags_approval_gate_mismatches(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.approval_gates.append(
        ApprovalGateDefinition(
            approval_gate_key="manager-review",
            display_name="Manager Review",
            approver_scope="named_role",
        )
    )

    findings = validate_authoring_document(document)

    assert any(
        finding["category"] == "approval_gate"
        and finding["severity"] == "blocking"
        and finding["field_path"] == "approval_gates[0].approver_role_code"
        for finding in findings
    )


def test_validate_authoring_document_rejects_secret_material_and_missing_refs(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.roles[0].allowed_tool_policy_refs = ("secret://prod-api-key",)
    document.subworkflow_refs.append(
        SubworkflowReference(
            alias="document-extraction",
            workflow_version_ref=str(uuid4()),
        )
    )

    findings = validate_authoring_document(document)

    assert any(
        finding["category"] == "skill_binding"
        and finding["severity"] == "blocking"
        and finding["field_path"] == "roles[0].allowed_tool_policy_refs"
        for finding in findings
    )
    assert any(
        finding["category"] == "subworkflow"
        and finding["severity"] == "blocking"
        and finding["field_path"] == "subworkflow_refs[0].workflow_version_ref"
        for finding in findings
    )


def test_validate_authoring_document_flags_missing_role_contracts_and_nodes(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.roles[0].input_contract_key = "missing-input"
    document.roles[0].output_contract_key = "missing-output"
    document.nodes.append(
        WorkflowNodeDefinition(
            node_key="missing-role-node",
            node_type="role",
            display_name="Missing Role",
            role_key="unknown-role",
        )
    )

    findings = validate_authoring_document(document)

    assert any(
        finding["field_path"] == "roles[0].input_contract_key" for finding in findings
    )
    assert any(
        finding["field_path"] == "roles[0].output_contract_key" for finding in findings
    )
    assert any(finding["field_path"] == "nodes[1].role_key" for finding in findings)


def test_validate_authoring_document_flags_invalid_join_and_approval_scopes(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.join_policies.append(
        JoinPolicyDefinition(
            join_policy_key="optional-quorum",
            strategy="first_success",
            quorum_count=1,
        )
    )
    document.approval_gates.append(
        ApprovalGateDefinition(
            approval_gate_key="bad-approval",
            display_name="Bad Approval",
            approver_scope="unknown-scope",
            decision_contract_key="missing-decision",
        )
    )

    findings = validate_authoring_document(document)

    assert any(
        finding["field_path"] == "join_policies[0].quorum_count" for finding in findings
    )
    assert any(
        finding["field_path"] == "approval_gates[0].approver_scope"
        for finding in findings
    )
    assert any(
        finding["field_path"] == "approval_gates[0].decision_contract_key"
        for finding in findings
    )


def test_validate_authoring_document_flags_breaking_contract_changes(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.contracts[0].json_schema = {
        "type": "array",
        "required": [],
        "properties": {"message": {"type": "integer"}},
    }

    findings = validate_authoring_document(
        document,
        previous_contract_schemas={
            "intake-request": {
                "type": "object",
                "required": ["message"],
                "properties": {"message": {"type": "string"}},
            }
        },
    )

    assert any(
        finding["field_path"] == "contracts[0].json_schema.type" for finding in findings
    )
    assert any(
        finding["field_path"] == "contracts[0].json_schema.required"
        for finding in findings
    )
    assert any(
        finding["field_path"] == "contracts[0].json_schema.properties.message.type"
        for finding in findings
    )
