from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from multi_agent_platform.api.routers import admin_run_inspection as router
from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentCommunicationGraph,
    AgentGraphAccessibility,
    AgentGraphProvenance,
    AgentGraphSource,
    AgentGraphState,
)
from multi_agent_platform.api.schemas.audit_debugging import (
    CreateDebugEvidenceExportRequest,
)
from multi_agent_platform.audit.inspection import TimelineView
from multi_agent_platform.audit.service import (
    AuditDebuggingAuthorizationError,
    AuditDebuggingRateLimitError,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.tenancy.context import ScopeType


def _principal(tenant_id: UUID) -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin-acme",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
        scope_type=ScopeType.TENANT,
        trace_id="trace-router-test",
    )


def _request(*, accept: str = "application/json", query: bytes = b"") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/admin/runs",
            "query_string": query,
            "headers": [(b"accept", accept.encode())],
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }
    )


def _timeline_view(workflow_run_id: UUID, tenant_id: UUID) -> TimelineView:
    now = datetime.now(UTC)
    return TimelineView(
        run={
            "workflow_run_id": workflow_run_id,
            "tenant_id": tenant_id,
            "status": "running",
            "trace_id": "trace-router-test",
            "latest_event_at": now,
        },
        events=[
            {
                "timeline_event_id": uuid4(),
                "sequence": 1,
                "event_category": "started",
                "run_status_after": "running",
                "trace_id": "trace-router-test",
                "correlation_id": None,
                "occurred_at": now,
                "recorded_at": now,
                "safe_summary": "Run started safely.",
                "safe_details": {"category": "runtime"},
                "traces": [],
            }
        ],
        lineage={
            "nodes": [
                {
                    "workflow_run_id": str(workflow_run_id),
                    "redacted": False,
                    "status": "running",
                }
            ],
            "edges": [],
        },
        bundle=None,
    )


def _runtime_graph(workflow_run_id: UUID, tenant_id: UUID) -> AgentCommunicationGraph:
    return AgentCommunicationGraph(
        graph_id=f"runtime:{workflow_run_id}",
        source=AgentGraphSource.RUNTIME_RUN,
        state=AgentGraphState.READY,
        provenance=AgentGraphProvenance(
            source_type=AgentGraphSource.RUNTIME_RUN,
            workflow_run_id=str(workflow_run_id),
            run_status="completed",
            workflow_lineage_id=str(uuid4()),
            workflow_key="router-test",
            revision="v1",
            scope_type="tenant",
            tenant_id=str(tenant_id),
            generated_at=datetime.now(UTC),
        ),
        accessibility=AgentGraphAccessibility(
            summary="Agent graph is ready with 0 nodes and 0 edges.",
        ),
    )


class FakeInspectionService:
    def __init__(self, *, workflow_run_id: UUID, tenant_id: UUID) -> None:
        self.workflow_run_id = workflow_run_id
        self.tenant_id = tenant_id
        self.timeline_view = _timeline_view(workflow_run_id, tenant_id)

    async def search_runs(self, **kwargs):
        self.search_kwargs = kwargs
        return [
            SimpleNamespace(
                workflow_run_id=self.workflow_run_id,
                tenant_id=self.tenant_id,
                run_status_after="running",
                occurred_at=datetime.now(UTC),
                trace_id="trace-router-test",
                safe_details={"category": "runtime"},
            )
        ]

    async def get_timeline(self, **kwargs):
        self.timeline_kwargs = kwargs
        return self.timeline_view

    async def get_replay(self, **kwargs):
        self.replay_kwargs = kwargs
        return [
            {
                "sequence": 1,
                "timestamp": datetime.now(UTC),
                "event_category": "started",
                "status_after": "running",
                "trace_id": "trace-router-test",
                "actor": "system",
                "safe_summary": "Run started safely.",
                "linked_trace_count": 0,
                "checkpoint": True,
            },
            {
                "sequence": 2,
                "timestamp": datetime.now(UTC),
                "event_category": "completed",
                "status_after": "succeeded",
                "trace_id": "trace-router-test",
                "actor": "system",
                "safe_summary": "Run completed safely.",
                "linked_trace_count": 0,
                "checkpoint": True,
            },
        ]

    async def get_bundle(self, **kwargs):
        self.bundle_kwargs = kwargs
        return None

    async def ensure_authorized(self, **kwargs) -> None:
        self.authorized_kwargs = kwargs

    async def create_export(self, **kwargs):
        self.export_kwargs = kwargs
        return SimpleNamespace(
            debug_evidence_export_id=uuid4(),
            tenant_id=self.tenant_id,
            requested_by="tenant-admin-acme",
            workflow_run_id=self.workflow_run_id,
            lineage_scope=kwargs["lineage_scope"],
            recipient_scope=kwargs["recipient_scope"],
            redaction_profile="viewer-aware",
            status="requested",
            artifact_id=None,
            artifact_ref=None,
            included_sections=kwargs["included_sections"],
            excluded_sections=kwargs["excluded_sections"],
            safe_failure_reason=None,
            requested_at=datetime.now(UTC),
            completed_at=None,
            expires_at=None,
        )


