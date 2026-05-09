from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from uuid import UUID

from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    AdminSortDirection,
    ConfirmationRequirement,
    IdempotencyReplay,
    PaginationState,
    RevisionConflict,
    SortField,
    SortingState,
    ToastHint,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminActionMetadata,
    ReactAdminActionMetadataSource,
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminScopeType,
    ReactAdminShellState,
    ReactAdminShellStateKind,
    ReactAdminSourceKind,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    WORKFLOW_BUILDER_UNSAFE_MARKERS,
    BuilderMutationResult,
    BuilderSection,
    ValidationFinding,
    WorkflowBuilderEnvelope,
    WorkflowBuilderSeverity,
    WorkflowBuilderStatus,
    WorkflowCreateEnvelope,
    WorkflowCreateTemplate,
    WorkflowEvidenceSummary,
    WorkflowGraphEdge,
    WorkflowGraphNode,
    WorkflowGraphPreview,
    WorkflowJoinPolicySummary,
    WorkflowJsonInspector,
    WorkflowLegacyRouteMapping,
    WorkflowPublishReadiness,
    WorkflowReferenceCatalog,
    WorkflowReferenceOption,
    WorkflowRegistryEnvelope,
    WorkflowRegistryItem,
    WorkflowRevisionSummary,
    WorkflowSharingSummary,
    WorkflowValidationSummary,
    WorkflowVersionDetail,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    WorkflowDraftDocument as WorkflowDraftEditorDocument,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupResponse,
    GraphPreviewResponse,
    PublishGateResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    DraftRevisionListResponse,
    ValidationFindingResponse,
    ValidationResultResponse,
    WorkflowDraftResponse,
    WorkflowVersionResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftDocument as RegistryWorkflowDraftDocument,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowRegistryItem as LiveWorkflowRegistryItem,
)
from multi_agent_platform.auth.principal import PrincipalContext


def build_workflow_registry_envelope(
    *,
    scope: ReactAdminScope,
    items: tuple[LiveWorkflowRegistryItem, ...] | list[LiveWorkflowRegistryItem] = (),
    filters: dict[str, str] | None = None,
) -> WorkflowRegistryEnvelope:
    live_items = tuple(items)
    provenance = _provenance(
        ReactAdminSourceKind.LIVE_REPOSITORY
        if live_items
        else ReactAdminSourceKind.EMPTY_LIVE_STATE,
        "Workflow registry records",
        (
            "Workflow lineages, drafts, validation state, versions, and sharing "
            "are read from durable workflow registry tables."
        ),
    )
    empty_state = None
    if not live_items:
        empty_state = _empty_state(
            title="No workflows found",
            summary=(
                "No authorized workflow lineages, active drafts, or published "
                "bundles exist for this scope."
            ),
            setup_hint="Create a workflow draft to populate the live registry.",
            provenance=provenance,
        )
    return WorkflowRegistryEnvelope(
        page_id="workflow-registry-react",
        title="Workflow registry",
        summary=(
            "Live workflow registry with draft, version, validation, evidence, "
            "and sharing summaries."
        ),
        scope=scope,
        filters=filters
        or {
            "status": "all",
            "scope_filter": "all",
            "sort": "updated_desc",
        },
        pagination=PaginationState(
            page_size=min(max(len(live_items), 1), 50),
            total_items=len(live_items),
        ),
        sorting=SortingState(
            active=SortField(
                key=(filters or {}).get("sort", "updated_desc"),
                label="Latest updated",
                direction=AdminSortDirection.DESC,
            ),
            allowed=(
                SortField(
                    key="updated_desc",
                    label="Latest updated",
                    direction=AdminSortDirection.DESC,
                ),
            ),
        ),
        items=tuple(_registry_item_from_live(item, scope) for item in live_items),
        create_action=AdminAction(
            action_id="workflow-create",
            label="Create workflow",
            method=AdminActionMethod.GET,
            href=_with_tenant_query("/admin/app/workflows/new", scope),
            variant=ReactAdminPageActionVariant.PRIMARY,
        ),
        provenance=provenance,
        empty_state=empty_state,
    )


def build_workflow_create_envelope(*, scope: ReactAdminScope) -> WorkflowCreateEnvelope:
    provenance = _provenance(
        ReactAdminSourceKind.COMPUTED_METADATA,
        "Workflow create actions",
        (
            "Create metadata is computed from backend workflow authoring "
            "capabilities and the active scope."
        ),
    )
    return WorkflowCreateEnvelope(
        page_id="workflow-create-react",
        title="Create workflow",
        summary="Start a durable workflow draft through the workflow registry service.",
        templates=(
            WorkflowCreateTemplate(
                template_id="blank_workflow",
                label="Blank workflow",
                summary=(
                    "Creates a tenant-scoped draft with no synthetic domain records."
                ),
                workflow_kind="main_workflow",
                href=_with_tenant_query(
                    "/admin/app/workflows/new?template=blank", scope
                ),
            ),
        ),
        create_action=AdminAction(
            action_id="workflow-create-submit",
            label="Create draft",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/workflows", scope),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                idempotency_source=(
                    ReactAdminActionMetadataSource.GENERATED_CLIENT_STATE
                ),
            ),
        ),
        provenance=provenance,
    )


