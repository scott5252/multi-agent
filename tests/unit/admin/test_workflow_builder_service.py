from __future__ import annotations

from multi_agent_platform.admin.workflow_builder import (
    CURRENT_REVISION,
    build_graph_preview,
    build_publish_result,
    build_reference_catalog,
    build_save_result,
    build_validation_result,
    build_workflow_builder_envelope,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    WorkflowDraftSaveRequest,
    WorkflowPublishRequest,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def _principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-workflow-builder-test",
    )


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type="tenant",
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )


def test_builder_envelope_contains_guided_draft_and_safe_actions() -> None:
    envelope = build_workflow_builder_envelope(
        scope=_tenant_scope(),
        principal=_principal(),
    )

    assert envelope.page_id == "react-workflow-builder"
    assert envelope.draft.tenant_label == "Acme"
    assert envelope.draft.graph.nodes[0].label == "Start briefing"
    assert envelope.sections[-1].status == "blocked"
    assert {action.action_id for action in envelope.actions} == {
        "workflow-publish",
        "workflow-save",
        "workflow-validate",
    }
    assert "qa030-secret-value" not in envelope.model_dump_json()


def test_reference_catalog_is_tenant_aware() -> None:
    tenant_catalog = build_reference_catalog(scope=_tenant_scope())
    platform_catalog = build_reference_catalog(
        scope=ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    )

    assert tenant_catalog.provider_options[0].tenant_eligible is True
    assert platform_catalog.provider_options[0].tenant_eligible is False
    assert tenant_catalog.test_suite_options[0].readiness_status == "blocked"


def test_save_result_accepts_current_revision_and_reports_stale_conflict() -> None:
    accepted = build_save_result(
        scope=_tenant_scope(),
        request=WorkflowDraftSaveRequest(
            description="Prepare a safe briefing.",
            idempotency_key="key-1",
            name="Daily briefing workflow",
            revision=CURRENT_REVISION,
        ),
    )
    stale = build_save_result(
        scope=_tenant_scope(),
        request=WorkflowDraftSaveRequest(
            description="Prepare a safe briefing.",
            force_stale=True,
            idempotency_key="key-2",
            name="Daily briefing workflow",
            revision=CURRENT_REVISION,
        ),
    )

    assert accepted.status == "accepted"
    assert accepted.revision == "draft-rev-qa030-next"
    assert accepted.validation is not None
    assert stale.status == "stale_conflict"
    assert stale.stale_conflict is not None
    assert stale.stale_conflict.reload_href.endswith(
        "tenant_id=11111111-1111-1111-1111-111111111111"
    )


def test_validation_and_publish_results_cover_blocked_and_ready_paths() -> None:
    blocked_validation = build_validation_result(ready=False)
    ready_validation = build_validation_result(ready=True)
    blocked_publish = build_publish_result(
        request=WorkflowPublishRequest(
            idempotency_key="publish-1",
            revision=CURRENT_REVISION,
        )
    )
    confirmation = build_publish_result(
        request=WorkflowPublishRequest(
            idempotency_key="publish-2",
            ready_fixture=True,
            revision=CURRENT_REVISION,
        )
    )
    accepted = build_publish_result(
        request=WorkflowPublishRequest(
            confirmed=True,
            idempotency_key="publish-3",
            ready_fixture=True,
            revision=CURRENT_REVISION,
        )
    )

    assert blocked_validation.validation is not None
    assert blocked_validation.validation.findings
    assert ready_validation.publish_readiness is not None
    assert ready_validation.publish_readiness.confirmation is not None
    assert blocked_publish.status == "validation_error"
    assert confirmation.status == "confirmation_required"
    assert accepted.status == "accepted"
    assert accepted.publish_readiness is not None
    assert accepted.publish_readiness.published_bundle_summary is not None


def test_large_graph_preview_is_bounded_and_accessible() -> None:
    graph = build_graph_preview(large=True)

    assert len(graph.nodes) == 100
    assert len(graph.edges) == 99
    assert graph.accessibility_summary
