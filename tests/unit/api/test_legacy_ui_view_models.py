from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from starlette.requests import Request

from multi_agent_platform.api.ui import (
    agent_profiles,
    model_providers,
    model_skill_config,
    operations,
    prompts,
    reliability_controls,
    run_details,
)
from multi_agent_platform.api.ui import agent_tests as agent_tests_ui
from multi_agent_platform.api.ui import briefing_preferences as briefing_ui
from multi_agent_platform.api.ui import memberships as memberships_ui
from multi_agent_platform.api.ui import usage as usage_ui
from multi_agent_platform.channels.models import (
    ArtifactMetadata,
    ResultAvailability,
    RunResult,
    RunStatusView,
    TimelineEvent,
    TimelineEventType,
    UserVisibleRunState,
)
from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsCapacitySummary,
    OperationsDashboardSnapshot,
    OperationsLogFilters,
    OperationsStatusCard,
    OperationsUsageSummary,
)
from multi_agent_platform.usage.models import UsageFilters, UsageTotals


def test_operations_console_view_model_uses_live_dashboard_values() -> None:
    dashboard = OperationsDashboardSnapshot(
        health_status="ready",
        status_cards=(
            OperationsStatusCard(
                label="Request Latency",
                value="12 ms",
                status="ready",
                summary="Live latency",
            ),
        ),
        dependencies=(),
        capacity=OperationsCapacitySummary(),
        usage=OperationsUsageSummary(token_throughput=42),
        logs=(
            OperationalLogEvent(
                event_id="log-1",
                source="audit",
                occurred_at=datetime.now(UTC),
                component="runtime",
                severity="info",
                status="ready",
                summary="Safe log",
            ),
        ),
        redaction_notice="redacted",
    )
    page = operations.OperationsConsolePage(
        dashboard=dashboard,
        filters=OperationsLogFilters(),
        can_export=True,
    )
    empty_page = operations.OperationsConsolePage(
        dashboard=dashboard.model_copy(
            update={"status_cards": (), "logs": (), "usage": OperationsUsageSummary()}
        ),
        filters=OperationsLogFilters(),
        can_export=False,
    )

    assert page.has_logs is True
    assert page.request_latency_display == "12 ms"
    assert page.token_throughput_display == "42"
    assert empty_page.has_logs is False
    assert empty_page.request_latency_display == "0 ms"
    assert "credentials" in operations.operations_redaction_notice()


def test_run_details_view_models_and_filters_are_safe() -> None:
    run_id = uuid4()
    status = RunStatusView(
        run_id=run_id,
        state=UserVisibleRunState.RUNNING,
        progress_summary="Running",
        latest_timeline_cursor="cursor-1",
        permitted_actions=("cancel",),
        trace_id="trace-run",
    )
    timeline = [
        TimelineEvent(
            sequence=1,
            event_type=TimelineEventType.RUN_STARTED,
            state=UserVisibleRunState.RUNNING,
            summary="Run started",
            trace_id="trace-run",
        )
    ]
    result = RunResult(
        run_id=run_id,
        availability=ResultAvailability.AVAILABLE,
        state=UserVisibleRunState.RUNNING,
        trace_id="trace-run",
        summary="Result safe",
    )
    artifact = ArtifactMetadata(
        artifact_id=uuid4(),
        name="artifact.json",
        user_facing_type="json",
    )

    model = run_details.build_run_details_model(
        status=status,
        timeline=timeline,
        result=result,
        artifacts=[artifact],
    )

    assert model.support_trace_id == "trace-run"
    assert model.timeline == tuple(timeline)
    assert run_details.build_run_search_model().audit_mode is True
    assert run_details.build_run_replay_model(workflow_run_id=str(run_id)).title
    assert run_details.run_inspection_filter_profile().admin_area == "run_inspection"