def build_workflow_builder_envelope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    registry_items: tuple[LiveWorkflowRegistryItem, ...]
    | list[LiveWorkflowRegistryItem] = (),
    draft: WorkflowDraftResponse | None = None,
    lookups: EditorLookupResponse | None = None,
    graph_preview: GraphPreviewResponse | None = None,
    revisions: DraftRevisionListResponse | None = None,
    publish_gate: PublishGateResponse | None = None,
    version: WorkflowVersionResponse | None = None,
) -> WorkflowBuilderEnvelope:
    _ = principal
    registry = build_workflow_registry_envelope(
        scope=scope, items=tuple(registry_items)
    )
    create_state = build_workflow_create_envelope(scope=scope)
    reference_catalog = build_reference_catalog(scope=scope, lookups=lookups)
    legacy_routes = build_workflow_legacy_route_mappings(scope=scope)
    if draft is None:
        provenance = _provenance(
            ReactAdminSourceKind.EMPTY_LIVE_STATE,
            "Workflow builder records",
            "No active durable workflow draft is available for the active scope.",
        )
        empty_state = _empty_state(
            title="No active workflow draft",
            summary="Create a workflow draft before opening the builder.",
            setup_hint="Use the create action to start a durable workflow draft.",
            provenance=provenance,
        )
        return WorkflowBuilderEnvelope(
            page_id="react-workflow-builder",
            title="Workflow builder",
            description=(
                "Guided workflow drafting with backend validation, graph review, "
                "required evidence, and publish gates."
            ),
            scope=scope,
            registry=registry,
            create_state=create_state,
            reference_catalog=reference_catalog,
            legacy_routes=legacy_routes,
            state=ReactAdminShellState(
                state=ReactAdminShellStateKind.EMPTY,
                title=empty_state.title,
                summary=empty_state.summary,
                action=None,
                provenance=provenance,
                empty_state=empty_state,
            ),
            provenance=provenance,
            empty_state=empty_state,
        )

    validation = build_validation_summary(
        draft=draft, validation=draft.latest_validation
    )
    published = (
        version is not None
        and version.published_from_draft_id == draft.workflow_draft_id
        and version.published_from_revision_id
        == draft.latest_revision.workflow_draft_revision_id
    )
    publish_readiness = build_publish_readiness(
        draft=draft,
        gate=publish_gate,
        published=published,
    )
    sections = _sections_from_draft(
        draft=draft, validation=validation, publish=publish_readiness
    )
    draft_document = _draft_document_from_live(
        draft,
        graph_preview,
        section_summaries=sections,
    )
    return WorkflowBuilderEnvelope(
        page_id="react-workflow-builder",
        title="Workflow builder",
        description=(
            "Guided workflow drafting with backend validation, graph review, "
            "required evidence, and publish gates."
        ),
        scope=scope,
        registry=registry,
        create_state=create_state,
        draft=draft_document,
        sections=sections,
        reference_catalog=reference_catalog,
        validation=validation,
        publish_readiness=publish_readiness,
        revisions=_revisions_from_live(revisions, draft=draft),
        version_detail=build_workflow_version_detail(scope=scope, version=version),
        sharing=build_workflow_sharing_summary(scope=scope, version=version),
        legacy_routes=legacy_routes,
        json_inspector=_json_inspector_from_draft(
            draft=draft, graph=draft_document.graph
        ),
        actions=_draft_actions(draft=draft, scope=scope),
        provenance=_provenance(
            ReactAdminSourceKind.LIVE_REPOSITORY,
            "Workflow draft records",
            (
                "Draft document, revisions, validation, graph, publish readiness, "
                "and sharing summaries are projected from durable workflow records."
            ),
        ),
    )


def build_workflow_version_detail(
    *,
    scope: ReactAdminScope,
    version: WorkflowVersionResponse | None = None,
) -> WorkflowVersionDetail | None:
    _ = scope
    if version is None:
        return None
    digest = version.compiled_bundle_digest or "digest unavailable"
    return WorkflowVersionDetail(
        workflow_version_bundle_id=str(version.workflow_version_bundle_id),
        display_name=version.display_name,
        display_version=version.display_version,
        digest_label=f"Digest {digest[:16]}",
        summary=(
            f"Published {version.status} workflow bundle from durable registry state."
        ),
        href=f"/admin/app/workflows/versions/{version.workflow_version_bundle_id}",
    )


