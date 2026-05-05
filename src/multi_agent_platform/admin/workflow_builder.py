from __future__ import annotations

from uuid import UUID

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    ConfirmationRequirement,
    RevisionConflict,
    ToastHint,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    BuilderMutationResult,
    BuilderSection,
    ValidationFinding,
    WorkflowBuilderEnvelope,
    WorkflowBuilderSeverity,
    WorkflowBuilderStatus,
    WorkflowDraftDocument,
    WorkflowDraftSaveRequest,
    WorkflowEvidenceSummary,
    WorkflowGraphEdge,
    WorkflowGraphNode,
    WorkflowGraphPreview,
    WorkflowJoinPolicySummary,
    WorkflowJsonInspector,
    WorkflowPublishReadiness,
    WorkflowPublishRequest,
    WorkflowReferenceCatalog,
    WorkflowReferenceOption,
    WorkflowRevisionSummary,
    WorkflowValidationSummary,
)
from multi_agent_platform.auth.principal import PrincipalContext

DEFAULT_DRAFT_ID = "00000000-0000-0000-0000-000000000030"
DEFAULT_LINEAGE_ID = "11111111-1111-1111-1111-000000000030"
CURRENT_REVISION = "draft-rev-qa030-current"
NEXT_REVISION = "draft-rev-qa030-next"