def test_small_admin_ui_models_cover_safe_defaults() -> None:
    profile = agent_profiles.build_agent_profile_ui_model(
        title="Profile",
        scope_type="tenant",
        validation_status="passed",
        status="draft",
        findings=[
            {"severity": "blocking", "section": "prompt_references"},
            {"severity": "info", "section": "skill_requirements"},
        ],
        submitted_fields={"agent_key": "daily"},
    )
    prompt = prompts.build_prompt_ui_model(
        title="Prompt",
        scope_type="platform",
        validation_status="passed",
        status="draft",
        findings=[{"code": "safe", "message": "Looks good"}],
    )

    assert profile.can_activate is True
    assert profile.sections[0].blocking_count == 1
    assert prompt.can_publish is True
    assert prompt.can_preview is True
    assert (
        prompts.build_prompt_ui_model(
            title="Active",
            scope_type="platform",
            status="active",
        ).can_retire
        is True
    )


def test_provider_model_skill_usage_and_membership_view_models() -> None:
    connection_id = uuid4()
    detail_connection = type("Connection", (), {"display_name": "Live Provider"})()

    assert model_providers.build_list_page([], can_mutate=True).title == (
        "Model Providers"
    )
    assert (
        model_providers.build_form_page(
            connection_id=None,
            can_mutate=True,
        ).title
        == "New Model Provider"
    )
    assert (
        str(connection_id)
        in model_providers.build_form_page(
            connection_id=connection_id,
            can_mutate=False,
        ).action
    )
    assert (
        model_providers.build_detail_page(
            connection=detail_connection,
            models=(),
            tenant_ids=(),
            latest_test=None,
            can_mutate=False,
        ).title
        == "Live Provider"
    )
    catalog_page = model_providers.build_catalog_page(entries=(), can_mutate=False)
    assert catalog_page.entries == ()
    assert model_providers.model_provider_filter_profile().admin_area == (
        "model_providers"
    )
    assert model_skill_config.build_model_routing_page_model(
        missing_default=True
    ).policy_create_actions
    assert model_skill_config.model_skill_history_filter_profile().admin_area == (
        "model_skill_history"
    )

    usage_page = usage_ui.UsageDashboardPage(
        filters=UsageFilters(),
        totals=UsageTotals(estimated_cost_micros=1_234_567),
        rollups=(),
        events=(),
        can_export=True,
    )
    assert usage_page.has_events is False
    assert usage_page.estimated_cost_display == "$1.234567"
    assert usage_ui.UsageExportPage(status="complete", row_count=2).row_count == 2
    assert "Raw prompts" in usage_ui.redaction_notice()

    membership_page = memberships_ui.MembershipAdministrationPage(
        principals=(),
        invitations=(),
        memberships=(),
        role_grants=(),
        access_history=(),
        audit_records=(),
    )
    assert membership_page.scope_label == "Platform scope"
    assert membership_page.active_principal_count == 0
    assert membership_page.active_grant_count == 0
    assert "tokens" in memberships_ui.redaction_notice()


def test_misc_ui_redaction_and_redirect_helpers() -> None:
    assert "payloads" in agent_tests_ui.redaction_notice()
    assert agent_tests_ui.AgentTestIndexPage(tenant_id="tenant").create_href

    briefing_page = briefing_ui.BriefingPreferencesPage(profile=None)
    assert briefing_page.profile_ready_label == "Not configured"
    assert briefing_page.topic_text == "AI, markets, product launches"
    assert briefing_page.vip_text == "product lead, legal team"
    assert "tokens" in briefing_ui.redaction_notice()

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/admin/reliability/ui/breakers",
            "headers": [],
            "query_string": b"tenant_id=tenant-1&state=open&ignored=yes",
        }
    )
    redirect = reliability_controls._react_redirect(request, panel="breakers")
    assert redirect.status_code == reliability_controls.SEE_OTHER
    assert redirect.headers["location"] == (
        "/admin/app/operations?tenant_id=tenant-1&state=open&panel=breakers"
    )
    assert reliability_controls.reliability_breakers_filter_profile().admin_area == (
        "reliability_breakers"
    )
    dead_letters_profile = (
        reliability_controls.reliability_dead_letters_filter_profile()
    )
    assert dead_letters_profile.admin_area == ("reliability_dead_letters")
