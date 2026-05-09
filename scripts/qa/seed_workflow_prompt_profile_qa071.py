#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
)
from multi_agent_platform.db.models.agent_profiles import (
    ActiveAgentProfilePointer,
    AgentProfileDraft,
    AgentProfileDraftRevision,
    AgentProfileValidationResult,
    AgentProfileVersion,
    AgentRuntimeProfile,
    TenantProfileVersionGrant,
)
from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
    PromptValidationResult,
    PromptVersion,
    TenantPromptVersionGrant,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowKind,
    WorkflowLineage,
    WorkflowLineageStatus,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA071_LINEAGE_ID = UUID("71717171-1111-4671-8671-000000000071")
QA071_DRAFT_ID = UUID("71717171-6669-4671-8671-000000000071")
QA071_REVISION_ID = UUID("71717171-3333-4671-8671-000000000071")

QA071_PROMPT_LINEAGE_ID = UUID("71717171-1000-4671-8671-000000000071")
QA071_PROMPT_DRAFT_ID = UUID("71717171-1001-4671-8671-000000000071")
QA071_PROMPT_REVISION_ID = UUID("71717171-1002-4671-8671-000000000071")
QA071_PROMPT_VALIDATION_ID = UUID("71717171-1003-4671-8671-000000000071")
QA071_PROMPT_VERSION_ID = UUID("71717171-1004-4671-8671-000000000071")
QA071_PROMPT_GRANT_ID = UUID("71717171-1005-4671-8671-000000000071")

QA071_PROFILE_ID = UUID("71717171-2000-4671-8671-000000000071")
QA071_PROFILE_DRAFT_ID = UUID("71717171-2001-4671-8671-000000000071")
QA071_PROFILE_REVISION_ID = UUID("71717171-2002-4671-8671-000000000071")
QA071_PROFILE_VALIDATION_ID = UUID("71717171-2003-4671-8671-000000000071")
QA071_PROFILE_VERSION_ID = UUID("71717171-2004-4671-8671-000000000071")
QA071_PROFILE_POINTER_ID = UUID("71717171-2005-4671-8671-000000000071")
QA071_PROFILE_GRANT_ID = UUID("71717171-2006-4671-8671-000000000071")

SAVE_PAYLOAD_PATH = Path(".data/qa071-artifacts/workflow-prompt-profile-save.json")
PROMPT_TEMPLATE = (
    "Summarize the request with tenant-approved facts and return a safe routing "
    "recommendation."
)


