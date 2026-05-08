from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.usage import (
    LlmPricingVersion,
    LlmUsageEvent,
    UsageExportRequest,
)
from multi_agent_platform.model_providers.models import UsageValueStatus
from multi_agent_platform.usage.models import (
    UsageEventStatus,
    UsageExportStatus,
    UsageScopeType,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA056_PRICING_ID = UUID("56000000-0000-0000-0000-000000000001")
QA056_EVENT_ID = UUID("56000000-0000-0000-0000-000000000011")
QA056_PARTIAL_EVENT_ID = UUID("56000000-0000-0000-0000-000000000012")
QA056_EXPORT_ID = UUID("56000000-0000-0000-0000-000000000056")
QA056_WORKFLOW_LINEAGE_ID = UUID("56000000-0000-0000-0000-000000000101")
QA056_WORKFLOW_RUN_ID = UUID("56000000-0000-0000-0000-000000000102")
QA056_WORKFLOW_STEP_ID = UUID("56000000-0000-0000-0000-000000000103")
QA056_PROMPT_VERSION_ID = UUID("56000000-0000-0000-0000-000000000104")
QA056_GATEWAY_ATTEMPT_ID = UUID("56000000-0000-0000-0000-000000000105")


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime.now(UTC)
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        _upsert_pricing(session, now=now)
        _upsert_confirmed_event(session, now=now)
        _upsert_partial_event(session, now=now)
        _upsert_seed_export(session, now=now)
        session.commit()
    print("Seeded QA056 usage live records")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"globex_tenant_id={GLOBEX_TENANT_ID}")
    print("usage_events=2")
    print(f"seed_export_id={QA056_EXPORT_ID}")
    return 0


def _upsert_tenant(
    session: Session,
    tenant_id: UUID,
    slug: str,
    display_name: str,
) -> None:
    record = session.get(Tenant, tenant_id)
    if record is None:
        record = Tenant(tenant_id=tenant_id)
        session.add(record)
    record.slug = slug
    record.display_name = display_name
    record.status = TenantStatus.ACTIVE


def _upsert_pricing(session: Session, *, now: datetime) -> None:
    record = session.get(LlmPricingVersion, QA056_PRICING_ID)
    if record is None:
        record = LlmPricingVersion(llm_pricing_version_id=QA056_PRICING_ID)
        session.add(record)
    record.provider_key = "openai"
    record.model_id = "gpt-live-usage"
    record.currency = "USD"
    record.input_token_micros = 2
    record.output_token_micros = 6
    record.cached_token_micros = 0
    record.reasoning_token_micros = 6
    record.billable_unit_micros = None
    record.calculation_method = "qa056_live_per_token"
    record.effective_from = now - timedelta(days=7)
    record.effective_to = None
    record.source_note = "qa056 persisted live pricing"
    record.created_by_principal_id = "tenant-admin-acme"


def _upsert_confirmed_event(session: Session, *, now: datetime) -> None:
    record = session.get(LlmUsageEvent, QA056_EVENT_ID)
    if record is None:
        record = LlmUsageEvent(
            llm_usage_event_id=QA056_EVENT_ID,
            tenant_id=ACME_TENANT_ID,
            provider_key="openai",
            model_id="gpt-live-usage",
        )
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.principal_id = "tenant-admin-acme"
    record.workflow_lineage_id = QA056_WORKFLOW_LINEAGE_ID
    record.workflow_run_id = QA056_WORKFLOW_RUN_ID
    record.workflow_run_step_id = QA056_WORKFLOW_STEP_ID
    record.agent_key = "usage-reviewer"
    record.sub_agent_key = "cost-summarizer"
    record.provider_key = "openai"
    record.model_id = "gpt-live-usage"
    record.prompt_version_id = QA056_PROMPT_VERSION_ID
    record.execution_mode = "test"
    record.operation_identity = "responses.live_usage.primary"
    record.idempotency_key = "qa056-live-usage-confirmed"
    record.trace_id = "trace-qa056-live-usage"
    record.input_tokens = 1200
    record.output_tokens = 360
    record.cached_tokens = 0
    record.reasoning_tokens = 0
    record.total_tokens = 1560
    record.provider_billable_units = None
    record.input_status = UsageValueStatus.CONFIRMED
    record.output_status = UsageValueStatus.CONFIRMED
    record.cached_status = UsageValueStatus.NOT_APPLICABLE
    record.reasoning_status = UsageValueStatus.NOT_APPLICABLE
    record.total_status = UsageValueStatus.CONFIRMED
    record.billable_status = UsageValueStatus.UNAVAILABLE
    record.cost_status = UsageValueStatus.ESTIMATED
    record.latency_ms = 420
    record.currency = "USD"
    record.estimated_cost_micros = 4560
    record.pricing_version_id = QA056_PRICING_ID
    record.usage_status = UsageEventStatus.CONFIRMED
    record.source_gateway_attempt_id = QA056_GATEWAY_ATTEMPT_ID
    record.safe_attribution = {
        "workflow_label": "Usage live review workflow",
        "prompt_label": "Usage summary prompt v1",
        "graph_node_label": "Summarize usage evidence",
        "governed_tool_label": "Usage export metadata lookup",
        "physical_attempt_label": "OpenAI live usage attempt",
        "summary": "Live usage attributed through safe persisted metadata.",
    }
    record.recorded_at = now - timedelta(days=1)


