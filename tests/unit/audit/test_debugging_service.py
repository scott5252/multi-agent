from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from multi_agent_platform.audit.capture import build_lifecycle_event, build_trace_record
from multi_agent_platform.audit.models import (
    CaptureGapCreate,
    LineageRelationship,
    RunLineageLinkCreate,
    RunStatusAfter,
    TimelineEventCategory,
    TraceType,
    VersionBundleSnapshotCreate,
)
from multi_agent_platform.audit.service import (
    AuditDebuggingAuthorizationError,
    AuditDebuggingService,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.audit_debugging import (
    InspectionAccessAuditEventRecord,
)
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_debugging_service_assembles_timeline_replay_bundle_search_and_export(
    session,
) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    child_id = uuid4()
    repository = AuditDebuggingRepository(session)
    service = AuditDebuggingService(repository)
    principal = PrincipalContext(
        principal_id="admin",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
        trace_id="trace",
    )
    event = await repository.create_timeline_event(
        build_lifecycle_event(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            category=TimelineEventCategory.STARTED,
            status_after=RunStatusAfter.RUNNING,
            trace_id="trace",
            source_event_id="started",
            details={"safe_reason": "started"},
        )
    )
    await repository.create_trace_record(
        build_trace_record(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            timeline_event_id=event.timeline_event_id,
            trace_type=TraceType.MODEL_SELECTION,
            trace_id="trace",
            metadata={"model_id": "safe-model"},
        )
    )
    await repository.create_capture_gap(
        CaptureGapCreate(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            timeline_event_id=event.timeline_event_id,
            trace_id="trace",
            gap_type="diagnostic_unavailable",
            affected_trace_type=TraceType.TOOL_USAGE,
            safe_reason="tool output unavailable",
        )
    )
    await repository.create_version_bundle_snapshot(
        VersionBundleSnapshotCreate(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            bundle_digest="digest",
            workflow_version={"workflow_id": "wf"},
        )
    )
    await repository.create_lineage_link(
        RunLineageLinkCreate(
            tenant_id=tenant_id,
            source_run_id=run_id,
            target_run_id=child_id,
            relationship_type=LineageRelationship.PARENT_CHILD,
            safe_reason="delegated child",
        )
    )

    timeline = await service.get_timeline(
        principal=principal, tenant_id=tenant_id, workflow_run_id=run_id
    )
    assert timeline is not None
    assert timeline.events[0]["traces"][0]["trace_type"] == "model_selection"
    assert timeline.capture_gaps[0]["gap_type"] == "diagnostic_unavailable"
    replay = await service.get_replay(
        principal=principal, tenant_id=tenant_id, workflow_run_id=run_id
    )
    assert replay is not None
    assert replay[0]["event_category"] == "started"
    bundle = await service.get_bundle(
        principal=principal, tenant_id=tenant_id, workflow_run_id=run_id
    )
    assert bundle is not None
    assert bundle.bundle_digest == "digest"
    results = await service.search_runs(
        principal=principal,
        tenant_id=tenant_id,
        filters={"status": "running"},
        limit=10,
    )
    assert results[0].workflow_run_id == run_id
    export = await service.create_export(
        principal=principal,
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        lineage_scope="authorized_children",
        recipient_scope="tenant_auditor",
        included_sections=["timeline", "trace"],
        excluded_sections=["raw_payloads"],
    )
    assert export.status == "requested"


async def test_debugging_service_denies_cross_tenant_and_audits_attempt(
    session,
) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    service = AuditDebuggingService(repository)
    principal = PrincipalContext(
        principal_id="operator",
        tenant_id=uuid4(),
        role_codes=("operator",),
        trace_id="trace-denied",
    )
    with pytest.raises(AuditDebuggingAuthorizationError):
        await service.get_timeline(
            principal=principal, tenant_id=tenant_id, workflow_run_id=run_id
        )
    records = (
        (await session.execute(select(InspectionAccessAuditEventRecord)))
        .scalars()
        .all()
    )
    assert records[0].authorization_outcome == "denied"