def main() -> int:
    engine = create_engine(_database_url())
    document = _workflow_document()
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        principal = _upsert_principal(session)
        actor_id = str(principal.principal_identity_id)
        _upsert_prompt(session, actor_id)
        _upsert_profile(session, actor_id)
        _upsert_workflow(session, principal, document)
        session.commit()

    SAVE_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PAYLOAD_PATH.write_text(
        json.dumps(
            {
                "revision": "1",
                "idempotency_key": "qa071-workflow-prompt-profile-save",
                "name": "QA071 Prompt Profile Builder Updated",
                "description": "Saved through deterministic QA071 binding UI.",
                "change_summary": "QA071 prompt/profile binding save",
                "client_context": {
                    "active_section": "workflow-prompt-profiles",
                    "form_version": "workflow-prompt-profile-binding.v1",
                },
                "selected_prompt_ref": "coordinator-binding",
                "selected_profile_ref": "coordinator-binding",
                "join_policy": "wait_for_required_branches",
                "force_stale": False,
                "document": {
                    **document,
                    "display_name": "QA071 Prompt Profile Builder Updated",
                    "description": "Saved through deterministic QA071 binding UI.",
                    "roles": [
                        {
                            **document["roles"][0],
                            "prompt_reference_keys": ["coordinator-binding"],
                            "profile_reference_key": "coordinator-binding",
                        },
                        {
                            **document["roles"][1],
                            "prompt_reference_keys": ["coordinator-binding"],
                            "profile_reference_key": "coordinator-binding",
                        },
                        {
                            **document["roles"][2],
                            "prompt_reference_keys": [],
                            "profile_reference_key": None,
                        },
                    ],
                    "editor_annotations": {
                        **document["editor_annotations"],
                        "section_notes": {
                            "prompt-profiles": "QA071 prompt/profile save payload."
                        },
                    },
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA071 workflow prompt/profile binding draft")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={QA071_DRAFT_ID}")
    print(f"prompt_lineage_id={QA071_PROMPT_LINEAGE_ID}")
    print(f"prompt_version_id={QA071_PROMPT_VERSION_ID}")
    print(f"agent_runtime_profile_id={QA071_PROFILE_ID}")
    print(f"agent_profile_version_id={QA071_PROFILE_VERSION_ID}")
    print(f"save_payload={SAVE_PAYLOAD_PATH}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if value is None:
        value = _env_file_value("DATABASE_URL")
    if value is None:
        raise RuntimeError("DATABASE_URL is required for QA071 seed")
    return value.replace("sqlite+aiosqlite://", "sqlite://", 1)


def _env_file_value(key: str) -> str | None:
    env_path = Path(".env")
    if not env_path.exists():
        return None
    prefix = f"{key}="
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _upsert_tenant(
    session: Session,
    tenant_id: UUID,
    slug: str,
    display_name: str,
) -> None:
    tenant = session.get(Tenant, tenant_id)
    if tenant is None:
        tenant = Tenant(tenant_id=tenant_id)
        session.add(tenant)
    tenant.slug = slug
    tenant.display_name = display_name
    tenant.status = TenantStatus.ACTIVE


def _upsert_principal(session: Session) -> PrincipalIdentity:
    principal = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == "local|qa071-builder"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa071-builder",
        )
        session.add(principal)
    principal.display_name = "QA071 Builder"
    principal.email = "qa071.builder@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_prompt(session: Session, actor_id: str) -> None:
    lineage = session.get(PromptLineage, QA071_PROMPT_LINEAGE_ID)
    if lineage is None:
        lineage = PromptLineage(prompt_lineage_id=QA071_PROMPT_LINEAGE_ID)
        session.add(lineage)
    lineage.scope_type = "tenant"
    lineage.tenant_id = ACME_TENANT_ID
    lineage.slug = "qa071-safe-role-routing"
    lineage.display_name = "QA071 Safe Role Routing Prompt"
    lineage.purpose = "Published prompt used by workflow role binding QA."
    lineage.status = "active"
    lineage.latest_draft_id = QA071_PROMPT_DRAFT_ID
    lineage.latest_published_prompt_version_id = QA071_PROMPT_VERSION_ID
    lineage.created_by_principal_id = actor_id

    draft = session.get(PromptDraft, QA071_PROMPT_DRAFT_ID)
    if draft is None:
        draft = PromptDraft(prompt_draft_id=QA071_PROMPT_DRAFT_ID)
        session.add(draft)
    draft.prompt_lineage_id = QA071_PROMPT_LINEAGE_ID
    draft.scope_type = "tenant"
    draft.tenant_id = ACME_TENANT_ID
    draft.status = "active"
    draft.current_revision_number = 1
    draft.latest_revision_id = QA071_PROMPT_REVISION_ID
    draft.last_validation_result_id = QA071_PROMPT_VALIDATION_ID
    draft.created_by_principal_id = actor_id
    draft.last_edited_by_principal_id = actor_id

    template_hash = hashlib.sha256(PROMPT_TEMPLATE.encode("utf-8")).hexdigest()
    revision = session.get(PromptDraftRevision, QA071_PROMPT_REVISION_ID)
    if revision is None:
        revision = PromptDraftRevision(
            prompt_draft_revision_id=QA071_PROMPT_REVISION_ID
        )
        session.add(revision)
    revision.prompt_draft_id = QA071_PROMPT_DRAFT_ID
    revision.revision_number = 1
    revision.prompt_title = "QA071 safe role routing"
    revision.purpose = "Route workflow requests without revealing raw prompt content."
    revision.usage_notes = "Used by deterministic QA only."
    revision.template_content = PROMPT_TEMPLATE
    revision.template_content_sha256 = template_hash
    revision.variable_declarations_json = [
        {
            "name": "request_summary",
            "purpose": "Safe request summary",
            "required": True,
            "allowed_value_category": "safe_summary",
            "safety_classification": "non_sensitive",
            "sample_guidance": "Use a redacted request summary.",
            "display_order": 1,
        }
    ]
    revision.fixture_value_sets_json = [
        {
            "fixture_set_id": "default",
            "label": "Default safe fixture",
            "values_by_variable": {"request_summary": "Redacted request summary"},
        }
    ]
    revision.safe_summary_json = {
        "title": "QA071 safe role routing",
        "body": "Published prompt with one safe fixture.",
    }
    revision.created_by_principal_id = actor_id
    revision.created_at = datetime.now(UTC)

    validation = session.get(PromptValidationResult, QA071_PROMPT_VALIDATION_ID)
    if validation is None:
        validation = PromptValidationResult(
            prompt_validation_result_id=QA071_PROMPT_VALIDATION_ID
        )
        session.add(validation)
    validation.prompt_draft_revision_id = QA071_PROMPT_REVISION_ID
    validation.status = "passed"
    validation.blocking_issue_count = 0
    validation.advisory_issue_count = 0
    validation.findings_json = []
    validation.template_content_sha256 = template_hash
    validation.validated_fixture_set_ids = ["default"]
    validation.executed_by_principal_id = actor_id
    validation.executed_at = datetime.now(UTC)

    version = session.get(PromptVersion, QA071_PROMPT_VERSION_ID)
    if version is None:
        version = PromptVersion(prompt_version_id=QA071_PROMPT_VERSION_ID)
        session.add(version)
    version.prompt_lineage_id = QA071_PROMPT_LINEAGE_ID
    version.scope_type = "tenant"
    version.tenant_id = ACME_TENANT_ID
    version.version_sequence = 1
    version.display_version = "v1"
    version.status = "active"
    version.published_from_draft_id = QA071_PROMPT_DRAFT_ID
    version.published_from_revision_id = QA071_PROMPT_REVISION_ID
    version.validation_result_id = QA071_PROMPT_VALIDATION_ID
    version.template_content = PROMPT_TEMPLATE
    version.template_content_sha256 = template_hash
    version.variable_declarations_json = revision.variable_declarations_json
    version.purpose = revision.purpose
    version.usage_notes = revision.usage_notes
    version.safe_summary_json = revision.safe_summary_json
    version.published_by_principal_id = actor_id
    version.published_at = datetime.now(UTC)
    version.publication_reason = "QA071 deterministic seed."

    grant = session.get(TenantPromptVersionGrant, QA071_PROMPT_GRANT_ID)
    if grant is None:
        grant = TenantPromptVersionGrant(
            tenant_prompt_version_grant_id=QA071_PROMPT_GRANT_ID
        )
        session.add(grant)
    grant.prompt_version_id = QA071_PROMPT_VERSION_ID
    grant.grantee_tenant_id = ACME_TENANT_ID
    grant.status = "active"
    grant.granted_by_principal_id = actor_id
    grant.reason = "QA071 deterministic tenant grant."


def _upsert_profile(session: Session, actor_id: str) -> None:
    profile = session.get(AgentRuntimeProfile, QA071_PROFILE_ID)
    if profile is None:
        profile = AgentRuntimeProfile(agent_runtime_profile_id=QA071_PROFILE_ID)
        session.add(profile)
    profile.scope_type = "tenant"
    profile.tenant_id = ACME_TENANT_ID
    profile.agent_key = "coordinator"
    profile.agent_kind = "agent"
    profile.display_name = "QA071 Coordinator Runtime Profile"
    profile.purpose = "Active runtime profile used by workflow binding QA."
    profile.status = "active"
    profile.latest_draft_id = QA071_PROFILE_DRAFT_ID
    profile.active_profile_version_id = QA071_PROFILE_VERSION_ID
    profile.created_by_principal_id = actor_id

    draft = session.get(AgentProfileDraft, QA071_PROFILE_DRAFT_ID)
    if draft is None:
        draft = AgentProfileDraft(agent_profile_draft_id=QA071_PROFILE_DRAFT_ID)
        session.add(draft)
    draft.agent_runtime_profile_id = QA071_PROFILE_ID
    draft.scope_type = "tenant"
    draft.tenant_id = ACME_TENANT_ID
    draft.status = "active"
    draft.current_revision_number = 1
    draft.latest_revision_id = QA071_PROFILE_REVISION_ID
    draft.last_validation_result_id = QA071_PROFILE_VALIDATION_ID
    draft.created_by_principal_id = actor_id
    draft.last_edited_by_principal_id = actor_id

    profile_revision = session.get(AgentProfileDraftRevision, QA071_PROFILE_REVISION_ID)
    if profile_revision is None:
        profile_revision = AgentProfileDraftRevision(
            agent_profile_draft_revision_id=QA071_PROFILE_REVISION_ID
        )
        session.add(profile_revision)
    profile_revision.agent_profile_draft_id = QA071_PROFILE_DRAFT_ID
    profile_revision.revision_number = 1
    profile_revision.agent_key = "coordinator"
    profile_revision.agent_kind = "agent"
    profile_revision.purpose = "Coordinate QA071 prompt/profile binding."
    profile_revision.prompt_references_json = [
        {"prompt_version_id": str(QA071_PROMPT_VERSION_ID), "role": "primary"}
    ]
    profile_revision.model_routing_hints_json = {
        "model_route": "local-safe-model",
        "credential_expectation": "static-reference-only",
    }
    profile_revision.memory_scope_policy_json = {"scope": "workflow_run"}
    profile_revision.skill_requirements_json = []
    profile_revision.tool_policy_expectations_json = []
    profile_revision.output_contract_expectations_json = {"contract_key": "result"}
    profile_revision.test_suite_requirements_json = []
    profile_revision.safe_summary_json = {
        "title": "QA071 Coordinator Runtime Profile",
        "body": "Active profile with safe routing hints.",
    }
    profile_revision.created_by_principal_id = actor_id
    profile_revision.created_at = datetime.now(UTC)

    validation = session.get(AgentProfileValidationResult, QA071_PROFILE_VALIDATION_ID)
    if validation is None:
        validation = AgentProfileValidationResult(
            agent_profile_validation_result_id=QA071_PROFILE_VALIDATION_ID
        )
        session.add(validation)
    validation.agent_profile_draft_revision_id = QA071_PROFILE_REVISION_ID
    validation.status = "passed"
    validation.blocking_issue_count = 0
    validation.advisory_issue_count = 0
    validation.findings_json = []
    validation.referenced_prompt_version_ids = [str(QA071_PROMPT_VERSION_ID)]
    validation.referenced_model_routing_scope_ids = ["local-safe-model"]
    validation.referenced_memory_policy_hash = "qa071-memory-policy"
    validation.referenced_skill_requirement_hash = "qa071-skill-requirements"
    validation.executed_by_principal_id = actor_id
    validation.executed_at = datetime.now(UTC)

    version = session.get(AgentProfileVersion, QA071_PROFILE_VERSION_ID)
    if version is None:
        version = AgentProfileVersion(agent_profile_version_id=QA071_PROFILE_VERSION_ID)
        session.add(version)
    version.agent_runtime_profile_id = QA071_PROFILE_ID
    version.scope_type = "tenant"
    version.tenant_id = ACME_TENANT_ID
    version.agent_key = "coordinator"
    version.agent_kind = "agent"
    version.version_sequence = 1
    version.display_version = "v1"
    version.status = "active"
    version.activated_from_draft_id = QA071_PROFILE_DRAFT_ID
    version.activated_from_revision_id = QA071_PROFILE_REVISION_ID
    version.validation_result_id = QA071_PROFILE_VALIDATION_ID
    version.purpose = profile_revision.purpose
    version.prompt_references_json = profile_revision.prompt_references_json
    version.model_routing_hints_json = profile_revision.model_routing_hints_json
    version.memory_scope_policy_json = profile_revision.memory_scope_policy_json
    version.skill_requirements_json = profile_revision.skill_requirements_json
    version.tool_policy_expectations_json = (
        profile_revision.tool_policy_expectations_json
    )
    version.output_contract_expectations_json = (
        profile_revision.output_contract_expectations_json
    )
    version.test_suite_requirements_json = profile_revision.test_suite_requirements_json
    version.safe_summary_json = profile_revision.safe_summary_json
    version.activated_by_principal_id = actor_id
    version.activated_at = datetime.now(UTC)
    version.activation_reason = "QA071 deterministic seed."

    pointer = session.get(ActiveAgentProfilePointer, QA071_PROFILE_POINTER_ID)
    if pointer is None:
        pointer = ActiveAgentProfilePointer(
            active_agent_profile_pointer_id=QA071_PROFILE_POINTER_ID
        )
        session.add(pointer)
    pointer.scope_type = "tenant"
    pointer.tenant_id = ACME_TENANT_ID
    pointer.agent_kind = "agent"
    pointer.agent_key = "coordinator"
    pointer.active_profile_version_id = QA071_PROFILE_VERSION_ID
    pointer.activated_by_principal_id = actor_id
    pointer.activated_at = datetime.now(UTC)
    pointer.activation_reason = "QA071 deterministic seed."
    pointer.expected_previous_version_id = None

    grant = session.get(TenantProfileVersionGrant, QA071_PROFILE_GRANT_ID)
    if grant is None:
        grant = TenantProfileVersionGrant(
            tenant_profile_version_grant_id=QA071_PROFILE_GRANT_ID
        )
        session.add(grant)
    grant.agent_profile_version_id = QA071_PROFILE_VERSION_ID
    grant.grantee_tenant_id = ACME_TENANT_ID
    grant.status = "active"
    grant.granted_by_principal_id = actor_id
    grant.reason = "QA071 deterministic tenant grant."


def _upsert_workflow(
    session: Session,
    principal: PrincipalIdentity,
    document: dict[str, object],
) -> None:
    lineage = session.get(WorkflowLineage, QA071_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA071_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa071-prompt-profile-builder",
            display_name="QA071 Prompt Profile Builder",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.DRAFTING
    lineage.description = "Seed draft for prompt/profile binding QA."

    draft = session.get(WorkflowDraft, QA071_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA071_DRAFT_ID,
            workflow_lineage_id=QA071_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=principal.principal_identity_id,
            last_edited_by_principal_id=principal.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1

    revision = session.get(WorkflowDraftRevision, QA071_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA071_REVISION_ID,
            workflow_draft_id=QA071_DRAFT_ID,
            revision_number=1,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = document
    revision.document_sha256 = _digest(document)
    revision.change_summary = "QA071 seed workflow prompt/profile document."
    revision.created_at = datetime.now(UTC)
    session.flush()
    draft.latest_revision_id = QA071_REVISION_ID


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa071-prompt-profile-builder",
        "display_name": "QA071 Prompt Profile Builder",
        "description": "Seed draft for prompt/profile binding QA.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "start",
        "contracts": [
            {
                "contract_key": "request",
                "contract_kind": "workflow_input",
                "display_name": "Request",
                "json_schema": {"type": "object"},
            },
            {
                "contract_key": "result",
                "contract_kind": "workflow_output",
                "display_name": "Result",
                "json_schema": {"type": "object"},
            },
        ],
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "purpose": "Coordinate deterministic QA071 workflow setup.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["start"],
                "prompt_reference_keys": ["coordinator-binding"],
                "profile_reference_key": "coordinator-binding",
            },
            {
                "role_key": "research",
                "display_name": "Research agent",
                "purpose": "Prepare safe request context.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["research"],
                "prompt_reference_keys": ["coordinator-binding"],
                "profile_reference_key": None,
            },
            {
                "role_key": "review",
                "display_name": "Review agent",
                "purpose": "Review role binding readiness.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["review"],
                "prompt_reference_keys": [],
                "profile_reference_key": None,
            },
        ],
        "prompt_profile_references": [
            {
                "reference_key": "coordinator-binding",
                "role_key": "coordinator",
                "agent_key": "coordinator",
                "agent_kind": "agent",
                "agent_profile_version_id": str(QA071_PROFILE_VERSION_ID),
                "prompt_version_ids": [str(QA071_PROMPT_VERSION_ID)],
                "prompt_reference_version_ids": [],
                "source_scope": "tenant",
                "resolution_digest": "sha256:qa071-coordinator-binding",
                "model_routing_preview": {
                    "preview_key": "qa071-local-safe-model",
                    "scope": "tenant",
                    "model_id": "local-safe-model",
                    "health_state": "ready",
                    "policy_status": "allowed",
                    "evaluated_version_ids": [str(QA071_PROFILE_VERSION_ID)],
                    "safe_summary": "Local deterministic route with static references.",
                },
                "readiness_status": "ready",
            },
        ],
        "skill_installations": [],
        "nodes": [
            {
                "node_key": "start",
                "node_type": "role",
                "display_name": "Coordinator",
                "role_key": "coordinator",
            },
            {
                "node_key": "research",
                "node_type": "role",
                "display_name": "Research agent",
                "role_key": "research",
            },
            {
                "node_key": "review",
                "node_type": "role",
                "display_name": "Review agent",
                "role_key": "review",
            },
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "edge-start-research",
                "source_node_key": "start",
                "target_node_key": "research",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-research-review",
                "source_node_key": "research",
                "target_node_key": "review",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-review-done",
                "source_node_key": "review",
                "target_node_key": "done",
                "edge_type": "success",
            },
        ],
        "join_policies": [],
        "approval_gates": [],
        "subworkflow_refs": [],
        "test_requirements": [],
        "editor_annotations": {
            "section_notes": {},
            "graph_layout": {
                "start": {"x": 0, "y": 100},
                "research": {"x": 260, "y": 100},
                "review": {"x": 520, "y": 100},
                "done": {"x": 780, "y": 100},
            },
            "collapsed_sections": [],
        },
    }


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
