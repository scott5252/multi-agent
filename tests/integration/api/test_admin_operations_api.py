from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.audit_debugging import (
    AuditTimelineEventRecord,
    InspectionAccessAuditEventRecord,
)
from multi_agent_platform.db.models.model_providers import (
    GatewayInvocationAttempt,
    ModelProviderConnection,
    ProviderModelDefinition,
)
from multi_agent_platform.db.models.reliability import CapacitySnapshotRecord
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.models.usage import LlmUsageEvent
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderType,
    TestOutcome,
)
from multi_agent_platform.usage.models import UsageEventStatus

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
AUDITOR_HEADERS = {"X-Local-Principal": "auditor"}
TENANT_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}


def _configure_env(monkeypatch, tmp_path: Path) -> Path:
    database_path = tmp_path / "operations.db"
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
                "VALUES ('0019_operations_console_logs_performance')"
            )
        )
    run_id = uuid4()
    provider_id = uuid4()
    model_id = uuid4()
    with Session(engine) as session:
        session.add(
            Tenant(
                tenant_id=UUID(ACME_TENANT_ID),
                slug="acme",
                display_name="Acme",
            )
        )
        session.add(
            CapacitySnapshotRecord(
                runnable_depth=6,
                delayed_depth=2,
                active_leases=3,
                retry_backlog=1,
                dead_letter_count=1,
                db_pool_wait_p95_ms=15,
                db_pool_in_use=4,
                db_pool_available=6,
                open_breaker_count=1,
            )
        )
        session.add(
            AuditTimelineEventRecord(
                tenant_id=UUID(ACME_TENANT_ID),
                workflow_run_id=run_id,
                sequence=1,
                event_category="runtime",
                run_status_after="running",
                origin_type="system",
                actor_principal_id="platform-admin",
                trace_id="trace-ops",
                source_event_id="source-ops-1",
                criticality="diagnostic",
                safe_summary="Run moved to running",
                safe_details={"dependency": "postgres", "prompt": "must-redact"},
                occurred_at=datetime(2026, 5, 3, tzinfo=UTC),
            )
        )
        session.add(
            ModelProviderConnection(
                provider_connection_id=provider_id,
                provider_type=ProviderType.OPENAI,
                display_name="OpenAI QA",
                timeout_policy={},
                active=True,
                health_state=HealthState.HEALTHY,
                credential_secret_reference_ids=[],
                created_by_principal_id="platform-admin",
                updated_by_principal_id="platform-admin",
            )
        )
        session.add(
            ProviderModelDefinition(
                provider_model_definition_id=model_id,
                provider_connection_id=provider_id,
                model_id="gpt-qa",
                display_name="GPT QA",
                available=True,
            )
        )
        session.add(
            GatewayInvocationAttempt(
                tenant_id=UUID(ACME_TENANT_ID),
                workflow_run_id=run_id,
                trace_id="trace-ops",
                provider_connection_id=provider_id,
                provider_model_definition_id=model_id,
                provider_type=ProviderType.OPENAI,
                model_id="gpt-qa",
                started_at=datetime(2026, 5, 3, tzinfo=UTC),
                completed_at=datetime(2026, 5, 3, tzinfo=UTC),
                latency_ms=80,
                outcome=TestOutcome.SUCCESS,
                normalized_error_category=ErrorCategory.NONE,
                usage_metadata={"total_tokens": 25},
                usage_available=True,
                safe_audit_summary={
                    "summary": "Gateway completed safely",
                    "credential": "must-redact",
                },
            )
        )
        session.add(
            LlmUsageEvent(
                tenant_id=UUID(ACME_TENANT_ID),
                principal_id="platform-admin",
                provider_key="openai",
                model_id="gpt-qa",
                execution_mode="test",
                total_tokens=25,
                estimated_cost_micros=75,
                latency_ms=80,
                usage_status=UsageEventStatus.CONFIRMED,
            )
        )
        session.commit()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "static:qa019/webhook")
    monkeypatch.setenv("TELEGRAM_PROVIDER_TOKEN_REF", "static:qa019/telegram")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "platform:admin",
                        "operations:read",
                        "operations:logs",
                        "operations:export",
                    ],
                },
                "auditor": {
                    "catalog_key": "auditor",
                    "display_name": "Auditor",
                    "role_codes": ["auditor"],
                    "permission_codes": [
                        "operations:read",
                        "operations:logs",
                        "operations:export",
                    ],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Acme Tenant Admin",
                    "tenant_id": ACME_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "operations:read",
                        "operations:logs",
                        "operations:export",
                    ],
                },
            }
        ),
    )
    return database_path


def test_operations_api_dashboard_logs_export_and_denial(tmp_path, monkeypatch) -> None:
    database_path = _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        dashboard = client.get(
            "/admin/operations/api/dashboard",
            headers=PLATFORM_HEADERS,
        )
        filtered = client.get(
            "/admin/operations/api/logs?trace_id=trace-ops&component=model_provider",
            headers=AUDITOR_HEADERS,
        )
        denied = client.get(
            "/admin/operations/api/dashboard",
            headers=TENANT_HEADERS,
        )
        export = client.post(
            "/admin/operations/api/logs/export",
            headers=PLATFORM_HEADERS,
            json={"filters": {"trace_id": "trace-ops", "limit": 10}},
        )

    assert dashboard.status_code == 200, dashboard.text
    labels = {card["label"] for card in dashboard.json()["status_cards"]}
    assert {"System Health", "Token Throughput", "Model Providers"} <= labels
    assert dashboard.json()["usage"]["total_tokens"] == 25
    assert filtered.status_code == 200, filtered.text
    assert filtered.json()["items"][0]["source"] == "gateway_attempt"
    assert "must-redact" not in filtered.text
    assert denied.status_code == 403
    assert export.status_code == 201, export.text
    assert export.json()["row_count"] >= 1
    assert export.json()["artifact_uri"]

    engine = create_engine(f"sqlite:///{database_path}")
    with Session(engine) as session:
        audit_count = session.scalar(
            select(func.count()).select_from(InspectionAccessAuditEventRecord)
        )
    assert audit_count == 1