class MissingInspectionService(FakeInspectionService):
    async def get_timeline(self, **kwargs):
        self.timeline_kwargs = kwargs
        return None

    async def get_replay(self, **kwargs):
        self.replay_kwargs = kwargs
        return None


class FailingInspectionService(FakeInspectionService):
    async def search_runs(self, **kwargs):
        raise AuditDebuggingAuthorizationError("search denied")

    async def get_timeline(self, **kwargs):
        raise AuditDebuggingAuthorizationError("timeline denied")

    async def get_replay(self, **kwargs):
        raise AuditDebuggingAuthorizationError("replay denied")

    async def ensure_authorized(self, **kwargs) -> None:
        raise AuditDebuggingAuthorizationError("graph denied")

    async def create_export(self, **kwargs):
        raise AuditDebuggingAuthorizationError("export denied")


@pytest.mark.asyncio
async def test_run_inspection_router_uses_service_views(monkeypatch) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    principal = _principal(tenant_id)
    service = FakeInspectionService(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    monkeypatch.setattr(router, "_service", lambda session: service)

    search = await router.debug_search(
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        status="running",
    )
    timeline = await router.timeline(
        workflow_run_id=workflow_run_id,
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=tenant_id,
    )
    replay = await router.replay(
        workflow_run_id=workflow_run_id,
        request=_request(),
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=tenant_id,
        from_sequence=2,
        to_sequence=None,
    )
    lineage = await router.lineage(
        workflow_run_id=workflow_run_id,
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=tenant_id,
    )
    export = await router.create_export(
        workflow_run_id=workflow_run_id,
        payload=CreateDebugEvidenceExportRequest(
            tenant_id=tenant_id,
            recipient_scope="tenant_auditor",
            included_sections=["timeline"],
            excluded_sections=[],
            reason="unit test",
        ),
        principal=principal,
        session=object(),  # type: ignore[arg-type]
    )

    assert search.items[0].failure_category == "runtime"
    assert service.search_kwargs["filters"]["status"] == "running"
    assert timeline.run.workflow_run_id == workflow_run_id
    assert len(replay.events) == 1
    assert replay.events[0].sequence == 2
    assert lineage.nodes[0].workflow_run_id == str(workflow_run_id)
    assert export.workflow_run_id == workflow_run_id


@pytest.mark.asyncio
async def test_run_inspection_router_returns_runtime_agent_graph(monkeypatch) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    principal = _principal(tenant_id)
    service = FakeInspectionService(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    monkeypatch.setattr(router, "_service", lambda session: service)

    async def fake_graph(**kwargs):
        return _runtime_graph(kwargs["workflow_run_id"], kwargs["tenant_id"])

    monkeypatch.setattr(router, "build_runtime_agent_graph", fake_graph)

    graph = await router.runtime_agent_graph(
        workflow_run_id=workflow_run_id,
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=None,
    )

    assert service.authorized_kwargs["tenant_id"] == tenant_id
    assert graph.provenance.workflow_run_id == str(workflow_run_id)


@pytest.mark.asyncio
async def test_run_inspection_router_redirect_and_not_found(monkeypatch) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    principal = _principal(tenant_id)
    service = FakeInspectionService(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    monkeypatch.setattr(router, "_service", lambda session: service)

    redirect = await router.replay(
        workflow_run_id=workflow_run_id,
        request=_request(accept="text/html", query=b"trace_id=trace-router-test"),
        principal=principal,
        session=object(),  # type: ignore[arg-type]
        tenant_id=tenant_id,
    )
    search_page = await router.admin_run_search_page(
        request=_request(query=b"status=running&ignored=value"),
        principal=principal,
        session=object(),  # type: ignore[arg-type]
    )
    detail_page = await router.admin_run_detail_page(
        workflow_run_id=workflow_run_id,
        request=_request(query=b"panel=timeline"),
        principal=principal,
        session=object(),  # type: ignore[arg-type]
    )

    assert redirect.status_code == 303
    assert "panel=replay" in redirect.headers["location"]
    assert search_page.headers["location"] == (
        "/admin/app/operations?status=running&panel=runs"
    )
    assert f"run_id={workflow_run_id}" in detail_page.headers["location"]
    with pytest.raises(HTTPException) as exc_info:
        await router.bundle(
            workflow_run_id=workflow_run_id,
            principal=principal,
            session=object(),  # type: ignore[arg-type]
            tenant_id=tenant_id,
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_run_inspection_router_not_found_paths(monkeypatch) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    principal = _principal(tenant_id)
    service = MissingInspectionService(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    monkeypatch.setattr(router, "_service", lambda session: service)

    async def missing_graph(**kwargs):
        return None

    monkeypatch.setattr(router, "build_runtime_agent_graph", missing_graph)

    for call in (
        router.timeline,
        router.replay,
        router.lineage,
        router.runtime_agent_graph,
    ):
        with pytest.raises(HTTPException) as exc_info:
            if call is router.replay:
                await call(
                    workflow_run_id=workflow_run_id,
                    request=_request(),
                    principal=principal,
                    session=object(),  # type: ignore[arg-type]
                    tenant_id=tenant_id,
                    to_sequence=None,
                )
            else:
                await call(
                    workflow_run_id=workflow_run_id,
                    principal=principal,
                    session=object(),  # type: ignore[arg-type]
                    tenant_id=tenant_id,
                )
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_run_inspection_router_wraps_service_errors(monkeypatch) -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    principal = _principal(tenant_id)
    service = FailingInspectionService(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )
    monkeypatch.setattr(router, "_service", lambda session: service)

    error_calls = (
        lambda: router.debug_search(
            principal=principal,
            session=object(),  # type: ignore[arg-type]
            tenant_id=tenant_id,
        ),
        lambda: router.timeline(
            workflow_run_id=workflow_run_id,
            principal=principal,
            session=object(),  # type: ignore[arg-type]
            tenant_id=tenant_id,
        ),
        lambda: router.replay(
            workflow_run_id=workflow_run_id,
            request=_request(),
            principal=principal,
            session=object(),  # type: ignore[arg-type]
            tenant_id=tenant_id,
            to_sequence=None,
        ),
        lambda: router.runtime_agent_graph(
            workflow_run_id=workflow_run_id,
            principal=principal,
            session=object(),  # type: ignore[arg-type]
            tenant_id=tenant_id,
        ),
        lambda: router.create_export(
            workflow_run_id=workflow_run_id,
            payload=CreateDebugEvidenceExportRequest(
                tenant_id=tenant_id,
                recipient_scope="tenant_auditor",
                included_sections=["timeline"],
                excluded_sections=[],
                reason="unit test",
            ),
            principal=principal,
            session=object(),  # type: ignore[arg-type]
        ),
    )

    for factory in error_calls:
        with pytest.raises(HTTPException) as exc_info:
            await factory()
        assert exc_info.value.status_code == 403


def test_run_inspection_router_error_helpers() -> None:
    assert router.build_combined_gateway_provenance_view({"status": "ready"}) == {
        "status": "ready"
    }
    forbidden = router._error(
        AuditDebuggingAuthorizationError("nope"),
        trace_id="trace-forbidden",
    )
    rate_limited = router._error(
        AuditDebuggingRateLimitError(retry_after_seconds=60),
        trace_id="trace-rate",
    )
    unexpected = router._error(RuntimeError("boom"), trace_id="trace-error")

    assert forbidden.status_code == 403
    assert forbidden.detail["trace_id"] == "trace-forbidden"
    assert rate_limited.status_code == 429
    assert rate_limited.detail["retry_after_seconds"] == 60
    assert unexpected.status_code == 500