def build_workflow_sharing_summary(
    *,
    scope: ReactAdminScope,
    version: WorkflowVersionResponse | None = None,
) -> WorkflowSharingSummary:
    if version is None:
        return WorkflowSharingSummary(
            status=WorkflowBuilderStatus.UNAVAILABLE,
            summary="Sharing is available after a workflow bundle is published.",
            grants_label="No published bundle selected",
            actions=(),
        )
    grant_count = len(version.sharing_grants)
    return WorkflowSharingSummary(
        status=WorkflowBuilderStatus.READY,
        summary="Sharing summary is derived from durable workflow version grants.",
        grants_label=(
            f"{grant_count} active sharing grant{'s' if grant_count != 1 else ''}"
        ),
        actions=(
            AdminAction(
                action_id="workflow-sharing-review",
                label="Review sharing",
                method=AdminActionMethod.GET,
                href=_with_tenant_query("/admin/app/workflows", scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
    )


def build_workflow_legacy_route_mappings(
    *,
    scope: ReactAdminScope,
) -> tuple[WorkflowLegacyRouteMapping, ...]:
    preserved = (
        "tenant_id",
        "scope_filter",
        "status",
        "q",
        "saved_filter",
        "workflow_draft_id",
        "workflow_version_bundle_id",
        "revision",
        "conflict",
    )
    return (
        WorkflowLegacyRouteMapping(
            legacy_path="/admin/workflows/ui",
            methods=("GET",),
            react_path=_with_tenant_query("/admin/app/workflows", scope),
            preserved_parameters=preserved[:5],
            redirect_status="303",
            authorization_behavior="Backend authorization before redirect.",
            inventory_item_id="workflow-registry-index",
            evidence_references=("tests/integration/api/test_admin_workflow_ui.py",),
            retirement_outcome="redirected",
        ),
        WorkflowLegacyRouteMapping(
            legacy_path="/admin/workflows/new",
            methods=("GET", "POST"),
            react_path=_with_tenant_query("/admin/app/workflows/new", scope),
            preserved_parameters=preserved[:5],
            redirect_status="303",
            compatibility_response="POST create returns the created React draft link.",
            authorization_behavior="Backend create authorization remains required.",
            inventory_item_id="workflow-create",
            evidence_references=("tests/integration/api/test_admin_workflow_ui.py",),
            retirement_outcome="converted",
        ),
        WorkflowLegacyRouteMapping(
            legacy_path="/admin/workflows/drafts/{workflow_draft_id}/editor",
            methods=("GET",),
            react_path=_with_tenant_query(
                "/admin/app/workflows/drafts/{workflow_draft_id}",
                scope,
            ),
            preserved_parameters=preserved,
            redirect_status="303",
            authorization_behavior="Draft visibility is checked by JSON APIs.",
            inventory_item_id="workflow-draft-editor",
            evidence_references=("tests/integration/api/test_admin_workflow_ui.py",),
            retirement_outcome="redirected",
        ),
        WorkflowLegacyRouteMapping(
            legacy_path="/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui",
            methods=("GET",),
            react_path=_with_tenant_query(
                "/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate",
                scope,
            ),
            preserved_parameters=preserved,
            redirect_status="303",
            authorization_behavior="Publish readiness remains backend-owned.",
            inventory_item_id="workflow-publish-gate",
            evidence_references=("tests/integration/api/test_admin_workflow_ui.py",),
            retirement_outcome="redirected",
        ),
        WorkflowLegacyRouteMapping(
            legacy_path="/admin/workflows/versions/{workflow_version_bundle_id}/detail",
            methods=("GET",),
            react_path=_with_tenant_query(
                "/admin/app/workflows/versions/{workflow_version_bundle_id}",
                scope,
            ),
            preserved_parameters=preserved,
            redirect_status="303",
            authorization_behavior="Version visibility is checked by JSON APIs.",
            inventory_item_id="workflow-version-detail",
            evidence_references=("tests/integration/api/test_admin_workflow_ui.py",),
            retirement_outcome="redirected",
        ),
    )


def build_reference_catalog(
    *,
    scope: ReactAdminScope,
    lookups: EditorLookupResponse | None = None,
) -> WorkflowReferenceCatalog:
    _ = scope
    if lookups is None:
        return WorkflowReferenceCatalog()
    grouped: dict[str, list[WorkflowReferenceOption]] = {
        "prompt": [],
        "runtime_profile": [],
        "model_route": [],
        "skill": [],
        "test_suite": [],
        "subworkflow": [],
    }
    for group in lookups.groups:
        for option in group.options:
            disabled = bool(getattr(option, "disabled", False))
            projected = WorkflowReferenceOption(
                reference_id=option.value or option.option_id,
                label=option.label,
                kind=group.lookup_kind,
                readiness_status=_status_from_lookup(option.status, disabled),
                tenant_eligible=not disabled,
                version_label=_metadata_label(option.metadata),
                safe_summary=option.description or f"{option.status} reference option",
                href=option.detail_url,
            )
            key = _lookup_group_key(group.lookup_kind)
            grouped.setdefault(key, []).append(projected)
    return WorkflowReferenceCatalog(
        prompt_options=tuple(grouped.get("prompt", ())),
        profile_options=tuple(grouped.get("runtime_profile", ())),
        provider_options=tuple(grouped.get("model_route", ())),
        skill_options=tuple(grouped.get("skill", ())),
        test_suite_options=tuple(grouped.get("test_suite", ())),
        subworkflow_options=tuple(grouped.get("subworkflow", ())),
    )


def build_save_result(
    *,
    draft: WorkflowDraftResponse | None = None,
    conflict: RevisionConflict | None = None,
    editor_state: WorkflowDraftEditorDocument | None = None,
    idempotency_key: str | None = None,
    replayed: bool = False,
) -> BuilderMutationResult:
    if conflict is not None:
        return BuilderMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary=conflict.message,
            stale_conflict=conflict,
        )
    if draft is None:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Workflow draft save did not return durable state.",
        )
    revision = _revision_label(draft)
    return BuilderMutationResult(
        status=AdminMutationStatus.IDEMPOTENT_REPLAY
        if replayed
        else AdminMutationStatus.ACCEPTED,
        summary=(
            "Workflow draft save was already applied for this idempotency key."
            if replayed
            else "Draft saved as a durable workflow revision."
        ),
        revision=revision,
        editor_state=editor_state,
        validation=build_validation_summary(
            draft=draft, validation=draft.latest_validation
        ),
        idempotency=IdempotencyReplay(
            idempotency_key=idempotency_key,
            replayed=True,
            original_result_reference=(
                f"workflow-draft:{draft.workflow_draft_id}:revision:"
                f"{draft.current_revision_number}"
            ),
            summary="Exact duplicate workflow save replayed without a new revision.",
        )
        if replayed and idempotency_key is not None
        else None,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Draft save replayed" if replayed else "Draft saved",
            summary=(
                "The durable workflow revision was already current."
                if replayed
                else "The latest durable workflow revision is now current."
            ),
        ),
        audit_reference_id=f"workflow-draft:{draft.workflow_draft_id}:revision:{draft.current_revision_number}",
    )


def build_create_result(
    *,
    draft: WorkflowDraftResponse | None = None,
    scope: ReactAdminScope,
) -> BuilderMutationResult:
    if draft is None:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Workflow draft create did not return durable state.",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow draft created through durable registry state.",
        revision=_revision_label(draft),
        validation=build_validation_summary(
            draft=draft,
            validation=draft.latest_validation,
        ),
        next_action=AdminAction(
            action_id="workflow-open-created-draft",
            label="Open draft",
            method=AdminActionMethod.GET,
            href=_with_tenant_query(
                f"/admin/app/workflows/drafts/{draft.workflow_draft_id}",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
        ),
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Workflow created",
            summary="A durable workflow draft is ready to edit.",
        ),
        audit_reference_id=f"workflow-draft:{draft.workflow_draft_id}:created",
    )


def build_document_save_validation_result(
    *,
    revision: str,
    findings: Sequence[ValidationFinding],
    summary: str = "Workflow document has blocking validation findings.",
    audit_reference_id: str | None = None,
) -> BuilderMutationResult:
    return BuilderMutationResult(
        status=AdminMutationStatus.VALIDATION_ERROR,
        summary=summary,
        revision=revision,
        validation=WorkflowValidationSummary(
            validation_id=f"workflow-document-save-validation:{revision}",
            status=WorkflowBuilderStatus.BLOCKED,
            revision=revision,
            generated_at_label="Pre-save validation",
            summary=summary,
            findings=tuple(findings),
            artifact_reference_ids=(),
        ),
        audit_reference_id=audit_reference_id,
    )