def _upsert_partial_event(session: Session, *, now: datetime) -> None:
    record = session.get(LlmUsageEvent, QA056_PARTIAL_EVENT_ID)
    if record is None:
        record = LlmUsageEvent(
            llm_usage_event_id=QA056_PARTIAL_EVENT_ID,
            tenant_id=ACME_TENANT_ID,
            provider_key="local-compatible",
            model_id="local-usage-check",
        )
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.principal_id = "tenant-admin-acme"
    record.workflow_run_id = None
    record.workflow_run_step_id = None
    record.workflow_lineage_id = QA056_WORKFLOW_LINEAGE_ID
    record.workflow_version_id = None
    record.agent_key = "usage-reviewer"
    record.sub_agent_key = None
    record.provider_key = "local-compatible"
    record.model_id = "local-usage-check"
    record.prompt_version_id = None
    record.execution_mode = "test"
    record.operation_identity = "local.live_usage.fallback"
    record.idempotency_key = "qa056-live-usage-partial"
    record.trace_id = "trace-qa056-local-usage"
    record.input_tokens = 300
    record.output_tokens = 0
    record.cached_tokens = 0
    record.reasoning_tokens = 0
    record.total_tokens = 300
    record.provider_billable_units = None
    record.input_status = UsageValueStatus.ESTIMATED
    record.output_status = UsageValueStatus.UNAVAILABLE
    record.cached_status = UsageValueStatus.NOT_APPLICABLE
    record.reasoning_status = UsageValueStatus.NOT_APPLICABLE
    record.total_status = UsageValueStatus.ESTIMATED
    record.billable_status = UsageValueStatus.UNAVAILABLE
    record.cost_status = UsageValueStatus.UNAVAILABLE
    record.latency_ms = 85
    record.currency = "USD"
    record.estimated_cost_micros = None
    record.pricing_version_id = None
    record.usage_status = UsageEventStatus.PARTIAL
    record.source_gateway_attempt_id = None
    record.safe_attribution = {
        "workflow_label": "Usage live review workflow",
        "summary": "Partial local usage with missing pricing metadata.",
    }
    record.recorded_at = now - timedelta(hours=3)


def _upsert_seed_export(session: Session, *, now: datetime) -> None:
    record = session.get(UsageExportRequest, QA056_EXPORT_ID)
    if record is None:
        record = UsageExportRequest(usage_export_request_id=QA056_EXPORT_ID)
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.requested_by_principal_id = "tenant-admin-acme"
    record.scope_type = UsageScopeType.TENANT
    record.filters = {"tenant_id": str(ACME_TENANT_ID), "range": "Last 30 days"}
    record.status = UsageExportStatus.COMPLETED
    record.row_count = 2
    record.artifact_uri = "qa056/exports/seeded-usage.csv"
    record.artifact_sha256 = "a" * 64
    record.artifact_size_bytes = 512
    record.denial_reason = None
    record.failure_reason = None
    record.created_at = now - timedelta(minutes=10)
    record.completed_at = now - timedelta(minutes=9)
    record.expires_at = now + timedelta(days=7)


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
