from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
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
from multi_agent_platform.db.models.model_providers import (
    ConnectionTenantVisibility,
    ConnectionTestResult,
    ModelProviderConnection,
    ProviderModelDefinition,
)
from multi_agent_platform.db.models.model_skill_config import (
    AllowedToolPolicyVersion,
    ConfigurationAuditRecord,
    ModelProviderCatalogEntry,
    ModelRoutingVersion,
    ModelSkillConfigKind,
    ModelSkillProviderStatus,
    ModelSkillVersionStatus,
    PromptReferenceVersion,
    ResolvedExecutionConfiguration,
    RuntimeDecisionOutcome,
    RuntimePolicyDecision,
    SkillBindingVersion,
)
from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
    PromptValidationResult,
    PromptVersion,
    TenantPromptVersionGrant,
)
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderType,
    TestOutcome,
    VisibilityMode,
)
from tests.fixtures.agent_tests import seed_live_agent_test_bench_session
from tests.fixtures.channel_telegram_briefing import (
    seed_channel_telegram_briefing_live_data_sync,
)
from tests.fixtures.memberships import seed_membership_live_data_sync
from tests.fixtures.operations_workbench import seed_operations_workbench_live_data_sync
from tests.fixtures.skill_registry import seed_live_skill_lifecycle_session
from tests.fixtures.usage_react import seed_usage_react_live_data_sync


def _configure_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    database_path = tmp_path / "react-admin.db"
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0020_live_model_credentials')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"),
                Tenant(
                    tenant_id=other_tenant_id,
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    monkeypatch.setenv("COMMIT_SHA", "test-sha")
    monkeypatch.setenv("BUILD_TIME", "2026-05-04T00:00:00+00:00")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "skill-registry:install",
                        "skill-registry:bind",
                        "skill-execution:read",
                    ],
                },
                "tenant-user-acme": {
                    "catalog_key": "tenant-user-acme",
                    "display_name": "Tenant User",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user"],
                    "permission_codes": ["tenant:read"],
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "operations:read",
                        "admin:model-providers:write",
                        "skill-registry:publish",
                        "skill-execution:read",
                    ],
                },
                "auditor": {
                    "catalog_key": "auditor",
                    "display_name": "Auditor",
                    "role_codes": ["auditor"],
                    "permission_codes": ["operations:read"],
                },
            }
        ),
    )


def _seed_skill_lifecycle_records(
    tmp_path: Path, tenant_id: UUID
) -> dict[str, UUID | str]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        return seed_live_skill_lifecycle_session(session, tenant_id=tenant_id)


def _seed_agent_test_bench_records(
    tmp_path: Path, tenant_id: UUID
) -> dict[str, UUID | str]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        return seed_live_agent_test_bench_session(session, tenant_id=tenant_id)


def _seed_operations_workbench_records(
    tmp_path: Path,
    tenant_id: UUID,
) -> dict[str, UUID]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        ids = seed_operations_workbench_live_data_sync(session, tenant_id=tenant_id)
        session.commit()
        return ids


