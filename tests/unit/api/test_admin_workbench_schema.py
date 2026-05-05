from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.api.schemas.admin_workbench import (
    GatewayAttemptSummary,
    TimelineEventSummary,
    WorkbenchExportSnapshot,
    WorkbenchLogSummary,
    WorkbenchSeverity,
    WorkbenchStatus,
)


def test_workbench_log_rejects_unsafe_payload_markers() -> None:
    log = WorkbenchLogSummary(
        log_id="log-safe",
        occurred_at_label="Now",
        source="gateway_attempt",
        severity=WorkbenchSeverity.WARNING,
        status=WorkbenchStatus.DEGRADED,
        subsystem="gateway",
        summary="Gateway attempt recorded retryable timeout category.",
        safe_details={"diagnostic": "resolved reference"},
    )

    assert log.safe_details["diagnostic"] == "resolved reference"

    with pytest.raises(ValidationError):
        WorkbenchLogSummary(
            log_id="log-unsafe",
            occurred_at_label="Now",
            source="gateway_attempt",
            severity=WorkbenchSeverity.WARNING,
            status=WorkbenchStatus.DEGRADED,
            subsystem="gateway",
            summary="raw provider response with private channel message",
        )


def test_run_debug_summaries_reject_unsafe_payload_markers() -> None:
    with pytest.raises(ValidationError):
        TimelineEventSummary(
            event_id="timeline-unsafe",
            occurred_at_label="Now",
            category="delivery",
            severity=WorkbenchSeverity.WARNING,
            status=WorkbenchStatus.WARNING,
            summary="Delivery detail includes a private channel message.",
        )

    with pytest.raises(ValidationError):
        GatewayAttemptSummary(
            attempt_id="gateway-unsafe",
            provider_label="OpenAI provider",
            model_label="Briefing model",
            status=WorkbenchStatus.DEGRADED,
            safe_summary="Raw provider response was copied into the summary.",
        )


def test_workbench_export_rejects_local_paths_and_secret_markers() -> None:
    snapshot = WorkbenchExportSnapshot(
        export_id="export-safe",
        status="complete",
        summary="Safe export ready.",
        artifact_reference_id="artifact-ref-qa029-platform",
        scope_label="Platform",
        redaction_summary="Secrets and payloads are redacted.",
        row_count=2,
    )

    assert snapshot.artifact_reference_id == "artifact-ref-qa029-platform"

    with pytest.raises(ValidationError):
        WorkbenchExportSnapshot(
            export_id="export-unsafe",
            status="complete",
            summary="Safe export ready.",
            artifact_reference_id="/Users/scott/raw.csv",
            scope_label="Platform",
            redaction_summary="Secrets are redacted.",
        )

    with pytest.raises(ValidationError):
        WorkbenchExportSnapshot(
            export_id="export-secret",
            status="complete",
            summary="qa029-secret-value leaked",
            artifact_reference_id="artifact-ref",
            scope_label="Platform",
            redaction_summary="Secrets are redacted.",
        )


def test_react_scope_remains_safe_in_schema_context() -> None:
    scope = ReactAdminScope(scope_type="tenant", tenant_id=None, label="Acme")

    assert scope.label == "Acme"
