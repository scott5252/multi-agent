from __future__ import annotations

import json
from typing import TYPE_CHECKING
from uuid import UUID

from multi_agent_platform.api.ui.admin_console import AdminScope, NavigationOutcome
from multi_agent_platform.audit.capture import AuditCaptureService
from multi_agent_platform.audit.inspection import (
    TimelineView,
    assemble_replay_events,
    assemble_timeline,
    build_lineage_graph,
)
from multi_agent_platform.audit.models import (
    AuditEventCreate,
    AuthorizationOutcome,
    CaptureCriticality,
    DebugEvidenceExportCreate,
    InspectionAction,
    TimelineEventCategory,
    TimelineEventCreate,
)
from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    DebugEvidenceExportRecord,
    VersionBundleSnapshotRecord,
)
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.observability.logging import redact_mapping

if TYPE_CHECKING:
    from multi_agent_platform.auth.principal import PrincipalContext


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    async def record(self, event: AuditEventCreate) -> AuditEvent:
        audit_event = AuditEvent(
            tenant_id=event.tenant_id,
            scope_type=event.scope_type,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            trace_id=event.trace_id,
            request_id=event.request_id,
            payload_redacted=redact_mapping(event.payload_redacted),
            occurred_at=event.occurred_at,
        )
        return await self.repository.create(audit_event)

    async def record_workflow_event(
        self,
        *,
        principal: PrincipalContext,
        scope_type: str,
        tenant_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: str,
        trace_id: str,
        request_id: str | None,
        payload_redacted: dict[str, str],
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=tenant_id,
                scope_type=scope_type,
                actor_type=AuditActorType.USER,
                actor_id=principal.principal_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                trace_id=trace_id,
                request_id=request_id,
                payload_redacted=payload_redacted,
            )
        )

    async def record_runtime_event(
        self,
        *,
        tenant_id: UUID | None,
        scope_type: str,
        action: str,
        workflow_run_id: UUID,
        trace_id: str,
        payload_redacted: dict[str, str],
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=tenant_id,
                scope_type=scope_type,
                actor_type=AuditActorType.SYSTEM,
                actor_id="runtime",
                action=action,
                entity_type="workflow_run",
                entity_id=str(workflow_run_id),
                trace_id=trace_id,
                payload_redacted=payload_redacted,
            )
        )

    async def record_reliability_event(
        self,
        *,
        tenant_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: str,
        trace_id: str,
        payload_redacted: dict[str, str],
        scope_type: str = "tenant",
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=tenant_id,
                scope_type=scope_type,
                actor_type=AuditActorType.SYSTEM,
                actor_id="reliability",
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                trace_id=trace_id,
                payload_redacted=payload_redacted,
            )
        )

    async def record_admin_navigation_visibility(
        self,
        *,
        principal: PrincipalContext,
        active_scope: AdminScope,
        request_path: str,
        outcomes: list[NavigationOutcome] | tuple[NavigationOutcome, ...],
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=active_scope.tenant_id,
                scope_type=active_scope.scope_type,
                actor_type=AuditActorType.USER,
                actor_id=principal.principal_id,
                action="admin_shell.navigation_visibility",
                entity_type="admin_shell",
                entity_id=request_path,
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted={
                    "active_scope": active_scope.scope_type,
                    "tenant_id": str(active_scope.tenant_id)
                    if active_scope.tenant_id is not None
                    else "none",
                    "request_path": request_path,
                    "role_context": ",".join(principal.role_codes),
                    "item_outcomes": json.dumps(
                        [outcome.model_dump(mode="json") for outcome in outcomes],
                        sort_keys=True,
                    ),
                },
            )
        )

    async def record_admin_scope_selection(
        self,
        *,
        principal: PrincipalContext,
        active_scope: AdminScope,
        selected_scope: AdminScope,
        outcome: str,
        reason_category: str,
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=selected_scope.tenant_id,
                scope_type=selected_scope.scope_type,
                actor_type=AuditActorType.USER,
                actor_id=principal.principal_id,
                action="admin_shell.scope_selection",
                entity_type="admin_scope",
                entity_id=str(selected_scope.tenant_id or "platform"),
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted={
                    "previous_scope": active_scope.scope_type,
                    "selected_scope": selected_scope.scope_type,
                    "outcome": outcome,
                    "reason_category": reason_category,
                },
            )
        )

    async def record_admin_filter_restore(
        self,
        *,
        principal: PrincipalContext,
        active_scope: AdminScope,
        admin_area: str,
        filter_id: str,
        outcome: str,
        reason_category: str,
    ) -> AuditEvent:
        return await self.record(
            AuditEventCreate(
                tenant_id=active_scope.tenant_id,
                scope_type=active_scope.scope_type,
                actor_type=AuditActorType.USER,
                actor_id=principal.principal_id,
                action="admin_shell.saved_filter_restore",
                entity_type="admin_saved_filter",
                entity_id=filter_id,
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted={
                    "admin_area": admin_area,
                    "outcome": outcome,
                    "reason_category": reason_category,
                },
            )
        )