def _seed_membership_records(
    tmp_path: Path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> dict[str, UUID]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        return seed_membership_live_data_sync(
            session,
            tenant_id=tenant_id,
            other_tenant_id=other_tenant_id,
        )


def _seed_channel_telegram_briefing_records(
    tmp_path: Path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> dict[str, UUID]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        return seed_channel_telegram_briefing_live_data_sync(
            session,
            tenant_id=tenant_id,
            other_tenant_id=other_tenant_id,
        )


def _seed_usage_records(tmp_path: Path, tenant_id: UUID) -> dict[str, UUID]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        ids = seed_usage_react_live_data_sync(session, tenant_id=tenant_id)
        session.commit()
        return ids


def _seed_governance_records(tmp_path: Path, tenant_id: UUID) -> dict[str, UUID]:
    database_path = tmp_path / "react-admin.db"
    engine = create_engine(f"sqlite:///{database_path}")
    now = datetime(2026, 5, 7, 12, tzinfo=UTC)
    provider_id = uuid4()
    model_definition_id = uuid4()
    prompt_lineage_id = uuid4()
    prompt_draft_id = uuid4()
    prompt_revision_id = uuid4()
    prompt_validation_id = uuid4()
    prompt_version_id = uuid4()
    profile_id = uuid4()
    profile_draft_id = uuid4()
    profile_revision_id = uuid4()
    profile_validation_id = uuid4()
    profile_version_id = uuid4()
    principal_identity_id = uuid4()
    route_id = uuid4()
    prompt_reference_id = uuid4()
    skill_binding_id = uuid4()
    tool_policy_id = uuid4()
    run_id = uuid4()
    resolved_id = uuid4()
    template = "Summarized governance prompt"
    template_hash = hashlib.sha256(template.encode("utf-8")).hexdigest()

    with Session(engine) as session:
        session.add(
            PrincipalIdentity(
                principal_identity_id=principal_identity_id,
                auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
                external_subject="local|governance-seed",
                display_name="Governance Seed",
            )
        )
        session.add(
            ModelProviderConnection(
                provider_connection_id=provider_id,
                provider_type=ProviderType.OPENAI,
                display_name="Governance provider",
                base_url_safe=None,
                timeout_policy={},
                visibility_mode=VisibilityMode.TENANT_ALLOWLIST,
                active=True,
                health_state=HealthState.HEALTHY,
                credential_secret_reference_ids=["secret-ref-governance-provider"],
                safe_metadata={},
                allowlist_decision_hash="allowlist-hash",
                created_by_principal_id="platform-admin",
                updated_by_principal_id="platform-admin",
            )
        )
        session.add(
            ProviderModelDefinition(
                provider_model_definition_id=model_definition_id,
                provider_connection_id=provider_id,
                model_id="governance-safe-model",
                display_name="Governance safe model",
                capability_metadata={},
                cost_metadata={},
                default_parameters={},
                available=True,
            )
        )
        session.add(
            ConnectionTenantVisibility(
                provider_connection_id=provider_id,
                tenant_id=tenant_id,
                visible=True,
                created_by_principal_id="platform-admin",
            )
        )
        session.add(
            ConnectionTestResult(
                provider_connection_id=provider_id,
                provider_model_definition_id=model_definition_id,
                actor_principal_id="platform-admin",
                source="admin_user",
                started_at=now,
                completed_at=now,
                latency_ms=120,
                outcome=TestOutcome.SUCCESS,
                normalized_reason=ErrorCategory.NONE,
                tested_model_id="governance-safe-model",
                safe_diagnostic_summary="Provider health check has safe metadata.",
                safe_provider_request_id=None,
                http_status_class="2xx",
                timeout_policy={},
            )
        )

        session.add(
            PromptLineage(
                prompt_lineage_id=prompt_lineage_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                slug="governance-prompt",
                display_name="Governance prompt",
                purpose="Governance summary prompt.",
                status="active",
                latest_draft_id=prompt_draft_id,
                latest_published_prompt_version_id=prompt_version_id,
                created_by_principal_id="tenant-admin",
            )
        )
        session.add(
            PromptDraft(
                prompt_draft_id=prompt_draft_id,
                prompt_lineage_id=prompt_lineage_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                status="active",
                current_revision_number=2,
                latest_revision_id=prompt_revision_id,
                last_validation_result_id=prompt_validation_id,
                created_by_principal_id="tenant-admin",
                last_edited_by_principal_id="tenant-admin",
            )
        )
        session.add(
            PromptDraftRevision(
                prompt_draft_revision_id=prompt_revision_id,
                prompt_draft_id=prompt_draft_id,
                revision_number=2,
                prompt_title="Governance prompt",
                purpose="Governance summary prompt.",
                usage_notes="Safe usage notes.",
                template_content=template,
                template_content_sha256=template_hash,
                variable_declarations_json=[{"name": "topic"}],
                fixture_value_sets_json=[{"fixture_set_id": "safe-summary"}],
                safe_summary_json={
                    "summary": "Prompt draft contains safe summary metadata."
                },
                created_by_principal_id="tenant-admin",
            )
        )
        session.add(
            PromptValidationResult(
                prompt_validation_result_id=prompt_validation_id,
                prompt_draft_revision_id=prompt_revision_id,
                rule_set_version="prompt-runtime-v1",
                status="passed",
                blocking_issue_count=0,
                advisory_issue_count=0,
                findings_json=[],
                template_content_sha256=template_hash,
                validated_fixture_set_ids=["safe-summary"],
                executed_by_principal_id="tenant-admin",
            )
        )
        session.add(
            PromptVersion(
                prompt_version_id=prompt_version_id,
                prompt_lineage_id=prompt_lineage_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                version_sequence=1,
                display_version="v1",
                status="active",
                published_from_draft_id=prompt_draft_id,
                published_from_revision_id=prompt_revision_id,
                validation_result_id=prompt_validation_id,
                template_content=template,
                template_content_sha256=template_hash,
                variable_declarations_json=[{"name": "topic"}],
                purpose="Governance summary prompt.",
                usage_notes="Safe usage notes.",
                safe_summary_json={"summary": "Published prompt version available."},
                published_by_principal_id="tenant-admin",
                publication_reason="Seeded safe governance evidence.",
            )
        )
        session.add(
            TenantPromptVersionGrant(
                prompt_version_id=prompt_version_id,
                grantee_tenant_id=tenant_id,
                status="active",
                granted_by_principal_id="tenant-admin",
                reason="Tenant owns this prompt.",
            )
        )

        session.add(
            AgentRuntimeProfile(
                agent_runtime_profile_id=profile_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                agent_key="governance",
                agent_kind="workflow",
                display_name="Governance runtime profile",
                purpose="Governance profile.",
                status="active",
                latest_draft_id=profile_draft_id,
                active_profile_version_id=profile_version_id,
                created_by_principal_id="tenant-admin",
            )
        )
        session.add(
            AgentProfileDraft(
                agent_profile_draft_id=profile_draft_id,
                agent_runtime_profile_id=profile_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                status="active",
                current_revision_number=2,
                latest_revision_id=profile_revision_id,
                last_validation_result_id=profile_validation_id,
                created_by_principal_id="tenant-admin",
                last_edited_by_principal_id="tenant-admin",
            )
        )
        profile_prompt_refs = [{"prompt_version_id": str(prompt_version_id)}]
        profile_routes = {
            "model_id": "governance-safe-model",
            "provider_key": str(provider_id),
        }
        profile_skills = [{"skill_slug": "read-only-governance-tool"}]
        session.add(
            AgentProfileDraftRevision(
                agent_profile_draft_revision_id=profile_revision_id,
                agent_profile_draft_id=profile_draft_id,
                revision_number=2,
                agent_key="governance",
                agent_kind="workflow",
                purpose="Governance profile.",
                prompt_references_json=profile_prompt_refs,
                model_routing_hints_json=profile_routes,
                memory_scope_policy_json={},
                skill_requirements_json=profile_skills,
                tool_policy_expectations_json=[],
                output_contract_expectations_json={},
                test_suite_requirements_json=[],
                safe_summary_json={"summary": "Profile summary is safe."},
                created_by_principal_id="tenant-admin",
            )
        )
        session.add(
            AgentProfileValidationResult(
                agent_profile_validation_result_id=profile_validation_id,
                agent_profile_draft_revision_id=profile_revision_id,
                rule_set_version="profile-runtime-v1",
                status="passed",
                blocking_issue_count=0,
                advisory_issue_count=0,
                findings_json=[],
                referenced_prompt_version_ids=[str(prompt_version_id)],
                referenced_model_routing_scope_ids=[],
                referenced_memory_policy_hash=None,
                referenced_skill_requirement_hash=None,
                executed_by_principal_id="tenant-admin",
            )
        )
        session.add(
            AgentProfileVersion(
                agent_profile_version_id=profile_version_id,
                agent_runtime_profile_id=profile_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                agent_key="governance",
                agent_kind="workflow",
                version_sequence=1,
                display_version="v1",
                status="active",
                activated_from_draft_id=profile_draft_id,
                activated_from_revision_id=profile_revision_id,
                validation_result_id=profile_validation_id,
                purpose="Governance profile.",
                prompt_references_json=profile_prompt_refs,
                model_routing_hints_json=profile_routes,
                memory_scope_policy_json={},
                skill_requirements_json=profile_skills,
                tool_policy_expectations_json=[],
                output_contract_expectations_json={},
                test_suite_requirements_json=[],
                safe_summary_json={"summary": "Profile version is safe."},
                activated_by_principal_id="tenant-admin",
                activation_reason="Seeded safe governance evidence.",
            )
        )
        session.add(
            TenantProfileVersionGrant(
                agent_profile_version_id=profile_version_id,
                grantee_tenant_id=tenant_id,
                status="active",
                granted_by_principal_id="tenant-admin",
                reason="Tenant owns this profile.",
            )
        )
        session.add(
            ActiveAgentProfilePointer(
                scope_type="tenant",
                tenant_id=tenant_id,
                agent_kind="workflow",
                agent_key="governance",
                active_profile_version_id=profile_version_id,
                activated_by_principal_id="tenant-admin",
                activation_reason="Seeded safe governance evidence.",
            )
        )

        session.add(
            ModelProviderCatalogEntry(
                model_provider_entry_id=uuid4(),
                tenant_id=tenant_id,
                provider_key=str(provider_id),
                model_id="governance-safe-model",
                display_name="Governance safe model",
                capabilities={},
                cost_metadata={},
                status=ModelSkillProviderStatus.ACTIVE,
                provider_connection_id=provider_id,
                provider_model_definition_id=model_definition_id,
                health_state="healthy",
                availability_status="available",
                visibility_mode="tenant_allowlist",
                tenant_visibility_hash="visible",
                last_synced_at=now,
                gateway_governed=True,
            )
        )
        model_entry_id = (
            session.query(ModelProviderCatalogEntry).one().model_provider_entry_id
        )
        session.add(
            ModelRoutingVersion(
                model_routing_version_id=route_id,
                tenant_id=tenant_id,
                scope_type="tenant",
                scope_hash="tenant-governance",
                model_provider_entry_id=model_entry_id,
                routing_parameters={},
                status=ModelSkillVersionStatus.ACTIVE,
                version_sequence=1,
                created_by_principal_id=principal_identity_id,
                activation_reason="Seeded safe governance evidence.",
                effective_from=now,
                redacted_summary={"summary": "Model route active."},
            )
        )
        session.add(
            PromptReferenceVersion(
                prompt_reference_version_id=prompt_reference_id,
                tenant_id=tenant_id,
                scope_type="tenant",
                scope_hash="tenant-governance",
                prompt_id=prompt_lineage_id,
                prompt_version_id=prompt_version_id,
                prompt_digest="prompt-digest",
                status=ModelSkillVersionStatus.ACTIVE,
                version_sequence=1,
                created_by_principal_id=principal_identity_id,
                activation_reason="Seeded safe governance evidence.",
                redacted_summary={"summary": "Prompt reference active."},
            )
        )
        session.add(
            SkillBindingVersion(
                skill_binding_version_id=skill_binding_id,
                tenant_id=tenant_id,
                scope_hash="tenant-governance",
                skill_slug="read-only-governance-tool",
                skill_version="v1",
                allowed_contexts=["governance"],
                runtime_ref_constraints={},
                status=ModelSkillVersionStatus.ACTIVE,
                version_sequence=1,
                created_by_principal_id=principal_identity_id,
                activation_reason="Seeded safe governance evidence.",
                redacted_summary={"summary": "Skill binding active."},
            )
        )
        session.add(
            AllowedToolPolicyVersion(
                allowed_tool_policy_version_id=tool_policy_id,
                tenant_id=tenant_id,
                scope_hash="tenant-governance",
                skill_slug="read-only-governance-tool",
                tool_id="governance-tool",
                allowed_action_categories=["read"],
                constraints={},
                status=ModelSkillVersionStatus.ACTIVE,
                version_sequence=1,
                created_by_principal_id=principal_identity_id,
                activation_reason="Seeded safe governance evidence.",
                redacted_summary={"summary": "Tool policy active."},
            )
        )
        session.add(
            ConfigurationAuditRecord(
                tenant_id=tenant_id,
                actor_principal_id=principal_identity_id,
                actor_role="Platform Admin",
                action="credential_reference_reviewed",
                config_kind=ModelSkillConfigKind.MODEL_ROUTING,
                affected_scope={"scope": "tenant-governance"},
                new_version_id=route_id,
                reason="Seeded safe governance evidence.",
                redacted_diff_summary={
                    "summary": "Credential reference metadata was reviewed."
                },
            )
        )
        session.add(
            ResolvedExecutionConfiguration(
                resolved_execution_configuration_id=resolved_id,
                tenant_id=tenant_id,
                workflow_run_id=run_id,
                run_bundle_id=uuid4(),
                bundle_digest="bundle-digest",
                workflow_version_bundle_id=uuid4(),
                accepted_at=now,
                resolved_by_principal_id=principal_identity_id,
                model_routing_version_ids=[str(route_id)],
                prompt_reference_version_ids=[str(prompt_reference_id)],
                skill_binding_version_ids=[str(skill_binding_id)],
                allowed_tool_policy_version_ids=[str(tool_policy_id)],
                outbound_domain_policy_version_ids=[],
                secret_reference_version_ids=[str(uuid4())],
                credential_requirement_version_ids=[],
                resolution_digest="abcdef1234567890",
                trace_id="trace-governance-seed",
                redacted_summary={"summary": "Run configuration resolved."},
            )
        )
        session.add(
            RuntimePolicyDecision(
                tenant_id=tenant_id,
                workflow_run_id=run_id,
                run_bundle_id=uuid4(),
                agent_key="governance",
                decision_category="tool",
                requested_resource="governance-tool",
                requested_action="read",
                outcome=RuntimeDecisionOutcome.ALLOW,
                safe_reason="Read-only governance tool allowed.",
                evaluated_version_ids=[str(tool_policy_id)],
                winning_version_ids=[str(tool_policy_id)],
                source_scopes=["tenant"],
                idempotency_key="governance-seed",
                trace_id="trace-governance-seed",
                redacted_metadata={},
            )
        )
        session.commit()

    return {
        "provider_id": provider_id,
        "prompt_lineage_id": prompt_lineage_id,
        "profile_id": profile_id,
        "run_id": run_id,
    }


def _workflow_document(slug: str, display_name: str) -> dict[str, object]:
    return {
        "workflow_key": slug,
        "display_name": display_name,
        "description": "Exercise the admin workflow live-data routes.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "triage-node",
        "roles": [
            {
                "role_key": "triage-role",
                "display_name": "Triage Role",
                "purpose": "Assess the incoming request.",
                "input_contract_key": "intake-request",
                "output_contract_key": "triage-result",
                "skill_bindings": [
                    {
                        "binding_key": "triage-skill",
                        "skill_slug": "triage-agent",
                        "skill_version": "2026.04.1",
                        "purpose": "Perform triage.",
                    }
                ],
            }
        ],
        "contracts": [
            {"contract_key": "intake-request", "json_schema": {"type": "object"}},
            {"contract_key": "triage-result", "json_schema": {"type": "object"}},
        ],
        "nodes": [
            {
                "node_key": "triage-node",
                "node_type": "role",
                "display_name": "Triage",
                "role_key": "triage-role",
            }
        ],
        "edges": [],
        "join_policies": [],
        "approval_gates": [],
        "subworkflow_refs": [],
    }


def _create_react_workflow_draft(
    client: TestClient,
    *,
    tenant_id: UUID,
    slug: str = "admin-live-flow",
) -> dict[str, object]:
    display_name = "Admin Live Flow"
    created = client.post(
        f"/admin/app/workflows?tenant_id={tenant_id}",
        headers={"X-Local-Principal": "tenant-admin-acme"},
        json={
            "idempotency_key": f"create-{slug}",
            "scope_type": "tenant",
            "tenant_id": str(tenant_id),
            "workflow_kind": "main_workflow",
            "slug": slug,
            "display_name": display_name,
            "description": "Created through the admin live-data route.",
            "created_from_version_id": None,
            "document": _workflow_document(slug, display_name),
        },
    )
    assert created.status_code == 201
    return created.json()


def test_local_principal_react_admin_entry_and_bootstrap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bootstrap = client.get(
            f"/admin/app/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert "Admin" in html.text
    assert "data-bootstrap-url" in html.text
    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["principal"]["auth_mode"] == "local_principal"
    assert payload["active_scope"]["tenant_id"] == str(tenant_id)
    assert payload["active_scope"]["label"] == "Acme"
    assert payload["feature_flags"]["react_admin_enabled"] is True
    assert payload["version"]["api_version"] == "admin-shell-2026-05"
    nav_by_area = {
        item["admin_area"]: item
        for group in payload["navigation"]
        for item in group["items"]
    }
    workflow_nav = nav_by_area["workflows"]
    assert workflow_nav["href"] == f"/admin/app/workflows?tenant_id={tenant_id}"
    assert workflow_nav["fallback_kind"] == "react"
    assert nav_by_area["skill_registry"]["href"] == (
        f"/admin/app/skills?tenant_id={tenant_id}"
    )
    assert nav_by_area["skill_registry_installations"]["href"] == (
        f"/admin/app/skills/installations?tenant_id={tenant_id}"
    )
    assert nav_by_area["skill_execution"]["href"] == (
        f"/admin/app/skills/diagnostics?tenant_id={tenant_id}"
    )
    assert nav_by_area["telegram_configuration"]["href"] == (
        f"/admin/app/channels?panel=telegram&tenant_id={tenant_id}"
    )
    assert nav_by_area["briefing_preferences"]["href"] == (
        f"/admin/app/channels?panel=briefing&tenant_id={tenant_id}"
    )
    assert nav_by_area["prompt_library"]["label"] == "Prompt Library"
    assert any(group["label"] == "Prompt Runtime" for group in payload["navigation"])
    assert payload["shell"]["product_name"] == "Multi-Agent Admin"
    assert payload["shell"]["breadcrumbs"][0]["label"] == "Admin"
    assert payload["shell"]["command_results"]
    assert "token_subject" not in json.dumps(payload)
    assert "raw-jti" not in json.dumps(payload)


def test_auth0_backed_principal_summary_uses_existing_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-reviewer",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-react",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(f"/admin/app/bootstrap.json?tenant_id={tenant_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["principal"]["auth_mode"] == "auth0"
    assert payload["principal"]["principal_id"] == "auth0-reviewer"
    assert payload["shell"]["design_token_version"] == "admin-shell-2026-05"
    assert "auth0|hidden" not in json.dumps(payload)


def test_react_admin_search_metadata_is_authorized_and_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_operations_workbench_records(tmp_path, tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-reviewer",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-search",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        tenant_search = client.get(
            f"/admin/app/search.json?tenant_id={tenant_id}&q=workflow",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/search.json")
        cross_tenant = client.get(
            f"/admin/app/search.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert tenant_search.status_code == 200
    payload = tenant_search.json()
    assert payload["query"] == "workflow"
    assert payload["results"]
    assert all("href" in result for result in payload["results"])
    assert "auth0|hidden" not in json.dumps(payload)
    assert missing.status_code == 401
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_search = client.get(
                f"/admin/app/search.json?tenant_id={tenant_id}&q=workflow"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_search.status_code == 200
    assert auth0_search.json()["results"]


def test_react_admin_patterns_routes_are_retired_and_omitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_operations_workbench_records(tmp_path, tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-patterns",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-patterns",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        retired_json = client.get(
            f"/admin/app/patterns.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        retired_html = client.get(
            f"/admin/app/patterns?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        retired_action = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"sample_name": "Preview"},
        )
        retired_export = client.post(
            f"/admin/app/patterns/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bootstrap = client.get(
            f"/admin/app/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        search = client.get(
            f"/admin/app/search.json?tenant_id={tenant_id}&q=patterns",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/patterns.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert retired_json.status_code == 404
    assert retired_html.status_code == 404
    assert retired_action.status_code in {404, 405}
    assert retired_export.status_code in {404, 405}
    assert cross_tenant.status_code == 404
    assert bootstrap.status_code == 200
    assert search.status_code == 200
    assert "/admin/app/patterns" not in json.dumps(bootstrap.json())
    assert "/admin/app/patterns" not in json.dumps(search.json())
    assert "react-admin-patterns" not in json.dumps(bootstrap.json())
    assert "react-admin-patterns" not in json.dumps(search.json())

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(f"/admin/app/patterns.json?tenant_id={tenant_id}")
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 404


def test_react_admin_operations_workbench_platform_and_tenant_views_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_operations_workbench_records(tmp_path, tenant_id)
    app = create_app()

    async def auth0_platform_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-platform",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            role_codes=("platform_admin",),
            permission_codes=("operations:read",),
            trace_id="trace-auth0-workbench",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/operations.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        auditor = client.get(
            "/admin/app/operations.json",
            headers={"X-Local-Principal": "auditor"},
        )
        tenant = client.get(
            f"/admin/app/operations.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/operations.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            "/admin/app/operations",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert platform.status_code == 200
    payload = platform.json()
    assert payload["page_id"] == "react-operations-workbench"
    assert payload["scope"]["scope_type"] == "platform"
    assert payload["time_range"]["preset"] == "60m"
    assert payload["refresh"]["interval_seconds"] == 30
    assert "Generated from live evidence" in payload["generated_at_label"]
    assert "Gateway attempt recorded retryable timeout category." in json.dumps(payload)
    assert "Provider health" not in json.dumps(payload)
    assert "qa029-secret-value" not in json.dumps(payload)
    assert "qa029" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert auditor.status_code == 200
    assert tenant.status_code == 200
    tenant_payload = tenant.json()
    assert tenant_payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Tenant live evidence" in json.dumps(tenant_payload)
    assert "Model Providers" not in json.dumps(tenant_payload)
    assert "OpenAI provider" not in json.dumps(tenant_payload)
    assert "gpt-qa057-live" not in json.dumps(tenant_payload)
    assert "/admin/app/governance/providers" not in json.dumps(tenant_payload)
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text
    assert html.status_code == 200
    assert "Admin" in html.text

    app.dependency_overrides[require_authorized_principal] = auth0_platform_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get("/admin/app/operations.json")
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["scope_type"] == "platform"


def test_react_admin_operations_workbench_filters_run_debug_and_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    ids = _seed_operations_workbench_records(tmp_path, tenant_id)
    app = create_app()
    run_id = str(ids["run_id"])

    with TestClient(app) as client:
        filtered = client.get(
            "/admin/app/operations.json?severity=critical&subsystem=gateway",
            headers={"X-Local-Principal": "platform-admin"},
        )
        bad_range = client.get(
            "/admin/app/operations.json?range=24h",
            headers={"X-Local-Principal": "platform-admin"},
        )
        bad_subsystem = client.get(
            "/admin/app/operations.json?subsystem=provider_payload",
            headers={"X-Local-Principal": "platform-admin"},
        )
        run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        platform_run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        cross_run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_export = client.post("/admin/app/operations/export")
        export = client.post(
            "/admin/app/operations/export",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "active",
                "range": "60m",
                "include_run_debug": True,
            },
        )
        tenant_export = client.post(
            f"/admin/app/operations/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"scope_type": "active", "range": "60m"},
        )
        cross_export = client.post(
            f"/admin/app/operations/export?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"scope_type": "active", "range": "60m"},
        )

    assert filtered.status_code == 200
    assert filtered.json()["logs"][0]["subsystem"] == "gateway"
    assert bad_range.status_code == 400
    assert bad_range.json()["detail"]["field_errors"][0]["field"] == "range"
    assert "24h" not in bad_range.text
    assert bad_subsystem.status_code == 400
    assert "provider_payload" not in bad_subsystem.text
    assert run_debug.status_code == 200
    debug_payload = run_debug.json()
    assert debug_payload["workflow_run_id"] == run_id
    assert debug_payload["branches"]
    assert debug_payload["gateway_attempts"][0]["credential_diagnostic_category"]
    assert debug_payload["tool_calls"][0]["policy_outcome"] == "allowed_read_only"
    assert (
        debug_payload["deliveries"][0]["failure_category"] == "telegram-retry-scheduled"
    )
    assert "OpenAI provider" not in json.dumps(debug_payload)
    assert "gpt-qa057-live" not in json.dumps(debug_payload)
    assert "/admin/app/governance/providers" not in json.dumps(debug_payload)
    assert platform_run_debug.status_code == 200
    assert platform_run_debug.json()["tenant_scope"] is None
    assert cross_run_debug.status_code == 403
    assert "Globex" not in cross_run_debug.text
    assert missing_export.status_code == 401
    assert export.status_code == 200
    export_payload = export.json()
    assert export_payload["status"] == "complete"
    assert export_payload["artifact_reference_id"].startswith("operations-export:")
    assert "/Users/" not in json.dumps(export_payload)
    assert "qa029" not in json.dumps(export_payload).lower()
    assert tenant_export.status_code == 200
    assert tenant_export.json()["artifact_reference_id"].startswith(
        "operations-export:"
    )
    assert cross_export.status_code == 403
    assert "Globex" not in cross_export.text


def test_react_admin_workflow_builder_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-workflow-builder",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-workflow-builder",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/workflows/builder.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        lookups = client.get(
            f"/admin/app/workflows/lookups.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        registry = client.get(
            f"/admin/app/workflows/registry.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        create_state = client.get(
            f"/admin/app/workflows/create.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        legacy_routes = client.get(
            f"/admin/app/workflows/legacy-routes.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        create_html = client.get(
            f"/admin/app/workflows/new?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/workflows/builder.json")
        denied = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    assert platform.json()["scope"]["scope_type"] == "platform"
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["page_id"] == "react-workflow-builder"
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["draft"] is None
    assert payload["state"]["state"] == "empty"
    assert payload["empty_state"]["title"] == "No active workflow draft"
    assert "qa030-secret-value" not in json.dumps(payload)
    assert "raw prompt" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert lookups.status_code == 200
    assert lookups.json()["prompt_options"] == []
    assert registry.status_code == 200
    assert registry.json()["items"] == []
    assert registry.json()["empty_state"]["title"] == "No workflows found"
    assert create_state.status_code == 200
    assert create_state.json()["create_action"]["method"] == "post"
    assert legacy_routes.status_code == 200
    assert legacy_routes.json()[0]["legacy_path"] == "/admin/workflows/ui"
    assert html.status_code == 200
    assert "Admin" in html.text
    assert create_html.status_code == 200
    assert "Admin" in create_html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/workflows/builder.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert auth0_page.json()["draft"] is None
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_workflow_builder_save_validate_and_publish_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}

    with TestClient(app) as client:
        created = _create_react_workflow_draft(client, tenant_id=tenant_id)
        draft_href = created["next_action"]["href"]
        draft_id = draft_href.split("/drafts/", maxsplit=1)[1].split("?", maxsplit=1)[0]
        current_revision = created["revision"]
        detail = client.get(
            f"/admin/app/workflows/drafts/{draft_id}/detail.json?tenant_id={tenant_id}",
            headers=headers,
        )
        initial_gate = client.get(
            f"/admin/app/workflows/drafts/{draft_id}/publish-gate.json?tenant_id={tenant_id}",
            headers=headers,
        )
        copied = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/copy?tenant_id={tenant_id}",
            headers=headers,
            json={
                "idempotency_key": "copy-key",
                "source_revision_number": None,
                "new_slug": "admin-live-flow-copy",
                "display_name": "Admin Live Flow Copy",
                "description": "Copied through the admin live-data route.",
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "change_summary": "Admin workflow copy",
            },
        )
        save_payload = {
            "description": "Updated through the admin live-data save route.",
            "idempotency_key": "save-key",
            "join_policy": "wait_for_required_branches",
            "name": "Admin Live Flow Updated",
            "revision": current_revision,
            "selected_profile_ref": None,
            "selected_prompt_ref": None,
        }
        accepted = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/save?tenant_id={tenant_id}",
            headers=headers,
            json=save_payload,
        )
        stale = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/save?tenant_id={tenant_id}",
            headers=headers,
            json={**save_payload, "force_stale": True, "idempotency_key": "stale"},
        )
        saved_revision = str(int(current_revision) + 1)
        restored = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/restore?tenant_id={tenant_id}",
            headers=headers,
            json={
                "idempotency_key": "restore-key",
                "revision_number": int(current_revision),
                "base_revision_number": int(saved_revision),
                "change_summary": "Restore for admin route coverage",
            },
        )
        active_revision = restored.json()["revision"]
        stale_restore = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/restore?tenant_id={tenant_id}",
            headers=headers,
            json={
                "idempotency_key": "restore-stale",
                "revision_number": int(current_revision),
                "base_revision_number": int(current_revision),
                "change_summary": "Stale restore",
            },
        )
        blocked_validation = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/validate?tenant_id={tenant_id}",
            headers=headers,
        )
        ready_validation = client.post(
            (
                f"/admin/app/workflows/drafts/{draft_id}/validate"
                f"?tenant_id={tenant_id}&ready=true"
            ),
            headers=headers,
        )
        blocked_publish = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": False,
                "idempotency_key": "publish-blocked",
                "ready_fixture": False,
                "revision": active_revision,
            },
        )
        confirmation = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": False,
                "idempotency_key": "publish-confirm",
                "ready_fixture": True,
                "revision": active_revision,
            },
        )
        published = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": True,
                "idempotency_key": "publish-accepted",
                "ready_fixture": True,
                "revision": active_revision,
            },
        )
        version_id = published.json()["audit_reference_id"].split("workflow-version:")[
            1
        ]
        version_detail = client.get(
            f"/admin/app/workflows/versions/{version_id}/detail.json?tenant_id={tenant_id}",
            headers=headers,
        )
        cross_publish = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={other_tenant_id}",
            headers=headers,
            json={
                "confirmed": True,
                "idempotency_key": "publish-cross",
                "ready_fixture": True,
                "revision": current_revision,
            },
        )

    assert accepted.status_code == 200
    assert detail.status_code == 200
    assert detail.json()["draft"]["workflow_draft_id"] == draft_id
    assert initial_gate.status_code == 200
    assert initial_gate.json()["revision"] == current_revision
    assert copied.status_code == 201
    assert copied.json()["status"] == "accepted"
    assert accepted.json()["status"] == "accepted"
    assert accepted.json()["revision"] == saved_revision
    assert stale.json()["status"] == "stale_conflict"
    assert stale.json()["stale_conflict"]["submitted_revision"] == current_revision
    assert restored.json()["status"] == "accepted"
    assert stale_restore.json()["status"] == "stale_conflict"
    assert blocked_validation.json()["validation"]["revision"] == active_revision
    assert ready_validation.json()["publish_readiness"]["revision"] == active_revision
    assert blocked_publish.json()["status"] in {
        "confirmation_required",
        "validation_error",
    }
    assert confirmation.json()["status"] == "confirmation_required"
    assert published.json()["status"] == "accepted"
    assert published.json()["publish_readiness"]["published_bundle_summary"]
    assert version_detail.status_code == 200
    assert version_detail.json()["workflow_version_bundle_id"] == version_id
    assert cross_publish.status_code == 403
    assert "Globex" not in cross_publish.text