def build_restore_result(
    *,
    draft: WorkflowDraftResponse | None = None,
    conflict: RevisionConflict | None = None,
) -> BuilderMutationResult:
    if conflict is not None:
        return BuilderMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary=conflict.message,
            stale_conflict=conflict,
        )
    if draft is None:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Workflow revision restore did not return durable state.",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow revision restored as the current durable draft revision.",
        revision=_revision_label(draft),
        validation=build_validation_summary(
            draft=draft,
            validation=draft.latest_validation,
        ),
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Revision restored",
            summary="The selected revision is now the current durable draft.",
        ),
        audit_reference_id=(
            f"workflow-draft:{draft.workflow_draft_id}:revision:"
            f"{draft.current_revision_number}"
        ),
    )


def build_copy_result(
    *,
    draft: WorkflowDraftResponse | None = None,
    scope: ReactAdminScope,
) -> BuilderMutationResult:
    if draft is None:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Workflow copy did not return durable state.",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow draft copied into a new durable lineage.",
        revision=_revision_label(draft),
        validation=build_validation_summary(
            draft=draft,
            validation=draft.latest_validation,
        ),
        next_action=AdminAction(
            action_id="workflow-open-copied-draft",
            label="Open copied draft",
            method=AdminActionMethod.GET,
            href=_with_tenant_query(
                f"/admin/app/workflows/drafts/{draft.workflow_draft_id}",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
        ),
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Workflow copied",
            summary="A copied durable workflow draft is ready to edit.",
        ),
        audit_reference_id=f"workflow-draft:{draft.workflow_draft_id}:copied",
    )


def build_validation_result(
    *,
    draft: WorkflowDraftResponse | None = None,
    validation: ValidationResultResponse | None = None,
    publish_gate: PublishGateResponse | None = None,
) -> BuilderMutationResult:
    if draft is None or validation is None:
        return BuilderMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Workflow validation did not return durable state.",
        )
    return BuilderMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Workflow validation completed and was persisted.",
        revision=_revision_label(draft),
        validation=build_validation_summary(draft=draft, validation=validation),
        publish_readiness=build_publish_readiness(draft=draft, gate=publish_gate),
        audit_reference_id=f"workflow-validation:{validation.validation_result_id}",
    )


def build_publish_result(
    *,
    draft: WorkflowDraftResponse,
    version: WorkflowVersionResponse | None = None,
    gate: PublishGateResponse | None = None,
    confirmation_required: bool = False,
) -> BuilderMutationResult:
    if version is not None:
        return BuilderMutationResult(
            status=AdminMutationStatus.ACCEPTED,
            summary="Workflow published as an immutable durable bundle.",
            revision=_revision_label(draft),
            publish_readiness=build_publish_readiness(
                draft=draft,
                gate=gate,
                published=True,
            ),
            toast=ToastHint(
                tone=ReactAdminNotificationTone.SUCCESS,
                title="Workflow published",
                summary="The published bundle is available for authorized runtime use.",
            ),
            audit_reference_id=f"workflow-version:{version.workflow_version_bundle_id}",
        )
    readiness = build_publish_readiness(draft=draft, gate=gate)
    return BuilderMutationResult(
        status=AdminMutationStatus.CONFIRMATION_REQUIRED
        if confirmation_required
        else AdminMutationStatus.VALIDATION_ERROR,
        summary=readiness.summary,
        revision=_revision_label(draft),
        publish_readiness=readiness,
        confirmation=readiness.confirmation if confirmation_required else None,
    )


def build_validation_summary(
    *,
    draft: WorkflowDraftResponse,
    validation: ValidationResultResponse | None,
) -> WorkflowValidationSummary:
    revision = _revision_label(draft)
    if validation is None:
        return WorkflowValidationSummary(
            validation_id=f"not-run-{draft.workflow_draft_id}",
            status=WorkflowBuilderStatus.UNAVAILABLE,
            revision=revision,
            generated_at_label="Not yet validated",
            summary=(
                "No durable validation result exists for the current draft revision."
            ),
            findings=(),
            artifact_reference_ids=(),
        )
    blocked = validation.blocking_issue_count > 0 or validation.status == "failed"
    return WorkflowValidationSummary(
        validation_id=str(validation.validation_result_id),
        status=WorkflowBuilderStatus.BLOCKED
        if blocked
        else WorkflowBuilderStatus.READY,
        revision=revision,
        generated_at_label="Latest durable validation",
        summary=(
            "Validation has blocking findings."
            if blocked
            else "Validation passed for the current draft revision."
        ),
        findings=tuple(_finding_from_live(finding) for finding in validation.findings),
        artifact_reference_ids=(),
    )


def build_publish_readiness(
    *,
    draft: WorkflowDraftResponse,
    gate: PublishGateResponse | None,
    published: bool = False,
) -> WorkflowPublishReadiness:
    revision = _revision_label(draft)
    if gate is None:
        if published:
            return WorkflowPublishReadiness(
                decision=AdminMutationStatus.ACCEPTED,
                revision=revision,
                summary="Workflow bundle has been published.",
                blockers=(),
                required_evidence=(),
                published_bundle_summary=(
                    "Published bundle pins durable workflow, validation, and evidence "
                    "references."
                ),
            )
        return WorkflowPublishReadiness(
            decision=AdminMutationStatus.VALIDATION_ERROR,
            revision=revision,
            summary="Publish readiness has not been evaluated for the current draft.",
            blockers=("Run validation and publish-gate evaluation before publishing.",),
            required_evidence=(),
        )
    ready = gate.status == "ready"
    blockers = tuple(finding.message for finding in gate.findings if finding.blocking)
    warnings = tuple(
        finding.message for finding in gate.findings if not finding.blocking
    )
    evidence = _evidence_from_gate(gate)
    return WorkflowPublishReadiness(
        decision=AdminMutationStatus.ACCEPTED
        if published
        else AdminMutationStatus.CONFIRMATION_REQUIRED
        if ready
        else AdminMutationStatus.VALIDATION_ERROR,
        revision=revision,
        summary=(
            "Workflow bundle has been published."
            if published
            else "Publish gate is ready after validation and evidence review."
            if ready
            else (
                "Publish is blocked until validation and required evidence are current."
            )
        ),
        blockers=blockers,
        warnings=warnings,
        required_evidence=evidence,
        confirmation=ConfirmationRequirement(
            title="Publish workflow",
            summary="Confirm publish to create an immutable workflow bundle.",
            confirm_label="Publish workflow",
        )
        if ready and not published
        else None,
        published_bundle_summary=(
            "Published bundle pins durable workflow, validation, and evidence "
            "references."
        )
        if published
        else None,
    )