def build_workflow_builder_envelope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    workflow_draft_id: str | UUID | None = None,
    large: bool = False,
) -> WorkflowBuilderEnvelope:
    _ = principal
    draft_id = str(workflow_draft_id or DEFAULT_DRAFT_ID)
    graph = build_graph_preview(large=large)
    validation = build_validation_summary(blocked=not large)
    publish_readiness = build_publish_readiness(ready=False)
    tenant_label = (
        scope.label if scope.scope_type == ReactAdminScopeType.TENANT else None
    )
    return WorkflowBuilderEnvelope(
        page_id="react-workflow-builder",
        title="Workflow builder",
        description=(
            "Guided workflow drafting with backend validation, graph review, "
            "required evidence, and publish gates."
        ),
        scope=scope,
        draft=WorkflowDraftDocument(
            workflow_draft_id=draft_id,
            workflow_lineage_id=DEFAULT_LINEAGE_ID,
            revision=CURRENT_REVISION,
            name="Daily briefing workflow",
            description="Prepare a safe daily intelligence briefing for a tenant.",
            status=WorkflowBuilderStatus.READY,
            tenant_label=tenant_label,
            metadata_summary="Briefing workflow with explicit revision saves.",
            roles_summary="Coordinator plus calendar and weather sub-agent roles.",
            references_summary=(
                "Prompt, profile, provider route, skill, and test evidence selected."
            ),
            graph=graph,
        ),
        sections=_sections(),
        reference_catalog=build_reference_catalog(scope=scope),
        validation=validation,
        publish_readiness=publish_readiness,
        revisions=_revisions(),
        json_inspector=_json_inspector(),
        actions=(
            AdminAction(
                action_id="workflow-save",
                label="Save draft",
                method=AdminActionMethod.POST,
                href=_draft_action_href(draft_id, "save", scope),
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
            AdminAction(
                action_id="workflow-validate",
                label="Run validation",
                method=AdminActionMethod.POST,
                href=_draft_action_href(draft_id, "validate", scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
            AdminAction(
                action_id="workflow-publish",
                label="Review publish",
                method=AdminActionMethod.POST,
                href=_draft_action_href(draft_id, "publish", scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
                requires_confirmation=True,
                confirmation=ConfirmationRequirement(
                    title="Publish workflow",
                    summary=(
                        "Publish only after validation and required evidence are "
                        "current."
                    ),
                    confirm_label="Publish workflow",
                ),
            ),
        ),
    )


def build_reference_catalog(*, scope: ReactAdminScope) -> WorkflowReferenceCatalog:
    tenant_eligible = scope.scope_type == ReactAdminScopeType.TENANT
    return WorkflowReferenceCatalog(
        prompt_options=(
            WorkflowReferenceOption(
                reference_id="prompt-daily-briefing-v3",
                label="Daily briefing prompt",
                kind="prompt",
                readiness_status=WorkflowBuilderStatus.READY,
                version_label="v3",
                safe_summary=(
                    "Prompt version is published and granted to the active scope."
                ),
                href=_with_tenant_query("/admin/prompt-runtime/prompts", scope),
            ),
        ),
        profile_options=(
            WorkflowReferenceOption(
                reference_id="profile-briefing-safe",
                label="Briefing runtime profile",
                kind="runtime_profile",
                readiness_status=WorkflowBuilderStatus.READY,
                version_label="v2",
                safe_summary="Profile pins provider routing and tool policy versions.",
                href=_with_tenant_query("/admin/prompt-runtime/profiles", scope),
            ),
        ),
        provider_options=(
            WorkflowReferenceOption(
                reference_id="provider-route-briefing",
                label="Pinned briefing model route",
                kind="model_route",
                readiness_status=WorkflowBuilderStatus.WARNING,
                tenant_eligible=tenant_eligible,
                safe_summary=(
                    "Provider route is configured with safe reference diagnostics."
                ),
                href="/admin/model-providers",
            ),
        ),
        skill_options=(
            WorkflowReferenceOption(
                reference_id="skill-weather-readonly",
                label="Weather connector skill",
                kind="skill",
                readiness_status=WorkflowBuilderStatus.READY,
                safe_summary=(
                    "Installed read-only connector is eligible for workflow binding."
                ),
                href=_with_tenant_query(
                    "/admin/skill-registry/ui/installations",
                    scope,
                ),
            ),
        ),
        test_suite_options=(
            WorkflowReferenceOption(
                reference_id="suite-briefing-required",
                label="Daily briefing required suite",
                kind="test_suite",
                readiness_status=WorkflowBuilderStatus.BLOCKED,
                safe_summary="Repository-backed evidence is required before publish.",
                href=_with_tenant_query("/admin/agent-tests/ui", scope),
            ),
        ),
        subworkflow_options=(
            WorkflowReferenceOption(
                reference_id="subworkflow-weather-v1",
                label="Weather enrichment subworkflow",
                kind="subworkflow",
                readiness_status=WorkflowBuilderStatus.READY,
                safe_summary="Published subworkflow is visible to the active scope.",
                href=_with_tenant_query("/admin/workflows/ui", scope),
            ),
        ),
    )


def build_save_result(
    *,
    scope: ReactAdminScope,
    request: WorkflowDraftSaveRequest,
) -> BuilderMutationResult:
    if request.force_stale or request.revision != CURRENT_REVISION:
        return BuilderMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Draft revision changed before the save could be applied.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision,
                current_revision=CURRENT_REVISION,
                message="Reload the current draft revision before saving again.",
                reload_href=_with_tenant_query("/admin/app/workflows", scope),
            ),
            audit_reference_id="audit-workflow-save-stale-qa030",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Draft saved as a new explicit revision.",
        revision=NEXT_REVISION,
        validation=build_validation_summary(blocked=True),
        publish_readiness=build_publish_readiness(ready=False),
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Draft saved",
            summary="Validation is ready to refresh for the new revision.",
        ),
        audit_reference_id="audit-workflow-save-qa030",
    )


def build_validation_result(*, ready: bool = False) -> BuilderMutationResult:
    validation = build_validation_summary(blocked=not ready)
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow validation completed with safe findings.",
        revision=CURRENT_REVISION,
        validation=validation,
        publish_readiness=build_publish_readiness(ready=ready),
        audit_reference_id="audit-workflow-validation-qa030",
    )


def build_publish_result(
    *,
    request: WorkflowPublishRequest,
) -> BuilderMutationResult:
    if not request.ready_fixture:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Publish is blocked until validation and evidence are current.",
            revision=request.revision,
            publish_readiness=build_publish_readiness(ready=False),
            audit_reference_id="audit-workflow-publish-blocked-qa030",
        )
    if not request.confirmed:
        return BuilderMutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Confirm publish after reviewing the immutable bundle summary.",
            revision=request.revision,
            publish_readiness=build_publish_readiness(ready=True),
            confirmation=ConfirmationRequirement(
                title="Publish workflow",
                summary="This creates an immutable published workflow bundle.",
                confirm_label="Publish workflow",
            ),
            audit_reference_id="audit-workflow-publish-confirm-qa030",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow published as an immutable bundle.",
        revision=request.revision,
        publish_readiness=build_publish_readiness(ready=True, published=True),
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Workflow published",
            summary="The published bundle is ready for runtime selection.",
        ),
        audit_reference_id="audit-workflow-publish-qa030",
    )