def test_react_admin_governance_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-governance",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-governance",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/governance/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        providers = client.get(
            f"/admin/app/governance/providers.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/governance?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/governance/bootstrap.json")
        denied = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    platform_payload = platform.json()
    assert platform_payload["page_id"] == "react-governance"
    assert platform_payload["scope"]["scope_type"] == "platform"
    assert platform_payload["providers"] == []
    assert platform_payload["empty_state"]["reason"] == "no_live_rows"
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["providers"] == []
    assert payload["prompts"] == []
    assert payload["routing_preview"] is None
    assert payload["run_provenance"] == []
    assert payload["empty_state"]["summary"]
    assert "qa031-secret-value" not in json.dumps(payload)
    assert "raw prompt" not in json.dumps(payload).lower()
    assert "raw completion" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert providers.status_code == 200
    assert providers.json()["providers"] == []
    assert providers.json()["empty_state"]["reason"] == "no_live_rows"
    assert html.status_code == 200
    assert "Admin" in html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert auth0_page.json()["empty_state"]["reason"] == "no_live_rows"
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_governance_actions_are_safe_and_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    ids = _seed_governance_records(tmp_path, tenant_id)
    app = create_app()
    tenant_headers = {"X-Local-Principal": "tenant-admin-acme"}
    platform_headers = {"X-Local-Principal": "platform-admin"}

    with TestClient(app) as client:
        bootstrap = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        probe = client.post(
            f"/admin/app/governance/providers/{ids['provider_id']}/probe",
            headers=platform_headers,
        )
        tenant_probe = client.post(
            f"/admin/app/governance/providers/{ids['provider_id']}/probe",
            headers=tenant_headers,
        )
        credential_reference = client.post(
            f"/admin/app/governance/providers/{ids['provider_id']}/credential-reference",
            headers=platform_headers,
            json={
                "credential_reference_id": "secret-ref-governance-next",
                "revision": "provider-rev-current",
            },
        )
        prompt_save = client.post(
            f"/admin/app/governance/prompts/{ids['prompt_lineage_id']}/save?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "prompt-save",
                "publish": False,
                "revision": "draft r2",
                "safe_summary": "Review safe prompt summary.",
            },
        )
        prompt_preview = client.post(
            f"/admin/app/governance/prompts/{ids['prompt_lineage_id']}/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={"fixture_id": "redaction-check"},
        )
        profile_save = client.post(
            f"/admin/app/governance/profiles/{ids['profile_id']}/save?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "profile-save",
                "model_binding": "governance-safe-model-v2",
                "provider_binding": str(ids["provider_id"]),
                "revision": "draft r2",
            },
        )
        profile_resolve = client.post(
            f"/admin/app/governance/profiles/{ids['profile_id']}/resolve?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        routing = client.post(
            f"/admin/app/governance/routing/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "profile_id": str(ids["profile_id"]),
                "skill_id": "read-only-governance-tool",
                "workflow_context": "Governance workflow",
            },
        )
        history = client.get(
            f"/admin/app/governance/history.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        provenance = client.get(
            f"/admin/app/governance/provenance/{ids['run_id']}.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        cross_history = client.get(
            f"/admin/app/governance/history.json?tenant_id={other_tenant_id}",
            headers=tenant_headers,
        )

    assert bootstrap.status_code == 200
    bootstrap_payload = bootstrap.json()
    assert bootstrap_payload["providers"][0]["display_name"] == "Governance provider"
    assert bootstrap_payload["prompts"][0]["name"] == "Governance prompt"
    assert bootstrap_payload["profiles"][0]["name"] == "Governance runtime profile"
    assert bootstrap_payload["routing_preview"]["direct_call_guardrail"]
    assert bootstrap_payload["run_provenance"] == []
    assert probe.status_code == 200
    assert probe.json()["probe"]["credential_resolution_status"] == "safe metadata only"
    assert "raw provider" not in probe.text.lower()
    assert tenant_probe.status_code == 403
    assert tenant_probe.json()["detail"] in {
        "insufficient_permission",
        "platform_admin_required",
    }
    assert credential_reference.status_code == 200
    assert credential_reference.json()["status"] == "accepted"
    assert "resolved credential" not in credential_reference.text.lower()
    assert prompt_save.json()["status"] == "accepted"
    assert prompt_preview.json()["status"] == "summarized"
    assert "raw prompt" not in prompt_preview.text.lower()
    assert "raw completion" not in prompt_preview.text.lower()
    assert profile_save.json()["status"] == "accepted"
    assert profile_resolve.json()["status"] == "ready"
    assert routing.json()["routing_preview"]["direct_call_guardrail"]
    assert "No live providers were invoked." in routing.text
    assert history.json()["history"][0]["audit_reference_id"]
    assert provenance.json()["credential_reference_evidence"]
    assert cross_history.status_code == 403
    assert "Globex" not in cross_history.text