def _registry_item_from_live(
    item: LiveWorkflowRegistryItem,
    scope: ReactAdminScope,
) -> WorkflowRegistryItem:
    actions: tuple[AdminAction, ...]
    if item.workflow_draft_id is not None:
        href = _with_tenant_query(
            f"/admin/app/workflows/drafts/{item.workflow_draft_id}",
            scope,
        )
        actions = (
            AdminAction(
                action_id="open-draft",
                label="Open draft",
                method=AdminActionMethod.GET,
                href=href,
                variant=ReactAdminPageActionVariant.PRIMARY,
            ),
            AdminAction(
                action_id="open-publish-gate",
                label="Publish gate",
                method=AdminActionMethod.GET,
                href=_with_tenant_query(
                    f"/admin/app/workflows/drafts/{item.workflow_draft_id}/publish-gate",
                    scope,
                ),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        )
    else:
        href = _with_tenant_query(
            f"/admin/app/workflows/versions/{item.workflow_version_bundle_id}",
            scope,
        )
        actions = (
            AdminAction(
                action_id="open-version",
                label="View version",
                method=AdminActionMethod.GET,
                href=href,
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        )
    return WorkflowRegistryItem(
        workflow_lineage_id=str(item.workflow_lineage_id),
        workflow_draft_id=str(item.workflow_draft_id)
        if item.workflow_draft_id
        else None,
        workflow_version_bundle_id=str(item.workflow_version_bundle_id)
        if item.workflow_version_bundle_id
        else None,
        name=item.display_name,
        workflow_kind=item.workflow_kind.value,
        status=_status_from_registry_item(item),
        owner_label="Platform workflow"
        if item.scope_type.value == "platform"
        else "Tenant workflow",
        tenant_label=_tenant_label(item=item, scope=scope),
        updated_at_label=_timestamp_label(item.updated_at),
        sharing_summary=_sharing_label(item),
        required_evidence_summary=_evidence_label(item),
        href=href,
        actions=actions,
    )


def _draft_document_from_live(
    draft: WorkflowDraftResponse,
    graph_preview: GraphPreviewResponse | None,
    *,
    section_summaries: Sequence[BuilderSection] = (),
) -> WorkflowDraftEditorDocument:
    document = draft.document
    graph = _graph_from_live(
        graph_preview,
        layout_revision=str(draft.latest_revision.workflow_draft_revision_id),
    )
    return WorkflowDraftEditorDocument(
        workflow_draft_id=str(draft.workflow_draft_id),
        workflow_draft_revision_id=str(
            draft.latest_revision.workflow_draft_revision_id
        ),
        workflow_lineage_id=str(draft.workflow_lineage_id),
        revision=_revision_label(draft),
        name=draft.display_name,
        description=draft.description or "No workflow description provided.",
        status=_status_from_draft(draft),
        tenant_label="Tenant workflow" if draft.tenant_id else None,
        metadata_summary=(
            f"{document.workflow_kind.value} / key {document.workflow_key}"
        ),
        roles_summary=(
            f"{len(document.roles)} role{'s' if len(document.roles) != 1 else ''}"
        ),
        references_summary=_references_summary(document),
        document=document,
        section_summaries=tuple(section_summaries),
        graph=graph,
    )


def _graph_from_live(
    graph_preview: GraphPreviewResponse | None,
    *,
    layout_revision: str,
) -> WorkflowGraphPreview:
    if graph_preview is None:
        return WorkflowGraphPreview(
            layout_revision=layout_revision,
            layout_is_authoritative=False,
            nodes=(),
            edges=(),
            join_policies=(),
            accessibility_summary=(
                "No graph preview is available for this workflow draft."
            ),
        )
    nodes = tuple(
        WorkflowGraphNode(
            node_id=node.id,
            label=node.label,
            node_type=node.node_type,
            status=_status_from_badges(node.badges),
            role_label=node.role_key,
            summary=f"{node.node_type} node from the stored workflow document.",
            x=(index % 4) * 220,
            y=(index // 4) * 140,
        )
        for index, node in enumerate(graph_preview.nodes)
    )
    edges = tuple(
        WorkflowGraphEdge(
            edge_id=edge.id,
            source=edge.source,
            target=edge.target,
            label=edge.label,
            condition_category=edge.edge_type,
        )
        for edge in graph_preview.edges
    )
    join_policies = tuple(
        WorkflowJoinPolicySummary(
            policy_id=f"join-{index}",
            label="Join policy",
            summary=summary,
            required_branch_count=0,
        )
        for index, summary in enumerate(graph_preview.summary.join_summaries, start=1)
    )
    return WorkflowGraphPreview(
        layout_revision=layout_revision,
        layout_is_authoritative=True,
        nodes=nodes,
        edges=edges,
        join_policies=join_policies,
        accessibility_summary=(
            f"Stored workflow graph has {graph_preview.summary.node_count} nodes and "
            f"{graph_preview.summary.edge_count} edges."
        ),
    )


def _sections_from_draft(
    *,
    draft: WorkflowDraftResponse,
    validation: WorkflowValidationSummary,
    publish: WorkflowPublishReadiness,
) -> tuple[BuilderSection, ...]:
    graph = draft.document
    return (
        BuilderSection(
            section_id="metadata",
            label="Metadata",
            status=_status_from_draft(draft),
            summary=f"{draft.display_name} revision {draft.current_revision_number}.",
        ),
        BuilderSection(
            section_id="roles",
            label="Roles",
            status=WorkflowBuilderStatus.READY
            if graph.roles
            else WorkflowBuilderStatus.WARNING,
            summary=f"{len(graph.roles)} role definitions.",
        ),
        BuilderSection(
            section_id="references",
            label="References",
            status=WorkflowBuilderStatus.READY,
            summary=_references_summary(graph),
        ),
        BuilderSection(
            section_id="contracts",
            label="Contracts",
            status=WorkflowBuilderStatus.READY
            if graph.contracts
            else WorkflowBuilderStatus.WARNING,
            summary=f"{len(graph.contracts)} workflow contracts.",
        ),
        BuilderSection(
            section_id="graph",
            label="Graph",
            status=validation.status,
            summary=(
                f"{len(graph.nodes)} nodes and {len(graph.edges)} edges in "
                "the stored document."
            ),
        ),
        BuilderSection(
            section_id="joins",
            label="Joins",
            status=WorkflowBuilderStatus.READY,
            summary=f"{len(graph.join_policies)} join policies.",
        ),
        BuilderSection(
            section_id="approvals",
            label="Approvals",
            status=WorkflowBuilderStatus.READY,
            summary=f"{len(graph.approval_gates)} approval gates.",
        ),
        BuilderSection(
            section_id="subworkflows",
            label="Subworkflows",
            status=WorkflowBuilderStatus.READY,
            summary=f"{len(graph.subworkflow_refs)} subworkflow references.",
        ),
        BuilderSection(
            section_id="tests",
            label="Tests",
            status=WorkflowBuilderStatus.READY
            if graph.test_requirements
            else WorkflowBuilderStatus.WARNING,
            summary=f"{len(graph.test_requirements)} required test entries.",
        ),
        BuilderSection(
            section_id="annotations",
            label="Annotations",
            status=WorkflowBuilderStatus.READY,
            summary=(
                f"{len(graph.editor_annotations.section_notes)} section notes "
                "and graph layout metadata."
            ),
        ),
        BuilderSection(
            section_id="publish",
            label="Publish",
            status=WorkflowBuilderStatus.READY
            if publish.decision
            in {AdminMutationStatus.ACCEPTED, AdminMutationStatus.CONFIRMATION_REQUIRED}
            else WorkflowBuilderStatus.BLOCKED,
            summary=publish.summary,
        ),
    )


def _revisions_from_live(
    revisions: DraftRevisionListResponse | None,
    *,
    draft: WorkflowDraftResponse,
) -> tuple[WorkflowRevisionSummary, ...]:
    if revisions is None:
        revision = draft.latest_revision
        return (
            WorkflowRevisionSummary(
                revision=_revision_label(draft),
                created_at_label=_timestamp_label(revision.created_at),
                actor_label="Workflow author",
                change_category="latest_revision",
                summary=revision.change_summary or "Latest durable workflow revision.",
                audit_reference_id=f"workflow-revision:{revision.workflow_draft_revision_id}",
                current=True,
            ),
        )
    return tuple(
        WorkflowRevisionSummary(
            revision=str(item.revision_number),
            created_at_label=_timestamp_label(item.created_at),
            actor_label="Workflow author",
            change_category="draft_revision",
            summary=item.change_summary or "Durable workflow draft revision.",
            audit_reference_id=f"workflow-revision:{item.workflow_draft_revision_id}",
            current=item.revision_number == revisions.current_revision_number,
        )
        for item in revisions.revisions
    )


def _json_inspector_from_draft(
    *,
    draft: WorkflowDraftResponse,
    graph: WorkflowGraphPreview,
) -> WorkflowJsonInspector:
    return WorkflowJsonInspector(
        collapsed_by_default=True,
        summary="Advanced JSON is read-only and redacted.",
        redaction_summary=(
            "Prompts, completions, memory, credentials, provider responses, "
            "channel messages, and connector outputs are summarized."
        ),
        safe_document_preview={
            "workflow": draft.document.workflow_key,
            "revision": str(draft.current_revision_number),
            "graph": f"{len(graph.nodes)} nodes, {len(graph.edges)} edges",
        },
        artifact_reference_id=None,
    )


def _draft_actions(
    *,
    draft: WorkflowDraftResponse,
    scope: ReactAdminScope,
) -> tuple[AdminAction, ...]:
    revision = _revision_label(draft)
    metadata = ReactAdminActionMetadata(
        revision=revision,
        revision_source=ReactAdminActionMetadataSource.BACKEND,
        idempotency_source=ReactAdminActionMetadataSource.GENERATED_CLIENT_STATE,
    )
    return (
        AdminAction(
            action_id="workflow-save",
            label="Save draft",
            method=AdminActionMethod.POST,
            href=_draft_action_href(draft.workflow_draft_id, "save", scope),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            action_metadata=metadata,
        ),
        AdminAction(
            action_id="workflow-validate",
            label="Run validation",
            method=AdminActionMethod.POST,
            href=_draft_action_href(draft.workflow_draft_id, "validate", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
            action_metadata=metadata,
        ),
        AdminAction(
            action_id="workflow-publish",
            label="Review publish",
            method=AdminActionMethod.POST,
            href=_draft_action_href(draft.workflow_draft_id, "publish", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_confirmation=True,
            confirmation=ConfirmationRequirement(
                title="Publish workflow",
                summary=(
                    "Publish only after validation and required evidence are current."
                ),
                confirm_label="Publish workflow",
            ),
            action_metadata=metadata,
        ),
    )


def _finding_from_live(finding: ValidationFindingResponse) -> ValidationFinding:
    return ValidationFinding(
        finding_id=finding.code or finding.field_path or finding.category,
        severity=WorkflowBuilderSeverity.BLOCKING
        if finding.blocking
        else WorkflowBuilderSeverity.WARNING
        if finding.severity in {"warning", "advisory"}
        else WorkflowBuilderSeverity.INFO,
        category=finding.category,
        section=finding.section_key or finding.field_path or "workflow",
        field_path=finding.field_path,
        graph_element_id=finding.graph_element_id,
        message=finding.message,
        recommended_action=finding.remediation or "Review the workflow document.",
        href=finding.safe_links[0] if finding.safe_links else None,
        evidence_reference_id=finding.reference_id,
    )


def findings_from_authoring_validation(
    findings: Sequence[dict[str, object]],
) -> tuple[ValidationFinding, ...]:
    return tuple(
        _finding_from_authoring_validation(finding, index=index)
        for index, finding in enumerate(findings, start=1)
    )


def findings_from_pydantic_error(exc: ValidationError) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for index, error in enumerate(exc.errors(include_url=False), start=1):
        location = ".".join(str(part) for part in error.get("loc", ())) or "document"
        message = str(error.get("msg", "Document field is invalid."))
        section = _section_from_field_path(location)
        if section == "metadata":
            section = _section_from_validation_message(message)
        findings.append(
            ValidationFinding(
                finding_id=f"document.shape.{index}",
                severity=WorkflowBuilderSeverity.BLOCKING,
                category="document",
                section=section,
                field_path=location,
                message=message,
                recommended_action=(
                    "Update the referenced workflow document field and save again."
                ),
                href=f"#workflow-{section}",
            )
        )
    return tuple(findings)


def workflow_document_digest(document: RegistryWorkflowDraftDocument) -> str:
    payload = document.model_dump(mode="json")
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def workflow_document_payload_digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
            "utf-8"
        )
    ).hexdigest()


def workflow_document_payload_size(payload: object) -> int:
    return len(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
            "utf-8"
        )
    )


def workflow_save_scope_hash(
    *,
    tenant_id: str | None,
    principal_id: str,
    workflow_draft_id: str,
    revision: str,
    route_family: str = "react-workflow-document-save",
) -> str:
    payload = {
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "workflow_draft_id": workflow_draft_id,
        "revision": revision,
        "route_family": route_family,
    }
    return workflow_document_payload_digest(payload)


def blocking_authoring_findings(
    document: RegistryWorkflowDraftDocument,
) -> tuple[ValidationFinding, ...]:
    from multi_agent_platform.admin.workflow_registry.validation import (
        validate_authoring_document,
    )

    visible_subworkflow_ids = {
        reference.workflow_version_ref for reference in document.subworkflow_refs
    }
    findings = validate_authoring_document(
        document,
        available_subworkflow_version_ids=visible_subworkflow_ids,
    )
    blocking = [
        finding
        for finding in findings
        if finding.get("blocking") is True
        or str(finding.get("severity", "")).lower() in {"blocking", "critical"}
    ]
    return findings_from_authoring_validation(blocking)


def oversized_document_finding(*, payload_size: int, limit: int) -> ValidationFinding:
    return ValidationFinding(
        finding_id="document.size.limit",
        severity=WorkflowBuilderSeverity.BLOCKING,
        category="document",
        section="metadata",
        field_path="document",
        message="Workflow document payload is too large to save safely.",
        recommended_action=(
            f"Reduce the workflow document below {limit} bytes before saving."
        ),
        href="#workflow-metadata",
        evidence_reference_id=f"payload-bytes:{payload_size}",
    )


def unsafe_document_findings(payload: object) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for field_path, value in _iter_document_strings(payload):
        lowered = value.lower()
        if any(marker in lowered for marker in WORKFLOW_BUILDER_UNSAFE_MARKERS) or any(
            marker in lowered
            for marker in (
                "sk-",
                "authorization:",
                "bearer ",
                "begin private key",
                "/users/",
            )
        ):
            section = _section_from_field_path(field_path)
            findings.append(
                ValidationFinding(
                    finding_id=f"document.unsafe.{len(findings) + 1}",
                    severity=WorkflowBuilderSeverity.BLOCKING,
                    category="redaction",
                    section=section,
                    field_path=field_path,
                    message="Workflow document field contains protected text.",
                    recommended_action=(
                        "Remove protected raw text and store only safe references."
                    ),
                    href=f"#workflow-{section}",
                )
            )
            if len(findings) >= 5:
                break
    return tuple(findings)


def _finding_from_authoring_validation(
    finding: dict[str, object],
    *,
    index: int,
) -> ValidationFinding:
    field_path = str(finding.get("field_path") or "")
    section = str(finding.get("section_key") or _section_from_field_path(field_path))
    severity_value = str(finding.get("severity") or "").lower()
    blocking = finding.get("blocking") is True or severity_value in {
        "blocking",
        "critical",
    }
    return ValidationFinding(
        finding_id=str(finding.get("code") or field_path or f"document.{index}"),
        severity=WorkflowBuilderSeverity.BLOCKING
        if blocking
        else WorkflowBuilderSeverity.WARNING
        if severity_value in {"warning", "advisory"}
        else WorkflowBuilderSeverity.INFO,
        category=str(finding.get("category") or section or "document"),
        section=section or "document",
        field_path=field_path or None,
        graph_element_id=str(finding.get("graph_element_id"))
        if finding.get("graph_element_id") is not None
        else None,
        message=str(finding.get("message") or "Workflow document is invalid."),
        recommended_action=str(
            finding.get("remediation")
            or "Update the referenced workflow document field and save again."
        ),
        href=f"#workflow-{section or 'metadata'}",
        evidence_reference_id=str(finding.get("reference_id"))
        if finding.get("reference_id") is not None
        else None,
    )


def _iter_document_strings(
    payload: object,
    prefix: str = "document",
) -> Iterator[tuple[str, str]]:
    if isinstance(payload, str):
        yield prefix, payload
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield from _iter_document_strings(value, f"{prefix}.{key}")
        return
    if isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from _iter_document_strings(value, f"{prefix}[{index}]")


def _section_from_field_path(field_path: str) -> str:
    if not field_path:
        return "metadata"
    normalized = (
        field_path.removeprefix("document.")
        if field_path.startswith("document.")
        else field_path
    )
    first = normalized.split("[", maxsplit=1)[0].split(".", maxsplit=1)[0]
    return {
        "display_name": "metadata",
        "description": "metadata",
        "workflow_key": "metadata",
        "workflow_kind": "metadata",
        "metadata": "metadata",
        "roles": "roles",
        "prompt_profile_references": "references",
        "skill_installations": "references",
        "contracts": "contracts",
        "nodes": "graph",
        "edges": "graph",
        "entry_node_key": "graph",
        "join_policies": "joins",
        "approval_gates": "approvals",
        "subworkflow_refs": "subworkflows",
        "test_requirements": "tests",
        "editor_annotations": "annotations",
    }.get(first, "metadata")


def _section_from_validation_message(message: str) -> str:
    lowered = message.lower()
    if any(marker in lowered for marker in ("edge", "node", "entry_node", "graph")):
        return "graph"
    if "role" in lowered:
        return "roles"
    if "join" in lowered:
        return "joins"
    if "approval" in lowered:
        return "approvals"
    if "subworkflow" in lowered:
        return "subworkflows"
    if "test" in lowered:
        return "tests"
    return "metadata"


def _evidence_from_gate(
    gate: PublishGateResponse,
) -> tuple[WorkflowEvidenceSummary, ...]:
    summary = gate.required_test_summary
    if summary.required_count == 0:
        return ()
    if summary.failing_count or summary.missing_count:
        status = WorkflowBuilderStatus.BLOCKED
    elif summary.stale_count:
        status = WorkflowBuilderStatus.WARNING
    elif summary.passing_count >= summary.required_count:
        status = WorkflowBuilderStatus.READY
    else:
        status = WorkflowBuilderStatus.UNAVAILABLE
    return (
        WorkflowEvidenceSummary(
            evidence_id="required-test-evidence",
            label="Required test evidence",
            status=status,
            summary=(
                f"{summary.passing_count} passing, {summary.failing_count} failing, "
                f"{summary.missing_count} missing, {summary.stale_count} stale."
            ),
            artifact_reference_id=None,
            href="/admin/app/test-bench",
        ),
    )


def _provenance(
    source_kind: ReactAdminSourceKind,
    source_label: str,
    source_detail: str | None = None,
) -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=source_kind,
        source_label=source_label,
        source_detail=source_detail,
    )


def _empty_state(
    *,
    title: str,
    summary: str,
    setup_hint: str,
    provenance: ReactAdminPageProvenance,
) -> ReactAdminEmptyStateMetadata:
    return ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title=title,
        summary=summary,
        setup_hint=setup_hint,
        provenance=provenance,
    )


