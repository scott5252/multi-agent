from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupGroup,
    EditorLookupOption,
    EditorLookupResponse,
    ReferenceReadinessSnapshot,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument

EXACT_VERSION_BLOCKLIST = {"", "latest", "main", "dev"}


class ReferenceReadinessAdapter(Protocol):
    reference_type: str

    async def check(self, reference_key: str) -> ReferenceReadinessSnapshot:
        """Resolve one reference through its authoritative owner."""


def build_editor_lookup_response(
    document: WorkflowDraftDocument | None = None,
    *,
    lookup_kind: str | None = None,
    scope_type: str = "platform",
    tenant_id: str | None = None,
    search: str | None = None,
) -> EditorLookupResponse:
    groups = _lookup_groups(
        document=document,
        scope_type=scope_type,
        tenant_id=tenant_id,
    )
    if lookup_kind:
        groups = [group for group in groups if group.lookup_kind == lookup_kind]
    if search:
        lowered = search.lower()
        groups = [
            group.model_copy(
                update={
                    "options": [
                        option
                        for option in group.options
                        if lowered in option.label.lower()
                        or lowered in option.value.lower()
                    ]
                }
            )
            for group in groups
        ]
    return EditorLookupResponse(groups=groups)


def validate_reference_readiness(
    document: WorkflowDraftDocument,
    *,
    visible_subworkflow_version_ids: set[str] | None = None,
) -> tuple[
    list[ReferenceReadinessSnapshot], list[dict[str, object]], RequiredTestSummary
]:
    snapshots: list[ReferenceReadinessSnapshot] = []
    findings: list[dict[str, object]] = []
    visible_subworkflows = visible_subworkflow_version_ids or set()

    for index, reference in enumerate(document.prompt_profile_references):
        status = reference.readiness_status
        blocking = status not in {"ready", "active"}
        profile_url = (
            "/admin/prompt-runtime/profiles/resolve?agent_key="
            f"{reference.agent_key or ''}"
        )
        snapshots.append(
            ReferenceReadinessSnapshot(
                reference_type="prompt_profile",
                reference_key=reference.reference_key,
                status=status,
                blocking=blocking,
                detail_url=profile_url,
                safe_summary=(
                    f"Prompt/profile reference {reference.reference_key}: {status}"
                ),
                pin_payload={
                    "reference_key": reference.reference_key,
                    "agent_profile_version_id": str(reference.agent_profile_version_id)
                    if reference.agent_profile_version_id
                    else None,
                    "prompt_version_ids": [
                        str(value) for value in reference.prompt_version_ids
                    ],
                    "prompt_reference_version_ids": [
                        str(value) for value in reference.prompt_reference_version_ids
                    ],
                    "model_routing_preview": reference.model_routing_preview.model_dump(
                        mode="json"
                    )
                    if reference.model_routing_preview is not None
                    else None,
                },
            )
        )
        if blocking:
            findings.append(
                _blocking(
                    category="prompt_profile",
                    code="reference.prompt_profile.not_ready",
                    field_path=f"prompt_profile_references[{index}].readiness_status",
                    message="Prompt/profile reference is not publish-ready.",
                    remediation=(
                        "Select an active authorized profile and prompt versions."
                    ),
                    reference_type="prompt_profile",
                    reference_id=reference.reference_key,
                )
            )

    for index, skill in enumerate(document.skill_installations):
        status = (
            "ready"
            if _is_exact_version(skill.skill_version)
            and skill.credential_requirement_status
            not in {"missing", "failed", "secret_value_present"}
            else "blocked"
        )
        snapshots.append(
            ReferenceReadinessSnapshot(
                reference_type="skill",
                reference_key=skill.skill_installation_key,
                status=status,
                blocking=status != "ready",
                safe_summary=f"{skill.skill_slug}@{skill.skill_version}",
                pin_payload={
                    "skill_installation_key": skill.skill_installation_key,
                    "skill_slug": skill.skill_slug,
                    "skill_version": skill.skill_version,
                    "binding_mode": skill.binding_mode.value,
                    "tool_policy_refs": list(skill.tool_policy_refs),
                    "outbound_policy_refs": list(skill.outbound_policy_refs),
                    "secret_reference_ids": list(skill.secret_reference_ids),
                },
            )
        )
        if status != "ready":
            findings.append(
                _blocking(
                    category="skill",
                    code="reference.skill.not_ready",
                    field_path=f"skill_installations[{index}].skill_version",
                    message="Skill installation must pin an exact ready version.",
                    remediation=(
                        "Use an exact installed skill version and ready credentials."
                    ),
                    reference_type="skill",
                    reference_id=skill.skill_installation_key,
                )
            )

    for index, subworkflow in enumerate(document.subworkflow_refs):
        status = (
            "ready"
            if subworkflow.workflow_version_ref in visible_subworkflows
            else "blocked"
        )
        snapshots.append(
            ReferenceReadinessSnapshot(
                reference_type="subworkflow",
                reference_key=subworkflow.alias,
                status=status,
                blocking=status != "ready",
                detail_url=f"/admin/workflows/versions/{subworkflow.workflow_version_ref}/detail",
                safe_summary=f"Subworkflow {subworkflow.alias}: {status}",
                pin_payload={
                    "alias": subworkflow.alias,
                    "workflow_version_ref": subworkflow.workflow_version_ref,
                    "input_contract_key": subworkflow.input_contract_key,
                    "output_contract_key": subworkflow.output_contract_key,
                },
            )
        )
        if status != "ready":
            findings.append(
                _blocking(
                    category="subworkflow",
                    code="reference.subworkflow.not_visible",
                    field_path=f"subworkflow_refs[{index}].workflow_version_ref",
                    message="Subworkflow reference is missing or not visible.",
                    remediation="Choose an authorized published subworkflow bundle.",
                    reference_type="subworkflow",
                    reference_id=subworkflow.alias,
                )
            )

    test_summary = summarize_required_tests(
        result_statuses=(
            requirement.latest_result_status
            for requirement in document.test_requirements
        )
    )
    for index, requirement in enumerate(document.test_requirements):
        if requirement.latest_result_status not in {"passed", "passing"}:
            findings.append(
                _blocking(
                    category="required_test",
                    code="reference.required_test.not_passing",
                    field_path=f"test_requirements[{index}].latest_result_status",
                    message=(
                        "Required workflow test evidence is missing, stale, or failing."
                    ),
                    remediation=(
                        "Run the required suite and attach a passing current result."
                    ),
                    reference_type="test_suite",
                    reference_id=requirement.requirement_key,
                )
            )
    return snapshots, findings, test_summary