def test_react_admin_skill_lifecycle_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        empty_tenant = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert empty_tenant.status_code == 200
    empty_payload = empty_tenant.json()
    assert empty_payload["empty_state"]["reason"] == "no_live_rows"
    assert empty_payload["tenant_discovery"]["available_versions"] == []
    assert empty_payload["installations"] == []
    assert empty_payload["skill_execution_diagnostics"] == []

    _seed_skill_lifecycle_records(tmp_path, tenant_id)

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-skills",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=(
                "tenant:read",
                "tenant:admin",
                "skill-registry:install",
                "skill-registry:bind",
                "skill-execution:read",
            ),
            trace_id="trace-auth0-skills",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/skills/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        discovery = client.get(
            f"/admin/app/skills/discovery.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        diagnostics = client.get(
            f"/admin/app/skills/diagnostics.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        legacy_routes = client.get(
            f"/admin/app/skills/legacy-routes.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/skills?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/skills/bootstrap.json")
        denied = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    platform_payload = platform.json()
    assert platform_payload["page_id"] == "react-skill-lifecycle"
    assert platform_payload["scope"]["scope_type"] == "platform"
    assert (
        platform_payload["platform_publication"]["package_versions"][0]["package_slug"]
        == "calendar-assistant"
    )
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["platform_publication"] is None
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["tenant_discovery"]["grants"][0]["tenant_label"] == "Acme"
    assert payload["connector_diagnostics"][0]["connector_label"] == "Calendar"
    assert payload["binding_preview"]["blocked_tools"]
    assert payload["audit_timeline"][0]["audit_reference_id"]
    assert "qa032-secret-value" not in json.dumps(payload)
    assert "raw manifest" not in json.dumps(payload).lower()
    assert "resolved credential" not in json.dumps(payload).lower()
    assert "authorization header" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert discovery.status_code == 200
    assert discovery.json()["discovery"]["available_versions"]
    assert diagnostics.status_code == 200
    assert (
        diagnostics.json()["diagnostics"][0]["gateway_decision"] == "allowed_read_only"
    )
    assert legacy_routes.status_code == 200
    assert legacy_routes.json()[0]["legacy_path"] == (
        "/admin/skill-registry/ui/packages"
    )
    assert legacy_routes.json()[-1]["react_path"] == "/admin/app/skills/diagnostics"
    assert html.status_code == 200
    assert "Admin" in html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_skill_lifecycle_actions_are_safe_and_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    ids = _seed_skill_lifecycle_records(tmp_path, tenant_id)
    app = create_app()
    tenant_headers = {"X-Local-Principal": "tenant-admin-acme"}
    platform_headers = {"X-Local-Principal": "platform-admin"}
    installation_id = str(ids["installation_id"])
    version_id = str(ids["version_id"])
    reference_id = str(ids["secret_reference_id"])

    with TestClient(app) as client:
        candidate = client.post(
            "/admin/app/skills/packages/candidates",
            headers=platform_headers,
            json={
                "candidate_revision": None,
                "idempotency_key": "candidate",
                "manifest_text": "unsafe sample text with qa032-secret-value",
                "uploaded_fixture_id": "qa032-uploaded-manifest",
            },
        )
        tenant_candidate = client.post(
            "/admin/app/skills/packages/candidates",
            headers=tenant_headers,
            json={
                "idempotency_key": "candidate",
                "manifest_text": "safe fixture",
                "uploaded_fixture_id": None,
            },
        )
        blocked_validation = client.post(
            "/admin/app/skills/packages/candidates/no-active-candidate/validate?ready=false",
            headers=platform_headers,
        )
        confirmation = client.post(
            "/admin/app/skills/packages/candidates/no-active-candidate/publish",
            headers=platform_headers,
            json={
                "candidate_revision": "candidate-unavailable",
                "confirmed": False,
                "idempotency_key": "publish-confirm",
            },
        )
        published = client.post(
            "/admin/app/skills/packages/candidates/no-active-candidate/publish",
            headers=platform_headers,
            json={
                "candidate_revision": "candidate-unavailable",
                "confirmed": True,
                "idempotency_key": "publish",
            },
        )
        grant = client.post(
            f"/admin/app/skills/packages/{version_id}/grants",
            headers=platform_headers,
            json={
                "grant_enabled": True,
                "idempotency_key": "grant",
                "revision": version_id,
                "tenant_id": str(tenant_id),
                "version_id": version_id,
            },
        )
        credential = client.post(
            f"/admin/app/skills/installations/{installation_id}/credentials?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "credential",
                "revision": ids["revision"],
                "selected_reference_id": reference_id,
            },
        )
        current_revision = credential.json()["revision"]
        bad_credential = client.post(
            f"/admin/app/skills/installations/{installation_id}/credentials?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "credential-bad",
                "revision": current_revision,
                "selected_reference_id": "other-tenant-reference",
            },
        )
        smoke = client.post(
            f"/admin/app/skills/installations/{installation_id}/smoke-tests?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "smoke",
                "revision": current_revision,
            },
        )
        install = client.post(
            f"/admin/app/skills/installations/{installation_id}/install?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "install",
                "package_id": "calendar-assistant",
                "revision": smoke.json()["revision"],
                "upgrade": False,
                "version_id": version_id,
            },
        )
        stale_install = client.post(
            f"/admin/app/skills/installations/{installation_id}/install?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "install-stale",
                "package_id": "calendar-assistant",
                "revision": "stale-revision",
                "upgrade": False,
                "version_id": version_id,
            },
        )
        binding = client.post(
            f"/admin/app/skills/installations/{installation_id}/eligibility/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "package_id": installation_id,
                "profile_id": "profile-calendar-runtime",
                "workflow_context": "Calendar workflow",
            },
        )
        diagnostic = client.post(
            f"/admin/app/skills/diagnostics/run?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        quarantine = client.post(
            f"/admin/app/skills/packages/{version_id}/quarantine",
            headers=platform_headers,
        )
        audit = client.get(
            f"/admin/app/skills/audit.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        cross_audit = client.get(
            f"/admin/app/skills/audit.json?tenant_id={other_tenant_id}",
            headers=tenant_headers,
        )

    assert candidate.status_code == 200
    assert candidate.json()["status"] == "accepted"
    assert "qa032-secret-value" not in candidate.text
    assert "uploaded fixture metadata took precedence" in candidate.text.lower()
    assert tenant_candidate.status_code == 403
    assert blocked_validation.json()["status"] == "validation_error"
    assert confirmation.json()["status"] == "confirmation_required"
    assert published.json()["publication"]["lifecycle_status"] == "published"
    assert grant.json()["status"] == "accepted"
    assert quarantine.json()["publication"]["lifecycle_status"] == "quarantined"
    assert install.json()["installation"]["credential_readiness"] == "ready"
    assert stale_install.json()["status"] == "stale_conflict"
    assert credential.json()["credential"]["fingerprint"].startswith("fp_")
    assert "resolved credential" not in credential.text.lower()
    assert bad_credential.json()["status"] == "validation_error"
    assert smoke.json()["smoke_test"]["readiness"] == "queued"
    assert "calendar.write" in binding.json()["binding_preview"]["blocked_tools"]
    assert "No tools" in binding.text
    assert diagnostic.json()["diagnostic"]["gateway_decision"] == "queued"
    assert "connector request" not in diagnostic.text.lower()
    assert audit.json()["audit_timeline"][0]["audit_reference_id"]
    assert cross_audit.status_code == 403
    assert "Globex" not in cross_audit.text