def _status_from_registry_item(item: LiveWorkflowRegistryItem) -> WorkflowBuilderStatus:
    if item.visibility_status.value == "published":
        return WorkflowBuilderStatus.PUBLISHED
    if item.latest_validation_status == "failed":
        return WorkflowBuilderStatus.BLOCKED
    if item.publish_readiness_status == "ready":
        return WorkflowBuilderStatus.READY
    return WorkflowBuilderStatus.READY


def _status_from_draft(draft: WorkflowDraftResponse) -> WorkflowBuilderStatus:
    if draft.status == "published_source":
        return WorkflowBuilderStatus.PUBLISHED
    if draft.latest_validation and draft.latest_validation.blocking_issue_count > 0:
        return WorkflowBuilderStatus.BLOCKED
    return WorkflowBuilderStatus.READY


def _status_from_lookup(status: str, disabled: bool) -> WorkflowBuilderStatus:
    if disabled:
        return WorkflowBuilderStatus.UNAVAILABLE
    if status in {"available", "ready", "active", "published"}:
        return WorkflowBuilderStatus.READY
    if status in {"blocked", "failed", "missing"}:
        return WorkflowBuilderStatus.BLOCKED
    if status in {"stale", "warning"}:
        return WorkflowBuilderStatus.WARNING
    return WorkflowBuilderStatus.UNAVAILABLE


