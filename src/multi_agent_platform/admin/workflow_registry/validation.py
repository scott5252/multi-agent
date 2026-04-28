from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import GatewayResult
from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins

EXACT_VERSION_BLOCKLIST = ("latest", "main", "dev")
SECRET_MARKERS = (
    "secret",
    "token",
    "password",
    "api-key",
    "api_key",
    "authorization",
    "credential",
    "delegated",
)
JOIN_STRATEGIES = {"all_success", "quorum", "first_success", "manual_resolution"}
APPROVER_SCOPES = {"tenant_admin", "platform_admin", "named_role"}


def validate_authoring_document(
    document: WorkflowDraftDocument,
    *,
    available_subworkflow_version_ids: set[str] | None = None,
    previous_contract_schemas: Mapping[str, object] | None = None,
    prompt_profile_findings: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    document = WorkflowDraftDocument.model_validate(document.model_dump(mode="json"))
    findings: list[dict[str, str]] = []
    contract_keys = {contract.contract_key for contract in document.contracts}
    role_keys = {role.role_key for role in document.roles}
    join_policy_keys = {
        join_policy.join_policy_key for join_policy in document.join_policies
    }
    approval_gate_keys = {
        approval_gate.approval_gate_key for approval_gate in document.approval_gates
    }
    subworkflow_aliases = {
        subworkflow_ref.alias for subworkflow_ref in document.subworkflow_refs
    }
    visible_subworkflow_ids = (
        available_subworkflow_version_ids
        if available_subworkflow_version_ids is not None
        else set()
    )

    if not document.roles:
        findings.append(
            {
                "category": "roles",
                "severity": "advisory",
                "message": "Draft has no roles yet; this is allowed during authoring.",
                "field_path": "roles",
            }
        )

    for index, role in enumerate(document.roles):
        if role.input_contract_key not in contract_keys:
            findings.append(
                _blocking(
                    category="compatibility",
                    field_path=f"roles[{index}].input_contract_key",
                    message="Role input contract must reference a defined contract.",
                )
            )
        if role.output_contract_key not in contract_keys:
            findings.append(
                _blocking(
                    category="compatibility",
                    field_path=f"roles[{index}].output_contract_key",
                    message="Role output contract must reference a defined contract.",
                )
            )
        if role.allowed_tool_policy_refs and any(
            _contains_secret_material(reference)
            for reference in role.allowed_tool_policy_refs
        ):
            findings.append(
                _blocking(
                    category="skill_binding",
                    field_path=f"roles[{index}].allowed_tool_policy_refs",
                    message=(
                        "Tool policy references cannot embed secrets "
                        "or delegated credentials."
                    ),
                )
            )
        for binding_index, binding in enumerate(role.skill_bindings):
            if not _is_exact_version(binding.skill_version):
                findings.append(
                    _blocking(
                        category="skill_binding",
                        field_path=(
                            f"roles[{index}].skill_bindings[{binding_index}]."
                            "skill_version"
                        ),
                        message=(
                            "Skill bindings must pin an exact published skill version."
                        ),
                    )
                )
            if any(
                _contains_secret_material(reference)
                for reference in binding.expected_runtime_refs
            ):
                findings.append(
                    _blocking(
                        category="skill_binding",
                        field_path=(
                            f"roles[{index}].skill_bindings[{binding_index}]."
                            "expected_runtime_refs"
                        ),
                        message=(
                            "Runtime refs cannot contain secret material "
                            "or delegated credentials."
                        ),
                    )
                )

    for index, node in enumerate(document.nodes):
        if node.node_type.value == "role" and node.role_key not in role_keys:
            findings.append(
                _blocking(
                    category="structure",
                    field_path=f"nodes[{index}].role_key",
                    message="Role nodes must reference a defined role.",
                )
            )
        if (
            node.node_type.value == "subworkflow"
            and node.subworkflow_alias not in subworkflow_aliases
        ):
            findings.append(
                _blocking(
                    category="subworkflow",
                    field_path=f"nodes[{index}].subworkflow_alias",
                    message=(
                        "Subworkflow nodes must reference a defined subworkflow alias."
                    ),
                )
            )
        if (
            node.node_type.value == "join"
            and node.join_policy_key not in join_policy_keys
        ):
            findings.append(
                _blocking(
                    category="join_policy",
                    field_path=f"nodes[{index}].join_policy_key",
                    message="Join nodes must reference a defined join policy.",
                )
            )
        if (
            node.node_type.value == "approval"
            and node.approval_gate_key not in approval_gate_keys
        ):
            findings.append(
                _blocking(
                    category="approval_gate",
                    field_path=f"nodes[{index}].approval_gate_key",
                    message="Approval nodes must reference a defined approval gate.",
                )
            )

    for index, reference in enumerate(document.subworkflow_refs):
        if reference.workflow_version_ref not in visible_subworkflow_ids:
            findings.append(
                _blocking(
                    category="subworkflow",
                    field_path=f"subworkflow_refs[{index}].workflow_version_ref",
                    message=(
                        "Subworkflow references must point to a visible "
                        "published version."
                    ),
                )
            )

    for index, join_policy in enumerate(document.join_policies):
        if join_policy.strategy not in JOIN_STRATEGIES:
            findings.append(
                _blocking(
                    category="join_policy",
                    field_path=f"join_policies[{index}].strategy",
                    message="Join policy strategy is not recognized.",
                )
            )
        if join_policy.strategy == "quorum":
            if join_policy.quorum_count is None or join_policy.quorum_count < 1:
                findings.append(
                    _blocking(
                        category="join_policy",
                        field_path=f"join_policies[{index}].quorum_count",
                        message="Quorum joins require a positive quorum count.",
                    )
                )
            elif join_policy.required_branches and (
                join_policy.quorum_count > len(join_policy.required_branches)
            ):
                findings.append(
                    _blocking(
                        category="join_policy",
                        field_path=f"join_policies[{index}].quorum_count",
                        message=(
                            "Quorum count cannot exceed the number of "
                            "required branches."
                        ),
                    )
                )
        elif join_policy.quorum_count is not None:
            findings.append(
                _blocking(
                    category="join_policy",
                    field_path=f"join_policies[{index}].quorum_count",
                    message="Only quorum joins can declare a quorum count.",
                )
            )

    for index, approval_gate in enumerate(document.approval_gates):
        if approval_gate.approver_scope not in APPROVER_SCOPES:
            findings.append(
                _blocking(
                    category="approval_gate",
                    field_path=f"approval_gates[{index}].approver_scope",
                    message=(
                        "Approval gate scope must be tenant_admin, "
                        "platform_admin, or named_role."
                    ),
                )
            )
        if (
            approval_gate.approver_scope == "named_role"
            and not approval_gate.approver_role_code
        ):
            findings.append(
                _blocking(
                    category="approval_gate",
                    field_path=f"approval_gates[{index}].approver_role_code",
                    message=(
                        "Named-role approval gates must declare the approver role code."
                    ),
                )
            )
        if (
            approval_gate.decision_contract_key is not None
            and approval_gate.decision_contract_key not in contract_keys
        ):
            findings.append(
                _blocking(
                    category="approval_gate",
                    field_path=f"approval_gates[{index}].decision_contract_key",
                    message=(
                        "Approval gates must reference a defined decision contract."
                    ),
                )
            )

    findings.extend(
        _validate_contract_compatibility(
            document=document,
            previous_contract_schemas=previous_contract_schemas or {},
        )
    )
    if prompt_profile_findings:
        findings.extend(prompt_profile_findings)
    return findings


async def execute_model_backed_validation(
    *,
    model_gateway: ModelGateway,
    connection_id: UUID,
    model_id: str,
    workflow_validation_id: UUID,
    tenant_id: UUID,
    trace_id: str,
    agent_key: str,
    agent_kind: str,
    agent_profile_version_id: UUID,
    prompt_version_ids: tuple[UUID, ...],
    prompt_reference_version_ids: tuple[UUID, ...],
    model_routing_provenance: dict[str, object],
) -> GatewayResult:
    context = build_gateway_context_from_pins(
        tenant_id=tenant_id,
        workflow_validation_id=workflow_validation_id,
        trace_id=trace_id,
        idempotency_key=f"workflow-validation:{workflow_validation_id}",
        agent_key=agent_key,
        agent_kind=agent_kind,
        agent_profile_version_id=agent_profile_version_id,
        prompt_version_ids=prompt_version_ids,
        prompt_reference_version_ids=prompt_reference_version_ids,
        model_routing_provenance=model_routing_provenance,
    )
    return await model_gateway.invoke(
        connection_id=connection_id,
        model_id=model_id,
        messages=(
            {"role": "system", "content": "Return safe workflow validation output."},
            {"role": "user", "content": "validate"},
        ),
        context=context,
    )


def _validate_contract_compatibility(
    *,
    document: WorkflowDraftDocument,
    previous_contract_schemas: Mapping[str, object],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    previous_by_key = {
        str(contract_key): schema
        for contract_key, schema in previous_contract_schemas.items()
    }
    for index, contract in enumerate(document.contracts):
        previous_schema = previous_by_key.get(contract.contract_key)
        if not isinstance(previous_schema, Mapping):
            continue
        previous_type = previous_schema.get("type")
        current_type = contract.json_schema.get("type")
        if previous_type and current_type and previous_type != current_type:
            findings.append(
                _blocking(
                    category="compatibility",
                    field_path=f"contracts[{index}].json_schema.type",
                    message="Contract type changes are breaking and block publish.",
                )
            )
        previous_required = set(_as_str_list(previous_schema.get("required")))
        current_required = set(_as_str_list(contract.json_schema.get("required")))
        missing_required = previous_required - current_required
        if missing_required:
            findings.append(
                _blocking(
                    category="compatibility",
                    field_path=f"contracts[{index}].json_schema.required",
                    message=(
                        "Removing previously required contract fields "
                        "is a breaking change."
                    ),
                )
            )
        previous_properties = previous_schema.get("properties")
        current_properties = contract.json_schema.get("properties")
        if isinstance(previous_properties, Mapping) and isinstance(
            current_properties, Mapping
        ):
            for property_name, previous_property in previous_properties.items():
                current_property = current_properties.get(property_name)
                if not isinstance(previous_property, Mapping) or not isinstance(
                    current_property, Mapping
                ):
                    continue
                previous_property_type = previous_property.get("type")
                current_property_type = current_property.get("type")
                if (
                    previous_property_type
                    and current_property_type
                    and previous_property_type != current_property_type
                ):
                    findings.append(
                        _blocking(
                            category="compatibility",
                            field_path=(
                                f"contracts[{index}].json_schema.properties."
                                f"{property_name}.type"
                            ),
                            message=(
                                "Changing a published contract field type "
                                "is a breaking change."
                            ),
                        )
                    )
    return findings


def _blocking(*, category: str, field_path: str, message: str) -> dict[str, str]:
    return {
        "category": category,
        "severity": "blocking",
        "message": message,
        "field_path": field_path,
    }


def _is_exact_version(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered or lowered in EXACT_VERSION_BLOCKLIST:
        return False
    return not any(
        marker in lowered for marker in ("*", ">", "<", "^", "~", " x", ".x")
    )


def _contains_secret_material(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in SECRET_MARKERS)


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return []
