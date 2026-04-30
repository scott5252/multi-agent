from __future__ import annotations

from multi_agent_platform.admin.skill_registry.smoke_runner import (
    SkillSmokeTestRunner,
    SmokeFixtureInput,
    SmokeRunnerInput,
)


def test_smoke_runner_records_safe_passed_output() -> None:
    output = SkillSmokeTestRunner().run(
        SmokeRunnerInput(
            tenant_id="tenant-1",
            installation_id="install-1",
            installation_version=1,
            package_slug="calendar-assistant",
            semantic_version="1.2.3",
            manifest_digest="sha256:manifest",
            artifact_digest="sha256:artifact",
            fixtures=(
                SmokeFixtureInput(
                    fixture_key="list-calendars",
                    tool_id="calendar.list",
                    action_category="read",
                ),
            ),
            credential_status="ready",
            idempotency_key="tenant-install-run",
            trace_id="trace-1",
        )
    )

    assert output.outcome == "passed"
    assert output.fixture_results[0]["policy_decision_summary"]["credential"] == "allow"


def test_smoke_runner_skips_credential_fixture_when_unready() -> None:
    output = SkillSmokeTestRunner().run(
        SmokeRunnerInput(
            tenant_id="tenant-1",
            installation_id="install-1",
            installation_version=1,
            package_slug="calendar-assistant",
            semantic_version="1.2.3",
            manifest_digest="sha256:manifest",
            artifact_digest="sha256:artifact",
            fixtures=(
                SmokeFixtureInput(
                    fixture_key="list-calendars",
                    tool_id="calendar.list",
                    action_category="read",
                    requires_credentials=True,
                ),
            ),
            credential_status="blocked",
            idempotency_key="tenant-install-run",
            trace_id="trace-1",
        )
    )

    assert output.outcome == "failed"
    assert output.failure_reasons