def _status_from_badges(badges: Sequence[object]) -> WorkflowBuilderStatus:
    for badge in badges:
        if getattr(badge, "blocking", False):
            return WorkflowBuilderStatus.BLOCKED
    return WorkflowBuilderStatus.READY


def _lookup_group_key(kind: str) -> str:
    normalized = kind.lower()
    if "prompt" in normalized:
        return "prompt"
    if "profile" in normalized:
        return "runtime_profile"
    if "provider" in normalized or "model" in normalized:
        return "model_route"
    if "skill" in normalized:
        return "skill"
    if "test" in normalized or "suite" in normalized:
        return "test_suite"
    if "subworkflow" in normalized or "workflow" in normalized:
        return "subworkflow"
    return "skill"


def _metadata_label(metadata: dict[str, object]) -> str | None:
    for key in ("version", "semantic_version", "display_version"):
        value = metadata.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _tenant_label(
    *,
    item: LiveWorkflowRegistryItem,
    scope: ReactAdminScope,
) -> str | None:
    if item.tenant_id is None or scope.scope_type != ReactAdminScopeType.TENANT:
        return None
    if scope.tenant_id is not None and str(item.tenant_id) == str(scope.tenant_id):
        return scope.label
    return None


def _sharing_label(item: LiveWorkflowRegistryItem) -> str:
    if item.visibility_status.value == "published":
        return "Published bundle sharing is backed by durable grants."
    return "Draft visibility follows workflow scope authorization."


def _evidence_label(item: LiveWorkflowRegistryItem) -> str:
    if item.publish_readiness_status == "ready":
        return "Required evidence is ready for publish."
    if item.latest_validation_status == "failed":
        return "Validation findings block publish readiness."
    if item.latest_validation_status:
        return f"Latest validation status is {item.latest_validation_status}."
    return "Publish readiness has not been evaluated."


def _references_summary(document: object) -> str:
    prompt_refs = len(getattr(document, "prompt_profile_references", ()))
    skills = len(getattr(document, "skill_installations", ()))
    tests = len(getattr(document, "test_requirements", ()))
    subworkflows = len(getattr(document, "subworkflow_refs", ()))
    return (
        f"{prompt_refs} prompt/profile references, {skills} skill installations, "
        f"{tests} required tests, {subworkflows} subworkflow references."
    )


def _revision_label(draft: WorkflowDraftResponse) -> str:
    return str(draft.current_revision_number)


def _timestamp_label(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _draft_action_href(
    draft_id: str | UUID,
    action: str,
    scope: ReactAdminScope,
) -> str:
    return _with_tenant_query(f"/admin/app/workflows/drafts/{draft_id}/{action}", scope)


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
