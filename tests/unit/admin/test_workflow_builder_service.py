from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.admin.workflow_builder import (
    _graph_from_live,
    _lookup_group_key,
    _section_from_validation_message,
    _status_from_badges,
    _status_from_lookup,
    blocking_authoring_findings,
    build_copy_result,
    build_create_result,
    build_document_save_validation_result,
    build_publish_result,
    build_reference_catalog,
    build_restore_result,
    build_save_result,
    build_validation_result,
    build_workflow_builder_envelope,
    build_workflow_registry_envelope,
    build_workflow_sharing_summary,
    build_workflow_version_detail,
    findings_from_authoring_validation,
    findings_from_pydantic_error,
    unsafe_document_findings,
    workflow_document_digest,
    workflow_document_payload_digest,
    workflow_document_payload_size,
    workflow_save_scope_hash,
)
from multi_agent_platform.admin.workflow_registry.reference_validation import (
    build_editor_lookup_response,
)
from multi_agent_platform.api.schemas.admin_patterns import RevisionConflict
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    WorkflowBuilderStatus,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupGroup,
    EditorLookupOption,
    EditorLookupResponse,
    GraphPreviewNode,
    GraphPreviewResponse,
    GraphValidationBadge,
    PublishGateResponse,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    DraftRevisionListResponse,
    RegistrySharingGrantResponse,
    ValidationFindingResponse,
    ValidationResultResponse,
    WorkflowBuilderStatusSummary,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowKind,
    WorkflowRegistryItem,
    WorkflowScopeType,
    WorkflowVersionResponse,
    WorkflowVisibilityStatus,
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
        tenant_id=uuid4(),
        label="Acme",
    )