def test_react_admin_test_bench_routes_are_safe_and_dual_auth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    ids = _seed_agent_test_bench_records(tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            f"/admin/app/test-bench?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bootstrap = client.get(
            f"/admin/app/test-bench/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        suites = client.get(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        suite_detail = client.get(
            f"/admin/app/test-bench/suites/{ids['suite_id']}?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        runs = client.get(
            f"/admin/app/test-bench/runs.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        run_detail = client.get(
            "/admin/app/test-bench/runs/"
            f"{ids['failed_run_id']}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        gates = client.get(
            f"/admin/app/test-bench/gates.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        artifact = client.get(
            "/admin/app/test-bench/artifacts/"
            f"{ids['artifact_id']}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        audit = client.get(
            f"/admin/app/test-bench/audit.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/test-bench/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_suites = client.get(
            f"/admin/app/test-bench/suites?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_suite_detail = client.get(
            f"/admin/app/test-bench/suites/{ids['suite_id']}"
            f"?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_runs = client.get(
            f"/admin/app/test-bench/runs.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_run_detail = client.get(
            "/admin/app/test-bench/runs/"
            f"{ids['failed_run_id']}.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_gates = client.get(
            f"/admin/app/test-bench/gates.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_artifact = client.get(
            "/admin/app/test-bench/artifacts/"
            f"{ids['artifact_id']}.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_audit = client.get(
            f"/admin/app/test-bench/audit.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_suite = client.get(
            f"/admin/app/test-bench/suites/{uuid4()}?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        invalid_suite = client.get(
            f"/admin/app/test-bench/suites/not-a-uuid?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_run = client.get(
            f"/admin/app/test-bench/runs/{uuid4()}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_artifact = client.get(
            f"/admin/app/test-bench/artifacts/{uuid4()}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["title"] == "Test Bench"
    assert payload["selected_suite"]["summary"]["default_safe_mode"] == "mock_model"
    assert payload["selected_suite"]["summary"]["suite_id"] == str(ids["suite_id"])
    assert payload["gate_alerts"][0]["evidence_status"] == "passed"
    assert suites.status_code == 200
    assert suites.json()["form_metadata"]["default_pass_threshold"] == 0.9
    assert suite_detail.status_code == 200
    assert suite_detail.json()["summary"]["suite_id"] == str(ids["suite_id"])
    assert runs.status_code == 200
    assert runs.json()["runs"][0]["suite_id"] == str(ids["suite_id"])
    assert run_detail.status_code == 200
    assert run_detail.json()["summary"]["status"] == "failed"
    assert run_detail.json()["assertion_diagnostics"][0]["category"] == (
        "failed_assertion"
    )
    assert gates.status_code == 200
    assert {gate["evidence_status"] for gate in gates.json()["gates"]} == {"passed"}
    assert artifact.status_code == 200
    assert artifact.json()["authorized_href"].endswith(".json")
    assert audit.status_code == 200
    assert audit.json()["audit_timeline"][0]["tenant_scope_label"] == "Acme"
    assert cross_tenant.status_code == 403
    assert cross_suites.status_code == 403
    assert cross_suite_detail.status_code == 403
    assert cross_runs.status_code == 403
    assert cross_run_detail.status_code == 403
    assert cross_gates.status_code == 403
    assert cross_artifact.status_code == 403
    assert cross_audit.status_code == 403
    assert missing_suite.status_code == 404
    assert invalid_suite.status_code == 404
    assert missing_run.status_code == 404
    assert missing_artifact.status_code == 404
    assert "Globex" not in cross_tenant.text

    serialized = json.dumps(payload).lower()
    assert "qa033-secret-value" not in serialized
    assert "raw prompt" not in serialized
    assert "raw completion" not in serialized
    assert "connector request" not in serialized
    assert "storage path" not in serialized

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-test-bench-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-test-bench",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_bootstrap = client.get(
                f"/admin/app/test-bench/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_bootstrap.status_code == 200
    assert auth0_bootstrap.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in json.dumps(auth0_bootstrap.json())


def test_react_admin_test_bench_mutations_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    ids = _seed_agent_test_bench_records(tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        suite_save = client.post(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Live daily briefing release gate",
                "target_type": "workflow_draft",
                "target_id": ids["target_id"],
                "target_revision": ids["current_revision"],
                "default_safe_mode": "mock_model",
                "pass_threshold": 0.95,
                "required_for_publish": True,
                "revision": "2",
                "idempotency_key": "suite-save-route",
            },
        )
        stale_suite = client.post(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Live daily briefing release gate",
                "target_type": "workflow_draft",
                "target_id": ids["target_id"],
                "target_revision": ids["current_revision"],
                "default_safe_mode": "mock_model",
                "pass_threshold": 0.95,
                "required_for_publish": True,
                "revision": "1",
                "idempotency_key": "suite-save-route",
            },
        )
        case_save = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/cases"
            f"?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Briefing summary contract",
                "fixture_summary": "Fixture includes weather metadata summary.",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "evaluator_reference_id": "evaluator-live-safe-summary",
                "revision": "3",
                "idempotency_key": "case-save-route",
            },
        )
        launch = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/runs"
            f"?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "safe_mode": "real_model_side_effects_disabled",
                "run_reason": "Release confidence",
                "idempotency_key": "run-launch-route",
            },
        )
        probe_denied = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/runs"
            f"?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "safe_mode": "approved_real_probe",
                "run_reason": "Release confidence",
                "idempotency_key": "run-probe-route",
            },
        )
        gate_refresh = client.post(
            f"/admin/app/test-bench/gates/gate-{ids['suite_id']}/refresh"
            f"?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "idempotency_key": "gate-refresh-route",
            },
        )
        unsafe_fixture = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/cases"
            f"?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Unsafe case",
                "fixture_summary": "raw prompt copied into browser",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "revision": "3",
                "idempotency_key": "unsafe-case-route",
            },
        )
        missing_case_suite = client.post(
            f"/admin/app/test-bench/suites/{uuid4()}/cases?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Missing suite case",
                "fixture_summary": "Safe fixture summary.",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "idempotency_key": "missing-case-suite-route",
            },
        )
        missing_run_suite = client.post(
            f"/admin/app/test-bench/suites/{uuid4()}/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "safe_mode": "mock_model",
                "run_reason": "Release confidence",
                "idempotency_key": "missing-run-suite-route",
            },
        )
        cross_suite_save = client.post(
            f"/admin/app/test-bench/suites?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Cross tenant suite",
                "target_type": "workflow_draft",
                "target_id": ids["target_id"],
                "target_revision": ids["current_revision"],
                "default_safe_mode": "mock_model",
                "pass_threshold": 0.95,
                "required_for_publish": True,
                "idempotency_key": "cross-suite-save-route",
            },
        )
        cross_case_save = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/cases"
            f"?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Cross tenant case",
                "fixture_summary": "Safe fixture summary.",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "idempotency_key": "cross-case-save-route",
            },
        )
        cross_run_launch = client.post(
            f"/admin/app/test-bench/suites/{ids['suite_id']}/runs"
            f"?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "safe_mode": "mock_model",
                "run_reason": "Release confidence",
                "idempotency_key": "cross-run-launch-route",
            },
        )
        cross_gate_refresh = client.post(
            f"/admin/app/test-bench/gates/gate-{ids['suite_id']}/refresh"
            f"?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": ids["current_revision"],
                "idempotency_key": "cross-gate-refresh-route",
            },
        )

    assert suite_save.status_code == 200
    assert suite_save.json()["status"] == "accepted"
    assert stale_suite.status_code == 200
    assert stale_suite.json()["status"] == "stale_conflict"
    assert case_save.status_code == 200
    assert case_save.json()["case"]["case_revision"] == "4"
    assert launch.status_code == 200
    assert launch.json()["run"]["progress"]["status"] == "failed"
    assert probe_denied.status_code == 200
    assert probe_denied.json()["status"] == "validation_error"
    assert gate_refresh.status_code == 200
    assert gate_refresh.json()["gate"]["evidence_status"] == "failed"
    assert unsafe_fixture.status_code == 422
    assert missing_case_suite.status_code == 404
    assert missing_run_suite.status_code == 404
    assert cross_suite_save.status_code == 403
    assert cross_case_save.status_code == 403
    assert cross_run_launch.status_code == 403
    assert cross_gate_refresh.status_code == 403