def summarize_required_tests(
    *,
    result_statuses: Iterable[str],
) -> RequiredTestSummary:
    statuses = [status.lower() for status in result_statuses]
    return RequiredTestSummary(
        required_count=len(statuses),
        passing_count=sum(1 for status in statuses if status in {"passed", "passing"}),
        failing_count=sum(1 for status in statuses if status in {"failed", "failing"}),
        missing_count=sum(1 for status in statuses if status == "missing"),
        stale_count=sum(1 for status in statuses if status == "stale"),
    )


def pin_summary_from_snapshots(
    snapshots: Iterable[ReferenceReadinessSnapshot],
) -> dict[str, object]:
    prompt_profile_pins: list[dict[str, object]] = []
    skill_installation_pins: list[dict[str, object]] = []
    subworkflow_bundle_pins: list[dict[str, object]] = []
    provider_catalog_pins: list[dict[str, object]] = []
    required_test_evidence: list[dict[str, object]] = []
    summary: dict[str, object] = {
        "prompt_profile_pins": prompt_profile_pins,
        "skill_installation_pins": skill_installation_pins,
        "subworkflow_bundle_pins": subworkflow_bundle_pins,
        "provider_catalog_pins": provider_catalog_pins,
        "required_test_evidence": required_test_evidence,
    }
    for snapshot in snapshots:
        if snapshot.reference_type == "prompt_profile":
            prompt_profile_pins.append(snapshot.pin_payload)
            preview = snapshot.pin_payload.get("model_routing_preview")
            if isinstance(preview, dict):
                provider_catalog_pins.append(dict(preview))
        elif snapshot.reference_type == "skill":
            skill_installation_pins.append(snapshot.pin_payload)
        elif snapshot.reference_type == "subworkflow":
            subworkflow_bundle_pins.append(snapshot.pin_payload)
        elif snapshot.reference_type == "test_suite":
            required_test_evidence.append(snapshot.pin_payload)
    return summary