def _document(slug: str = "customer-intake") -> WorkflowDraftDocument:
    return WorkflowDraftDocument(
        workflow_key=slug,
        display_name="Customer Intake",
        description="Collect incoming work and route it to the next step.",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        entry_node_key="triage-node",
        roles=[
            {
                "role_key": "triage-role",
                "display_name": "Triage Role",
                "purpose": "Assess the incoming payload.",
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
        contracts=[
            {"contract_key": "intake-request", "json_schema": {"type": "object"}},
            {"contract_key": "triage-result", "json_schema": {"type": "object"}},
        ],
        nodes=[
            {
                "node_key": "triage-node",
                "node_type": "role",
                "display_name": "Triage",
                "role_key": "triage-role",
            }
        ],
        edges=[],
        join_policies=[],
        approval_gates=[],
        subworkflow_refs=[],
    )


def _draft(revision: int = 1) -> WorkflowDraftResponse:
    now = datetime.now(UTC)
    revision_id = uuid4()
    return WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        description="Collect incoming work.",
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=uuid4(),
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        status="active",
        current_revision_number=revision,
        latest_revision=WorkflowDraftRevisionResponse(
            workflow_draft_revision_id=revision_id,
            revision_number=revision,
            document_sha256="a" * 64,
            change_summary="Current durable revision",
            created_at=now,
        ),
        latest_validation=ValidationResultResponse(
            validation_result_id=uuid4(),
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
            draft_revision_id=revision_id,
        ),
        document=_document(),
        builder_status=WorkflowBuilderStatusSummary(
            latest_validation_status="passed",
            publish_readiness_status="ready",
        ),
        updated_at=now,
    )


def _version() -> WorkflowVersionResponse:
    now = datetime.now(UTC)
    version_id = uuid4()
    return WorkflowVersionResponse(
        workflow_version_bundle_id=version_id,
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        display_version="v3",
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=uuid4(),
        status="published",
        compiled_bundle_digest="b" * 64,
        published_from_draft_id=uuid4(),
        published_from_revision_id=uuid4(),
        sharing_grants=[
            RegistrySharingGrantResponse(
                registry_sharing_grant_id=uuid4(),
                workflow_version_bundle_id=version_id,
                grantee_tenant_id=uuid4(),
                status="active",
                created_at=now,
            )
        ],
        published_at=now,
    )


def _publish_gate(
    *,
    passing: int = 0,
    failing: int = 0,
    missing: int = 0,
    stale: int = 0,
) -> PublishGateResponse:
    return PublishGateResponse(
        publish_gate_id="gate-1",
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="c" * 64,
        status="blocked" if failing or missing else "ready",
        blocking_issue_count=failing + missing,
        advisory_issue_count=stale,
        required_test_summary=RequiredTestSummary(
            required_count=passing + failing + missing + stale,
            passing_count=passing,
            failing_count=failing,
            missing_count=missing,
            stale_count=stale,
        ),
        digest="digest-1",
    )


def _graph_preview(size: int = 1) -> GraphPreviewResponse:
    return GraphPreviewResponse(
        nodes=[
            GraphPreviewNode(
                id=f"node-{index}",
                node_key=f"node-{index}",
                node_type="role",
                label=f"Node {index}",
                field_path=f"nodes[{index}]",
                role_key="triage-role",
            )
            for index in range(size)
        ],
    )


def _blocking_graph_preview() -> GraphPreviewResponse:
    return GraphPreviewResponse(
        nodes=[
            GraphPreviewNode(
                id="blocked-node",
                node_key="blocked-node",
                node_type="role",
                label="Blocked Node",
                field_path="nodes[0]",
                role_key="triage-role",
                badges=[
                    GraphValidationBadge(
                        code="missing-reference",
                        severity="error",
                        message="Reference is missing.",
                    )
                ],
            )
        ],
    )


def test_workflow_builder_status_helpers_cover_fallback_branches() -> None:
    empty_graph = _graph_from_live(None, layout_revision="layout-empty")

    assert empty_graph.layout_revision == "layout-empty"
    assert empty_graph.nodes == ()
    assert empty_graph.edges == ()
    assert "No graph preview" in empty_graph.accessibility_summary
    assert _status_from_lookup("available", False) == WorkflowBuilderStatus.READY
    assert _status_from_lookup("failed", False) == WorkflowBuilderStatus.BLOCKED
    assert _status_from_lookup("warning", False) == WorkflowBuilderStatus.WARNING
    assert _status_from_lookup("unknown", True) == WorkflowBuilderStatus.UNAVAILABLE
    assert (
        _status_from_badges(
            [
                GraphValidationBadge(
                    code="missing-role",
                    severity="error",
                    message="Role is missing.",
                    blocking=True,
                )
            ]
        )
        == WorkflowBuilderStatus.BLOCKED
    )
    assert _lookup_group_key("provider model route") == "model_route"
    assert _lookup_group_key("required test suite") == "test_suite"
    assert _lookup_group_key("subworkflow bundle") == "subworkflow"
    assert _section_from_validation_message("Role binding is invalid") == "roles"
    assert _section_from_validation_message("Join policy is invalid") == "joins"
    assert _section_from_validation_message("Approval gate is invalid") == "approvals"
    assert (
        _section_from_validation_message("Subworkflow reference is invalid")
        == "subworkflows"
    )
    assert _section_from_validation_message("Test evidence is missing") == "tests"
    assert _section_from_validation_message("Metadata is invalid") == "metadata"


def test_empty_builder_envelope_is_truthful_and_safe() -> None:
    envelope = build_workflow_builder_envelope(
        scope=_tenant_scope(),
        principal=_principal(),
    )

    assert envelope.page_id == "react-workflow-builder"
    assert envelope.draft is None
    assert envelope.state is not None
    assert envelope.state.state == "empty"
    assert envelope.empty_state is not None
    assert "qa030-secret-value" not in envelope.model_dump_json()


def test_live_registry_and_draft_projection_use_durable_ids() -> None:
    scope = _tenant_scope()
    draft = _draft()
    registry = WorkflowRegistryItem(
        workflow_lineage_id=draft.workflow_lineage_id,
        workflow_draft_id=draft.workflow_draft_id,
        slug=draft.slug,
        display_name=draft.display_name,
        workflow_kind=draft.workflow_kind,
        scope_type=draft.scope_type,
        tenant_id=draft.tenant_id,
        visibility_status=WorkflowVisibilityStatus.DRAFT,
        current_revision_number=draft.current_revision_number,
        latest_validation_status="passed",
        publish_readiness_status="ready",
        updated_at=draft.updated_at,
    )

    envelope = build_workflow_builder_envelope(
        scope=scope,
        principal=_principal(),
        registry_items=(registry,),
        draft=draft,
        graph_preview=_graph_preview(),
        revisions=DraftRevisionListResponse(
            workflow_draft_id=draft.workflow_draft_id,
            current_revision_number=draft.current_revision_number,
            revisions=[draft.latest_revision],
        ),
    )

    assert envelope.draft is not None
    assert envelope.draft.workflow_draft_id == str(draft.workflow_draft_id)
    assert envelope.draft.document.workflow_key == draft.document.workflow_key
    assert envelope.draft.section_summaries
    assert envelope.draft.graph.nodes[0].label == "Node 0"
    assert envelope.registry.items[0].workflow_draft_id == str(draft.workflow_draft_id)
    assert envelope.validation is not None
    assert envelope.validation.status == "ready"


def test_reference_catalog_projects_live_lookup_groups() -> None:
    catalog = build_reference_catalog(
        scope=_tenant_scope(),
        lookups=EditorLookupResponse(
            groups=[
                EditorLookupGroup(
                    lookup_kind="prompt",
                    label="Prompts",
                    options=[
                        EditorLookupOption(
                            option_id="prompt-1",
                            label="Published prompt",
                            value="prompt-version-1",
                            lookup_kind="prompt",
                            scope_type="tenant",
                            status="ready",
                            description="Safe prompt summary.",
                        )
                    ],
                )
            ]
        ),
    )

    assert catalog.prompt_options[0].reference_id == "prompt-version-1"
    assert catalog.prompt_options[0].safe_summary == "Safe prompt summary."


def test_reference_catalog_splits_prompt_profile_document_references() -> None:
    prompt_version_id = uuid4()
    profile_version_id = uuid4()
    document_payload = _document().model_dump(mode="json")
    document_payload["prompt_profile_references"] = [
        {
            "reference_key": "coordinator-binding",
            "role_key": "triage-role",
            "agent_key": "triage-role",
            "agent_kind": "agent",
            "agent_profile_version_id": str(profile_version_id),
            "prompt_version_ids": [str(prompt_version_id)],
            "readiness_status": "ready",
            "source_scope": "tenant",
            "resolution_digest": "sha256:coordinator-binding",
        }
    ]
    document = WorkflowDraftDocument.model_validate(document_payload)

    lookups = build_editor_lookup_response(
        document,
        scope_type="tenant",
        tenant_id=str(uuid4()),
    )
    catalog = build_reference_catalog(scope=_tenant_scope(), lookups=lookups)

    assert catalog.prompt_options[0].reference_id == "coordinator-binding"
    assert catalog.prompt_options[0].readiness_status == "ready"
    assert catalog.profile_options[0].reference_id == "coordinator-binding"
    assert catalog.profile_options[0].readiness_status == "ready"


def test_mutation_results_require_durable_state() -> None:
    scope = _tenant_scope()
    draft = _draft()

    created = build_create_result(draft=draft, scope=scope)
    saved = build_save_result(draft=draft)
    replayed = build_save_result(
        draft=draft,
        idempotency_key="workflow-save-key",
        replayed=True,
    )
    missing = build_save_result()

    assert created.status == "accepted"
    assert created.next_action is not None
    assert saved.revision == str(draft.current_revision_number)
    assert replayed.status == "idempotent_replay"
    assert replayed.idempotency is not None
    assert replayed.idempotency.replayed is True
    assert missing.status == "validation_error"


def test_mutation_result_edge_states_are_safe() -> None:
    scope = _tenant_scope()
    draft = _draft()
    conflict = RevisionConflict(
        submitted_revision="1",
        current_revision="2",
        message="Reload before retrying.",
        reload_href="/admin/app/workflows",
    )

    assert build_create_result(scope=scope).status == "validation_error"
    assert build_restore_result(conflict=conflict).status == "stale_conflict"
    assert build_restore_result().status == "validation_error"
    assert build_restore_result(draft=draft).toast is not None
    assert build_copy_result(scope=scope).status == "validation_error"
    assert build_copy_result(draft=draft, scope=scope).next_action is not None
    assert build_validation_result().status == "validation_error"


def test_document_save_validation_helpers_map_field_paths() -> None:
    invalid_payload = {
        **_document().model_dump(mode="json"),
        "edges": [
            {
                "edge_key": "bad-edge",
                "source_node_key": "triage-node",
                "target_node_key": "missing-node",
            }
        ],
    }

    try:
        WorkflowDraftDocument.model_validate(invalid_payload)
    except ValueError as exc:
        findings = findings_from_pydantic_error(exc)  # type: ignore[arg-type]
    else:  # pragma: no cover - defensive branch
        raise AssertionError("invalid graph payload should fail validation")

    result = build_document_save_validation_result(
        revision="1",
        findings=findings,
    )
    digest = workflow_document_digest(_document())

    assert digest
    assert result.status == "validation_error"
    assert result.validation is not None
    assert result.validation.findings[0].field_path
    assert blocking_authoring_findings(_document()) == ()


def test_document_save_helper_branches_are_safe_and_deterministic() -> None:
    payload = {
        "roles": [{"purpose": "raw prompt copied into a role"}],
        "edges": [{"message": "Bearer token copied into graph edge"}],
        "editor_annotations": {
            "section_notes": {"metadata": "authorization: copied header"}
        },
        "test_requirements": [{"description": "begin private key copied"}],
        "subworkflow_refs": [{"description": "sk-copied-token"}],
        "description": "safe workflow description",
    }

    unsafe_findings = unsafe_document_findings(payload)
    payload_digest = workflow_document_payload_digest(
        {"payload": payload, "id": uuid4()}
    )
    scope_hash = workflow_save_scope_hash(
        tenant_id=str(uuid4()),
        principal_id="tenant-admin",
        workflow_draft_id=str(uuid4()),
        revision="7",
    )
    authoring_findings = findings_from_authoring_validation(
        (
            {
                "field_path": "roles[0].role_key",
                "severity": "warning",
                "category": "roles",
                "message": "Role reference is advisory.",
                "remediation": "Review the role reference.",
            },
            {
                "field_path": "join_policies[0].join_key",
                "severity": "info",
                "category": "joins",
                "message": "Join policy is informational.",
            },
            {
                "field_path": "edges[0].target_node_key",
                "severity": "critical",
                "blocking": True,
                "category": "graph",
                "message": "Graph edge is blocking.",
                "graph_element_id": "edge-a",
                "reference_id": "validation-ref",
            },
        )
    )

    assert len(unsafe_findings) == 5
    assert unsafe_findings[0].section == "roles"
    assert unsafe_findings[1].section == "graph"
    assert unsafe_findings[2].section == "annotations"
    assert unsafe_findings[3].section == "tests"
    assert unsafe_findings[4].section == "subworkflows"
    assert workflow_document_payload_size(payload) > 0
    assert len(payload_digest) == 64
    assert len(scope_hash) == 64
    assert authoring_findings[0].severity == "warning"
    assert authoring_findings[1].severity == "info"
    assert authoring_findings[2].severity == "blocking"
    assert authoring_findings[2].graph_element_id == "edge-a"
    assert authoring_findings[2].evidence_reference_id == "validation-ref"


def test_validation_and_publish_results_project_findings_and_evidence() -> None:
    draft = _draft()
    validation = ValidationResultResponse(
        validation_result_id=uuid4(),
        status="failed",
        blocking_issue_count=1,
        advisory_issue_count=1,
        draft_revision_id=draft.latest_revision.workflow_draft_revision_id,
        findings=[
            ValidationFindingResponse(
                category="reference",
                severity="warning",
                message="Missing safe reference.",
                field_path="nodes[0]",
                code="missing-reference",
                remediation="Select a live reference.",
                blocking=True,
                reference_id="ref-1",
                safe_links=["/admin/app/workflows"],
            )
        ],
    )

    validation_result = build_validation_result(
        draft=draft,
        validation=validation,
        publish_gate=_publish_gate(failing=1, missing=1),
    )
    blocked_publish = build_publish_result(
        draft=draft,
        gate=_publish_gate(missing=1),
    )
    confirmation = build_publish_result(
        draft=draft,
        gate=_publish_gate(stale=1),
        confirmation_required=True,
    )
    published = build_publish_result(
        draft=draft,
        version=_version(),
        gate=_publish_gate(passing=1),
    )

    assert validation_result.validation is not None
    assert validation_result.validation.findings[0].severity == "blocking"
    assert validation_result.publish_readiness is not None
    assert validation_result.publish_readiness.required_evidence[0].status == "blocked"
    assert blocked_publish.status == "validation_error"
    assert confirmation.status == "confirmation_required"
    assert published.status == "accepted"
    assert published.publish_readiness is not None
    assert published.publish_readiness.published_bundle_summary is not None


def test_publish_evidence_with_required_count_without_results_is_unavailable() -> None:
    draft = _draft()
    gate = PublishGateResponse(
        publish_gate_id="gate-unavailable",
        workflow_draft_id=str(draft.workflow_draft_id),
        workflow_draft_revision_id=str(
            draft.latest_revision.workflow_draft_revision_id
        ),
        document_sha256="d" * 64,
        status="blocked",
        blocking_issue_count=0,
        advisory_issue_count=0,
        required_test_summary=RequiredTestSummary(
            required_count=2,
            passing_count=0,
            failing_count=0,
            missing_count=0,
            stale_count=0,
        ),
        digest="digest-unavailable",
    )

    result = build_validation_result(
        draft=draft,
        validation=draft.latest_validation,
        publish_gate=gate,
    )

    assert result.publish_readiness is not None
    assert result.publish_readiness.required_evidence[0].status == "unavailable"


def test_version_registry_and_sharing_projection_cover_published_state() -> None:
    scope = _tenant_scope()
    version = _version()
    registry = WorkflowRegistryItem(
        workflow_lineage_id=version.workflow_lineage_id,
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        slug=version.slug,
        display_name=version.display_name,
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=version.tenant_id,
        visibility_status=WorkflowVisibilityStatus.PUBLISHED,
        latest_validation_status=None,
        publish_readiness_status="not_evaluated",
        updated_at=version.published_at,
    )

    detail = build_workflow_version_detail(scope=scope, version=version)
    sharing = build_workflow_sharing_summary(scope=scope, version=version)
    envelope = build_workflow_registry_envelope(scope=scope, items=(registry,))

    assert detail is not None
    assert detail.digest_label.startswith("Digest ")
    assert sharing.status == "ready"
    assert sharing.grants_label == "1 active sharing grant"
    assert envelope.items[0].status == "published"
    assert envelope.items[0].actions[0].label == "View version"
    assert envelope.items[0].tenant_label is None
    assert envelope.items[0].sharing_summary.startswith("Published bundle")


def test_graph_and_lookup_status_branches_are_projected() -> None:
    envelope = build_workflow_builder_envelope(
        scope=_tenant_scope(),
        principal=_principal(),
        draft=_draft(),
        graph_preview=_blocking_graph_preview(),
        lookups=EditorLookupResponse(
            groups=[
                EditorLookupGroup(
                    lookup_kind="runtime_profile",
                    label="Profiles",
                    options=[
                        EditorLookupOption(
                            option_id="profile-1",
                            label="Missing profile",
                            value="profile-1",
                            lookup_kind="runtime_profile",
                            scope_type="tenant",
                            status="missing",
                            metadata={"display_version": "v2"},
                        ),
                    ],
                ),
                EditorLookupGroup(
                    lookup_kind="model_route",
                    label="Models",
                    options=[
                        EditorLookupOption(
                            option_id="model-1",
                            label="Stale model",
                            value="model-1",
                            lookup_kind="model_route",
                            scope_type="tenant",
                            status="stale",
                        ),
                    ],
                ),
                EditorLookupGroup(
                    lookup_kind="subworkflow",
                    label="Subworkflows",
                    options=[
                        EditorLookupOption(
                            option_id="workflow-1",
                            label="Subworkflow",
                            value="workflow-1",
                            lookup_kind="subworkflow",
                            scope_type="tenant",
                            status="ready",
                        ),
                    ],
                ),
            ]
        ),
    )

    assert envelope.draft is not None
    assert envelope.draft.graph.nodes[0].status == "blocked"
    assert envelope.reference_catalog.profile_options[0].readiness_status == "blocked"
    assert envelope.reference_catalog.provider_options[0].readiness_status == "warning"
    assert envelope.reference_catalog.subworkflow_options[0].version_label is None


def test_registry_empty_state_includes_pagination_and_sorting_metadata() -> None:
    registry = build_workflow_registry_envelope(scope=_tenant_scope())

    assert registry.empty_state is not None
    assert registry.pagination is not None
    assert registry.pagination.total_items == 0
    assert registry.sorting is not None
    assert registry.sorting.active.key == "updated_desc"