def test_react_admin_memberships_platform_and_tenant_flows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    seed_ids = _seed_membership_records(tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            "/admin/app/memberships",
            headers={"X-Local-Principal": "platform-admin"},
        )
        platform_bootstrap = client.get(
            "/admin/app/memberships/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_bootstrap = client.get(
            f"/admin/app/memberships/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        invite_replay = client.post(
            f"/admin/app/memberships/invitations?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "email": "invited.user@example.test",
                "requested_roles": ["tenant_user"],
                "tenant_id": str(tenant_id),
                "idempotency_key": "qa054-live-invite",
            },
        )
        platform_role_denied = client.post(
            f"/admin/app/memberships/role-grants?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "confirmed": True,
                "idempotency_key": "role-grant-ui-qa054",
                "principal_identity_id": str(seed_ids["tenant_principal_id"]),
                "role_code": "platform_admin",
                "scope_type": "platform",
            },
        )
        principal_link_denied = client.post(
            f"/admin/app/memberships/principals/link?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "display_name": "Linked Reviewer",
                "email": "linked@example.test",
                "external_subject": "auth0|safe-subject-7788",
                "idempotency_key": "principal-link-ui-qa054",
            },
        )
        access_history = client.get(
            f"/admin/app/memberships/access-history.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        audit = client.get(
            f"/admin/app/memberships/audit.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/memberships/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert platform_bootstrap.status_code == 200
    assert platform_bootstrap.json()["title"] == "Membership Administration"
    assert "Support override evidence is persisted" in json.dumps(
        platform_bootstrap.json()
    )
    assert tenant_bootstrap.status_code == 200
    tenant_payload = tenant_bootstrap.json()
    serialized_tenant = json.dumps(tenant_payload)
    assert "Globex" not in serialized_tenant
    assert "platform_admin" not in serialized_tenant
    assert tenant_payload["directory"][0]["raw_identifier_detail"] is None
    assert invite_replay.status_code == 200
    assert invite_replay.json()["status"] == "replayed"
    assert invite_replay.json()["invitation"]["masked_email"] == "in***r@e***.test"
    assert platform_role_denied.status_code == 200
    assert platform_role_denied.json()["status"] == "validation_error"
    assert principal_link_denied.status_code == 200
    assert principal_link_denied.json()["status"] == "validation_error"
    assert access_history.status_code == 200
    assert access_history.json()["records"][0]["decision"] == "allow"
    assert audit.status_code == 200
    assert audit.json()["records"][0]["redaction_class"] == "safe-summary"
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    serialized = json.dumps(platform_bootstrap.json()).lower()
    assert "qa034" not in serialized
    assert "raw email" not in serialized
    assert "full subject" not in serialized
    assert "authorization header" not in serialized


def test_react_admin_memberships_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-membership-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-membership",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/admin/app/memberships/bootstrap.json?tenant_id={tenant_id}"
            )
            role_denied = client.post(
                f"/admin/app/memberships/role-grants?tenant_id={tenant_id}",
                json={
                    "confirmed": True,
                    "idempotency_key": "role-grant-ui-qa054",
                    "principal_identity_id": str(uuid4()),
                    "role_code": "platform_admin",
                    "scope_type": "platform",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in json.dumps(response.json())
    assert role_denied.status_code == 200
    assert role_denied.json()["field_errors"][0]["code"] == "scope_denied"


def test_react_admin_usage_local_principal_platform_tenant_and_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_usage_records(tmp_path, tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            "/admin/app/usage",
            headers={"X-Local-Principal": "platform-admin"},
        )
        platform_dashboard = client.get(
            "/admin/app/usage/bootstrap.json?group_by=tenant",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_dashboard = client.get(
            f"/admin/app/usage/bootstrap.json?tenant_id={tenant_id}&group_by=provider",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        grouped = client.get(
            "/admin/app/usage/bootstrap.json?group_by=gateway_operation",
            headers={"X-Local-Principal": "platform-admin"},
        )
        events = client.get(
            "/admin/app/usage/events.json?group_by=governed_tool",
            headers={"X-Local-Principal": "platform-admin"},
        )
        export = client.post(
            f"/admin/app/usage/exports?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "filters": {"tenant_id": str(tenant_id), "range": "Last 7 days"},
                "requested_group_by": "provider",
                "idempotency_key": "usage-export-ui-qa056",
            },
        )
        export_id = export.json()["usage_export_request_id"]
        denied_export = client.post(
            f"/admin/app/usage/exports?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "filters": {"tenant_id": str(other_tenant_id)},
                "requested_group_by": "provider",
                "idempotency_key": "usage-export-ui-qa056-denied",
            },
        )
        export_detail = client.get(
            f"/admin/app/usage/exports/{export_id}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "platform-admin"},
        )
        export_detail_html = client.get(
            f"/admin/app/usage/exports/{export_id}",
            headers={"X-Local-Principal": "platform-admin"},
        )
        cross_tenant = client.get(
            f"/admin/app/usage/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert platform_dashboard.status_code == 200
    platform_payload = platform_dashboard.json()
    platform_usage_payload = {
        "summary_cards": platform_payload["summary_cards"],
        "trend": platform_payload["trend"],
        "rollup": platform_payload["rollup"],
        "drilldown": platform_payload["drilldown"],
        "exports": platform_payload["exports"],
        "states": platform_payload["states"],
    }
    assert "Acme" in json.dumps(platform_usage_payload)
    assert "Globex" not in json.dumps(platform_usage_payload)
    assert tenant_dashboard.status_code == 200
    serialized_tenant = json.dumps(tenant_dashboard.json())
    assert "Usage and Cost Analytics" in serialized_tenant
    assert "Globex" not in serialized_tenant
    assert grouped.status_code == 200
    assert grouped.json()["rollup"]["group_by"] == "gateway_operation"
    assert events.status_code == 200
    assert any(row["tool_label"] for row in events.json()["rows"])
    assert export.status_code == 200
    assert export.json()["status"] == "completed"
    assert export.json()["artifact_reference"].startswith("usage-export:")
    assert "file:" not in json.dumps(export.json())
    assert denied_export.status_code == 200
    assert denied_export.json()["status"] == "denied"
    assert export_detail.status_code == 200
    assert export_detail.json()["usage_export_request_id"] == export_id
    assert export_detail_html.status_code == 200
    assert "Admin" in export_detail_html.text
    assert cross_tenant.status_code == 403
    unsafe = json.dumps(platform_dashboard.json()).lower()
    assert "qa035-secret-value" not in unsafe
    assert "raw prompt" not in unsafe
    assert "authorization header" not in unsafe


def test_react_admin_usage_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    _seed_usage_records(tmp_path, tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-usage-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-usage",
            token_subject="auth0|usage-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            dashboard = client.get(
                f"/admin/app/usage/bootstrap.json?tenant_id={tenant_id}"
            )
            export = client.post(
                f"/admin/app/usage/exports?tenant_id={tenant_id}",
                json={
                    "filters": {"tenant_id": str(tenant_id)},
                    "requested_group_by": "provider",
                    "idempotency_key": "usage-export-auth0-qa056",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Globex" not in json.dumps(payload)
    assert "auth0|usage-hidden" not in json.dumps(payload)
    assert export.status_code == 200
    assert export.json()["status"] == "completed"
    assert export.json()["artifact_reference"].startswith("usage-export:")


def test_react_admin_fails_closed_for_unauthorized_and_cross_tenant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        missing = client.get("/admin/app")
        not_admin = client.get(
            "/admin/app",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert missing.status_code == 401
    assert missing.json()["detail"] == "missing local principal header or cookie"
    assert not_admin.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_bootstrap_fails_closed_when_navigation_audit_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())

    async def fail_audit(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("audit store unavailable")

    monkeypatch.setattr(
        AuditService,
        "record_admin_navigation_visibility",
        fail_audit,
    )
    app = create_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            f"/admin/app/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "audit_unavailable"


def test_manifest_and_non_jinja_fallbacks_remain_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    monkeypatch.setenv(
        "REACT_ADMIN_MANIFEST_PATH",
        str(tmp_path / "missing-manifest.json"),
    )
    app = create_app()

    with TestClient(app) as client:
        manifest = client.get(
            "/admin/app/manifest.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        fallback = client.get(
            "/admin",
            headers={"X-Local-Principal": "platform-admin"},
        )
        disabled_route = client.get(
            "/admin/app/workflows",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert manifest.status_code == 200
    assert manifest.json()["available"] is False
    assert "src/multi_agent_platform" not in manifest.text
    assert fallback.status_code == 200
    assert fallback.headers["X-React-Admin-Host"] == "non-jinja"
    assert "Admin built assets are unavailable" in fallback.text
    assert "Admin Console" not in fallback.text
    assert disabled_route.status_code == 200
    assert "Admin" in disabled_route.text


def test_react_channels_platform_and_tenant_dashboards_are_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_channel_telegram_briefing_records(tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/channels/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/channels/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/channels?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        runs_html = client.get(
            f"/admin/app/channels/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/channels/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    assert "Globex" in json.dumps(platform.json())
    assert "qa036-secret-value" not in json.dumps(platform.json())
    assert tenant.status_code == 200
    tenant_payload = tenant.json()
    assert tenant_payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Globex" not in json.dumps(tenant_payload)
    assert "pair-code" not in json.dumps(tenant_payload)
    assert "qa036" not in json.dumps(tenant_payload).lower()
    assert html.status_code == 200
    assert "Admin" in html.text
    assert runs_html.status_code == 200
    assert "Admin" in runs_html.text
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_react_channels_mutations_link_token_and_run_status_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    seed = _seed_channel_telegram_briefing_records(
        tmp_path,
        tenant_id,
        other_tenant_id,
    )
    app = create_app()
    query = f"?tenant_id={tenant_id}"
    headers = {"X-Local-Principal": "tenant-admin-acme"}

    with TestClient(app) as client:
        bootstrap = client.get(
            f"/admin/app/channels/bootstrap.json{query}",
            headers=headers,
        )
        revision = bootstrap.json()["tenant_configs"][0]["revision"]
        config = client.post(
            f"/admin/app/channels/telegram/config{query}",
            headers=headers,
            json={
                "enabled": True,
                "bot_token_reference_label": "Telegram provider ref ready",
                "webhook_signing_reference_label": "Webhook signing ref ready",
                "revision": revision,
                "idempotency_key": "live-config",
            },
        )
        webhook = client.post(
            f"/admin/app/channels/telegram/webhook/validate{query}",
            headers=headers,
            json={
                "tenant_id": str(tenant_id),
                "revision": revision,
                "idempotency_key": "live-webhook",
            },
        )
        alias = client.post(
            f"/admin/app/channels/telegram/aliases{query}",
            headers=headers,
            json={
                "alias_text": "Morning briefing",
                "target_summary": "Configured workflow",
                "idempotency_key": "live-alias",
            },
        )
        token = client.post(
            f"/admin/app/channels/telegram/link-tokens{query}",
            headers=headers,
            json={
                "principal_label": "Acme briefing user",
                "expires_in_minutes": 10,
                "idempotency_key": "live-link-token",
            },
        )
        deliveries = client.get(
            f"/admin/app/channels/telegram/deliveries.json{query}",
            headers=headers,
        )
        run = client.get(
            f"/admin/app/channels/runs/{seed['run_id']}/status.json{query}",
            headers=headers,
        )

    assert config.status_code == 200
    assert config.json()["status"] == "accepted"
    assert webhook.status_code == 200
    assert webhook.json()["status"] == "accepted"
    assert alias.status_code == 200
    assert alias.json()["audit_reference"]
    assert token.status_code == 200
    assert len(token.json()["token_value"]) == 32
    assert deliveries.status_code == 200
    assert deliveries.json()["attempts"][0]["bot_api_boundary_status"] == "delivered"
    assert run.status_code == 200
    run_text = json.dumps(run.json())
    assert "raw prompt" not in run_text.lower()
    assert "run result" not in run_text.lower()


def test_react_channels_preference_routes_support_user_and_auth0_principal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    _seed_channel_telegram_briefing_records(tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        preferences = client.get(
            f"/admin/app/channels/briefing/preferences.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        save = client.post(
            f"/admin/app/channels/briefing/preferences?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
            json={
                "timezone": "America/New_York",
                "location_summary": "Metro area summary",
                "news_topics_summary": "4 topic categories",
                "vip_sender_summary": "3 masked sender hints",
                "workday_hours": "08:30-17:30",
                "commute_mode": "transit",
                "default_account_summary": "2 masked account refs",
                "output_style": "executive",
                "scheduled_time_summary": "Profile preference 07:45",
                "idempotency_key": "live-pref-save",
            },
        )
        export = client.post(
            f"/admin/app/channels/briefing/preferences/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
            json={"format": "json", "idempotency_key": "live-pref-export"},
        )

    assert preferences.status_code == 200
    assert preferences.json()["current_user_profile"]["timezone"] == "America/New_York"
    assert "raw preference" not in json.dumps(preferences.json()).lower()
    assert save.status_code == 200
    assert save.json()["status"] == "accepted"
    assert export.status_code == 200
    assert export.json()["artifact_reference"].startswith("briefing-export-")

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-channel-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-channel",
            token_subject="auth0|channel-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_dashboard = client.get(
                f"/admin/app/channels/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_dashboard.status_code == 200
    assert auth0_dashboard.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|channel-hidden" not in json.dumps(auth0_dashboard.json())


def test_react_migration_hardening_platform_tenant_and_user_scopes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        root_html = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        platform_dashboard = client.get(
            "/admin/app/migration/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_dashboard = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        tenant_user_dashboard = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        route_list = client.get(
            f"/admin/app/migration/routes.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        rollback = client.get(
            f"/admin/app/migration/rollback.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        tenant_user_shell = client.get(
            f"/admin/app/migration/shell.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        missing = client.get("/admin/app/migration/bootstrap.json")
        cross_tenant = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert root_html.status_code == 200
    assert platform_dashboard.status_code == 200
    platform_payload = platform_dashboard.json()
    assert platform_payload["summary"]["total_destinations"] >= 8
    assert "qa037-secret-value" not in json.dumps(platform_payload)
    assert platform_payload["title"] == "Admin browser UI"
    assert not any(
        entry["decision"] == "retained_fallback"
        for group in platform_payload["route_groups"]
        for entry in group["entries"]
    )
    assert platform_payload["jinja_inventory"]["summary"]["template_count"] == 0
    assert tenant_dashboard.status_code == 200
    tenant_payload = tenant_dashboard.json()
    assert all(
        entry["scope_requirement"] in {"tenant_admin", "tenant_user", "mixed"}
        for group in tenant_payload["route_groups"]
        for entry in group["entries"]
    )
    assert tenant_user_dashboard.status_code == 200
    assert any(
        state["reason"] == "user_scope_limited"
        for state in tenant_user_dashboard.json()["states"]
    )
    assert route_list.status_code == 200
    assert isinstance(route_list.json(), list)
    assert rollback.status_code == 200
    assert rollback.json()["status"] == "ready"
    assert tenant_user_shell.status_code == 200
    assert missing.status_code == 401
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_react_migration_hardening_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-migration-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-migration",
            token_subject="auth0|migration-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            dashboard = client.get(
                f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}"
            )
            routes = client.get(
                f"/admin/app/migration/routes.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert routes.status_code == 200
    assert "auth0|migration-hidden" not in json.dumps(payload)