def build_graph_preview(*, large: bool = False) -> WorkflowGraphPreview:
    if large:
        nodes = tuple(
            WorkflowGraphNode(
                node_id=f"node-{index}",
                label=f"Workflow step {index}",
                node_type="agent",
                status=WorkflowBuilderStatus.READY,
                summary="Large workflow fixture node summary.",
                x=(index % 10) * 180,
                y=(index // 10) * 120,
            )
            for index in range(1, 101)
        )
        edges = tuple(
            WorkflowGraphEdge(
                edge_id=f"edge-{index}-{index + 1}",
                source=f"node-{index}",
                target=f"node-{index + 1}",
                label="next",
            )
            for index in range(1, 100)
        )
    else:
        nodes = (
            WorkflowGraphNode(
                node_id="start",
                label="Start briefing",
                node_type="trigger",
                status=WorkflowBuilderStatus.READY,
                role_label="Coordinator",
                summary="Start the daily briefing workflow.",
                x=0,
                y=80,
            ),
            WorkflowGraphNode(
                node_id="calendar",
                label="Calendar branch",
                node_type="sub_agent",
                status=WorkflowBuilderStatus.READY,
                role_label="Calendar analyst",
                summary="Read-only calendar context branch.",
                x=260,
                y=0,
            ),
            WorkflowGraphNode(
                node_id="weather",
                label="Weather branch",
                node_type="tool",
                status=WorkflowBuilderStatus.WARNING,
                role_label="Weather analyst",
                summary="Weather connector branch requires current evidence.",
                x=260,
                y=170,
            ),
            WorkflowGraphNode(
                node_id="join",
                label="Join briefing branches",
                node_type="join",
                status=WorkflowBuilderStatus.WARNING,
                summary="Wait for required branches before drafting the briefing.",
                x=560,
                y=80,
            ),
        )
        edges = (
            WorkflowGraphEdge(
                edge_id="edge-start-calendar",
                source="start",
                target="calendar",
                label="fan-out",
                condition_category="parallel",
            ),
            WorkflowGraphEdge(
                edge_id="edge-start-weather",
                source="start",
                target="weather",
                label="fan-out",
                condition_category="parallel",
            ),
            WorkflowGraphEdge(
                edge_id="edge-calendar-join",
                source="calendar",
                target="join",
                label="required",
                condition_category="join",
            ),
            WorkflowGraphEdge(
                edge_id="edge-weather-join",
                source="weather",
                target="join",
                label="required",
                condition_category="join",
            ),
        )
    return WorkflowGraphPreview(
        layout_revision="layout-qa030",
        layout_is_authoritative=False,
        nodes=nodes,
        edges=edges,
        join_policies=(
            WorkflowJoinPolicySummary(
                policy_id="wait_for_required_branches",
                label="Wait for required branches",
                summary="Join proceeds after required branches complete.",
                required_branch_count=2,
            ),
        ),
        accessibility_summary=(
            "Graph details are also available through keyboard-accessible "
            "node and edge lists."
        ),
    )


def build_validation_summary(*, blocked: bool) -> WorkflowValidationSummary:
    findings: tuple[ValidationFinding, ...] = ()
    status = WorkflowBuilderStatus.READY
    summary = "Validation passed for the current draft revision."
    if blocked:
        status = WorkflowBuilderStatus.BLOCKED
        summary = "Validation found publish blockers that require review."
        findings = (
            ValidationFinding(
                finding_id="finding-required-evidence",
                severity=WorkflowBuilderSeverity.BLOCKING,
                category="required_test_evidence",
                section="Evidence",
                message="Required Daily briefing test evidence is stale.",
                recommended_action="Run the required test suite and refresh evidence.",
                href="/admin/agent-tests/ui",
                evidence_reference_id="evidence-qa030-required-suite",
            ),
        )
    return WorkflowValidationSummary(
        validation_id="validation-qa030",
        status=status,
        revision=CURRENT_REVISION,
        generated_at_label="Generated for deterministic QA030 validation",
        summary=summary,
        findings=findings,
        artifact_reference_ids=("artifact-ref-qa030-validation",),
    )


def build_publish_readiness(
    *,
    ready: bool,
    published: bool = False,
) -> WorkflowPublishReadiness:
    if not ready:
        return WorkflowPublishReadiness(
            decision=AdminMutationStatus.VALIDATION_ERROR,
            revision=CURRENT_REVISION,
            summary="Publish is blocked until required evidence is current.",
            blockers=("Required Daily briefing test evidence is stale.",),
            warnings=("Weather branch evidence should be refreshed after save.",),
            required_evidence=(
                WorkflowEvidenceSummary(
                    evidence_id="evidence-qa030-required-suite",
                    label="Daily briefing required suite",
                    status=WorkflowBuilderStatus.BLOCKED,
                    summary="Repository-backed test evidence is stale for this draft.",
                    artifact_reference_id="artifact-ref-qa030-stale-evidence",
                    href="/admin/agent-tests/ui",
                ),
            ),
        )
    return WorkflowPublishReadiness(
        decision=AdminMutationStatus.ACCEPTED
        if published
        else AdminMutationStatus.CONFIRMATION_REQUIRED,
        revision=CURRENT_REVISION,
        summary="Publish gate is ready after validation and evidence review.",
        required_evidence=(
            WorkflowEvidenceSummary(
                evidence_id="evidence-qa030-required-suite",
                label="Daily briefing required suite",
                status=WorkflowBuilderStatus.READY,
                summary="Repository-backed test evidence is current.",
                artifact_reference_id="artifact-ref-qa030-ready-evidence",
                href="/admin/agent-tests/ui",
            ),
        ),
        confirmation=ConfirmationRequirement(
            title="Publish workflow",
            summary="Confirm publish to create an immutable workflow bundle.",
            confirm_label="Publish workflow",
        ),
        published_bundle_summary=(
            "Published bundle pins workflow, prompts, profile, provider, skills, "
            "and required evidence references."
        )
        if published
        else None,
    )


def _sections() -> tuple[BuilderSection, ...]:
    return (
        BuilderSection(
            section_id="metadata",
            label="Metadata",
            status=WorkflowBuilderStatus.READY,
            summary="Name, description, tags, and Daily Briefing pattern.",
        ),
        BuilderSection(
            section_id="references",
            label="References",
            status=WorkflowBuilderStatus.WARNING,
            summary="Prompt, profile, provider, skill, and test references.",
        ),
        BuilderSection(
            section_id="graph",
            label="Graph",
            status=WorkflowBuilderStatus.WARNING,
            summary="Nodes, edges, fan-out, joins, and approval gates.",
        ),
        BuilderSection(
            section_id="publish",
            label="Publish",
            status=WorkflowBuilderStatus.BLOCKED,
            summary="Required evidence must be current before publish.",
        ),
    )


def _revisions() -> tuple[WorkflowRevisionSummary, ...]:
    return (
        WorkflowRevisionSummary(
            revision=CURRENT_REVISION,
            created_at_label="Current revision",
            actor_label="Tenant Admin",
            change_category="draft_saved",
            summary="Updated graph references and validation evidence.",
            audit_reference_id="audit-workflow-revision-current-qa030",
            current=True,
        ),
        WorkflowRevisionSummary(
            revision="draft-rev-qa030-previous",
            created_at_label="Earlier today",
            actor_label="Platform Admin",
            change_category="graph_updated",
            summary="Added weather branch and required join policy.",
            audit_reference_id="audit-workflow-revision-previous-qa030",
        ),
    )


def _json_inspector() -> WorkflowJsonInspector:
    return WorkflowJsonInspector(
        collapsed_by_default=True,
        summary="Advanced JSON is read-only and redacted.",
        redaction_summary=(
            "Prompts, completions, memory, credentials, provider responses, "
            "channel messages, and connector outputs are summarized."
        ),
        safe_document_preview={
            "workflow": "Daily briefing workflow",
            "revision": CURRENT_REVISION,
            "graph": "4 nodes, 4 edges, 1 join policy",
        },
        artifact_reference_id="artifact-ref-qa030-json-preview",
    )


def _draft_action_href(
    draft_id: str,
    action: str,
    scope: ReactAdminScope,
) -> str:
    return _with_tenant_query(f"/admin/app/workflows/drafts/{draft_id}/{action}", scope)


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