def _lookup_groups(
    *,
    document: WorkflowDraftDocument | None,
    scope_type: str,
    tenant_id: str | None,
) -> list[EditorLookupGroup]:
    contracts = []
    roles = []
    subworkflows = []
    skills = []
    prompts = []
    tests = []
    if document is not None:
        contracts = [
            _option(
                lookup_kind="contracts",
                value=contract.contract_key,
                label=contract.display_name or contract.contract_key,
                scope_type=scope_type,
                tenant_id=tenant_id,
                status="available",
            )
            for contract in document.contracts
        ]
        roles = [
            _option(
                lookup_kind="approval_roles",
                value=role.role_key,
                label=role.display_name,
                scope_type=scope_type,
                tenant_id=tenant_id,
                status="available",
            )
            for role in document.roles
        ]
        subworkflows = [
            _option(
                lookup_kind="subworkflows",
                value=reference.workflow_version_ref,
                label=reference.display_name or reference.alias,
                scope_type=scope_type,
                tenant_id=tenant_id,
                status=reference.compatibility_status,
            )
            for reference in document.subworkflow_refs
        ]
        skills = [
            _option(
                lookup_kind="skills",
                value=skill.skill_installation_key,
                label=f"{skill.skill_slug}@{skill.skill_version}",
                scope_type=skill.scope_type.value,
                tenant_id=str(skill.tenant_id) if skill.tenant_id else tenant_id,
                status=skill.credential_requirement_status,
            )
            for skill in document.skill_installations
        ]
        prompts = [
            _option(
                lookup_kind="profiles",
                value=reference.reference_key,
                label=reference.agent_key or reference.reference_key,
                scope_type=scope_type,
                tenant_id=tenant_id,
                status=reference.readiness_status,
                detail_url=(
                    "/admin/prompt-runtime/profiles/resolve?agent_key="
                    f"{reference.agent_key or ''}"
                ),
            )
            for reference in document.prompt_profile_references
        ]
        tests = [
            _option(
                lookup_kind="test_suites",
                value=requirement.suite_id,
                label=requirement.requirement_key,
                scope_type=scope_type,
                tenant_id=tenant_id,
                status=requirement.latest_result_status,
            )
            for requirement in document.test_requirements
        ]
    return [
        EditorLookupGroup(
            lookup_kind="profiles", label="Runtime Profiles", options=prompts
        ),
        EditorLookupGroup(lookup_kind="prompts", label="Prompt Versions", options=[]),
        EditorLookupGroup(lookup_kind="model_routes", label="Model Routes", options=[]),
        EditorLookupGroup(
            lookup_kind="provider_catalog",
            label="Provider Catalog",
            options=[],
        ),
        EditorLookupGroup(lookup_kind="skills", label="Skills", options=skills),
        EditorLookupGroup(
            lookup_kind="subworkflows",
            label="Subworkflows",
            options=subworkflows,
        ),
        EditorLookupGroup(
            lookup_kind="contracts", label="Contracts", options=contracts
        ),
        EditorLookupGroup(
            lookup_kind="approval_roles",
            label="Approval Roles",
            options=roles,
        ),
        EditorLookupGroup(
            lookup_kind="test_suites",
            label="Required Tests",
            options=tests,
        ),
    ]


def _option(
    *,
    lookup_kind: str,
    value: str,
    label: str,
    scope_type: str,
    tenant_id: str | None,
    status: str,
    detail_url: str | None = None,
) -> EditorLookupOption:
    return EditorLookupOption(
        option_id=f"{lookup_kind}:{value}",
        lookup_kind=lookup_kind,
        value=value,
        label=label,
        scope_type=scope_type,
        tenant_id=tenant_id,
        status=status,
        detail_url=detail_url,
    )


def _is_exact_version(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in EXACT_VERSION_BLOCKLIST:
        return False
    return not any(marker in lowered for marker in ("*", ">", "<", "^", "~", ".x"))


def _blocking(
    *,
    category: str,
    code: str,
    field_path: str,
    message: str,
    remediation: str,
    reference_type: str,
    reference_id: str,
) -> dict[str, object]:
    return {
        "category": category,
        "severity": "blocking",
        "message": message,
        "field_path": field_path,
        "section_key": _section_for_field_path(field_path),
        "code": code,
        "remediation": remediation,
        "blocking": True,
        "reference_type": reference_type,
        "reference_id": reference_id,
    }


def _section_for_field_path(field_path: str) -> str:
    if field_path.startswith("prompt_profile_references"):
        return "prompt_profile_references"
    if field_path.startswith("skill_installations"):
        return "skills"
    if field_path.startswith("subworkflow_refs"):
        return "subworkflows"
    if field_path.startswith("test_requirements"):
        return "tests"
    return field_path.split("[", maxsplit=1)[0]