class AuditDebuggingAuthorizationError(PermissionError):
    pass


class AuditDebuggingRateLimitError(RuntimeError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("debug export rate limit exceeded")
        self.retry_after_seconds = retry_after_seconds


class AuditDebuggingService:
    ADMIN_ROLES = {"tenant_admin", "platform_admin", "admin", "auditor"}
    EXPORT_LIMIT_PER_ACTOR = 5
    _export_rate_counts: dict[tuple[str, str], int] = {}

    def __init__(self, repository: AuditDebuggingRepository) -> None:
        self.repository = repository
        self.capture = AuditCaptureService(repository)

    def _role(self, principal: PrincipalContext) -> str:
        return next(iter(principal.role_codes), "unknown")

    def _is_authorized(
        self, principal: PrincipalContext, tenant_id: UUID | None
    ) -> bool:
        has_role = bool(set(principal.role_codes) & self.ADMIN_ROLES)
        same_tenant = principal.tenant_id == tenant_id or principal.tenant_id is None
        return has_role and same_tenant

    def _check_export_rate_limit(
        self, *, principal: PrincipalContext, tenant_id: UUID | None
    ) -> None:
        key = (str(tenant_id), principal.principal_id)
        count = self._export_rate_counts.get(key, 0)
        if count >= self.EXPORT_LIMIT_PER_ACTOR:
            raise AuditDebuggingRateLimitError(retry_after_seconds=60)
        self._export_rate_counts[key] = count + 1

    async def _record_access(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        action: InspectionAction,
        outcome: AuthorizationOutcome,
        workflow_run_id: UUID | None = None,
        denial_category: str | None = None,
        filters: dict[str, object] | None = None,
        export_id: UUID | None = None,
    ) -> None:
        await self.repository.create_inspection_access_event(
            tenant_id=tenant_id,
            actor_principal_id=principal.principal_id,
            actor_role=self._role(principal),
            action=action.value,
            target_run_id=workflow_run_id,
            authorization_outcome=outcome.value,
            denial_category=denial_category,
            filters=filters,
            export_id=export_id,
            trace_id=principal.trace_id,
            safe_metadata={"request_id": principal.request_id}
            if principal.request_id
            else {},
        )

    async def ensure_authorized(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        workflow_run_id: UUID | None,
        action: InspectionAction,
    ) -> None:
        if self._is_authorized(principal, tenant_id):
            return
        await self._record_access(
            principal=principal,
            tenant_id=tenant_id,
            action=action,
            outcome=AuthorizationOutcome.DENIED,
            workflow_run_id=workflow_run_id,
            denial_category="role_or_tenant_scope",
        )
        raise AuditDebuggingAuthorizationError("admin inspection denied")

    async def search_runs(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        filters: dict[str, object],
        limit: int,
    ) -> list[AuditTimelineEventRecord]:
        await self.ensure_authorized(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=None,
            action=InspectionAction.SEARCH,
        )
        await self._record_access(
            principal=principal,
            tenant_id=tenant_id,
            action=InspectionAction.SEARCH,
            outcome=AuthorizationOutcome.ALLOWED,
            filters=filters,
        )
        workflow_run_filter = filters.get("workflow_run_id")
        status_filter = filters.get("status")
        failure_category_filter = filters.get("failure_category")
        return await self.repository.search_runs(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_filter
            if isinstance(workflow_run_filter, UUID)
            else None,
            status=status_filter if isinstance(status_filter, str) else None,
            failure_category=failure_category_filter
            if isinstance(failure_category_filter, str)
            else None,
            limit=limit,
        )

    async def get_timeline(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
    ) -> TimelineView | None:
        await self.ensure_authorized(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            action=InspectionAction.TIMELINE,
        )
        events = await self.repository.list_timeline_events(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        if not events:
            await self._record_access(
                principal=principal,
                tenant_id=tenant_id,
                action=InspectionAction.TIMELINE,
                outcome=AuthorizationOutcome.NOT_FOUND,
                workflow_run_id=workflow_run_id,
            )
            return None
        traces = await self.repository.list_trace_records(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        traces_by_event: dict[UUID, list[AuditRuntimeTraceRecord]] = {}
        for trace in traces:
            traces_by_event.setdefault(trace.timeline_event_id, []).append(trace)
        bundle = await self.repository.get_version_bundle_snapshot(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        links = await self.repository.list_lineage_links(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        authorized = {workflow_run_id}
        for link in links:
            authorized.add(link.source_run_id)
            authorized.add(link.target_run_id)
        gaps = await self.repository.list_capture_gaps(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        await self._record_access(
            principal=principal,
            tenant_id=tenant_id,
            action=InspectionAction.TIMELINE,
            outcome=AuthorizationOutcome.ALLOWED,
            workflow_run_id=workflow_run_id,
        )
        return assemble_timeline(
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            events=events,
            traces_by_event=traces_by_event,
            lineage=build_lineage_graph(
                workflow_run_id=workflow_run_id,
                authorized_run_ids=authorized,
                links=links,
            ),
            bundle=bundle,
            capture_gaps=gaps,
        )

    async def get_replay(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
    ) -> list[dict[str, object]] | None:
        timeline = await self.get_timeline(
            principal=principal, tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
        if timeline is None:
            return None
        return assemble_replay_events(timeline.events)

    async def get_bundle(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
    ) -> VersionBundleSnapshotRecord | None:
        await self.ensure_authorized(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            action=InspectionAction.BUNDLE,
        )
        await self._record_access(
            principal=principal,
            tenant_id=tenant_id,
            action=InspectionAction.BUNDLE,
            outcome=AuthorizationOutcome.ALLOWED,
            workflow_run_id=workflow_run_id,
        )
        return await self.repository.get_version_bundle_snapshot(
            tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )

    async def create_export(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        lineage_scope: str,
        recipient_scope: str,
        included_sections: list[str],
        excluded_sections: list[str],
    ) -> DebugEvidenceExportRecord:
        await self.ensure_authorized(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            action=InspectionAction.EXPORT_CREATE,
        )
        requested_by = principal.principal_id
        existing = await self.repository.find_export(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            requested_by=requested_by,
            lineage_scope=lineage_scope,
            recipient_scope=recipient_scope,
            included_sections=included_sections,
        )
        if existing is not None:
            return existing
        self._check_export_rate_limit(principal=principal, tenant_id=tenant_id)
        export = await self.repository.create_export(
            DebugEvidenceExportCreate(
                tenant_id=tenant_id,
                requested_by=requested_by,
                workflow_run_id=workflow_run_id,
                lineage_scope=lineage_scope,
                recipient_scope=recipient_scope,
                included_sections=included_sections,
                excluded_sections=excluded_sections,
            )
        )
        await self._record_access(
            principal=principal,
            tenant_id=tenant_id,
            action=InspectionAction.EXPORT_CREATE,
            outcome=AuthorizationOutcome.ALLOWED,
            workflow_run_id=workflow_run_id,
            export_id=export.debug_evidence_export_id,
        )
        return export

    async def capture_denied_access(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        actor_principal_id: str,
        trace_id: str,
        safe_reason: str,
    ) -> None:
        await self.capture.record_event(
            TimelineEventCreate(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_category=TimelineEventCategory.INSPECTION_DENIED,
                trace_id=trace_id,
                source_event_id=f"denied:{actor_principal_id}:{trace_id}",
                criticality=CaptureCriticality.SECURITY_GOVERNANCE,
                safe_summary="Denied admin run inspection",
                safe_details={"safe_reason": safe_reason},
            )
        )
