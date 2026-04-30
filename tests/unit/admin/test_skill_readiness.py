from __future__ import annotations

from multi_agent_platform.admin.skill_registry.readiness import (
    CredentialReferenceSummary,
    evaluate_installation_readiness,
)


def test_readiness_blocks_missing_credentials() -> None:
    readiness = evaluate_installation_readiness(
        required_credential_keys=["calendar-oauth"],
        configured_credentials=[],
        compatibility_status="ready",
        permission_status="ready",
        smoke_test_status="passed",
    )

    assert readiness.readiness_state == "blocked"
    assert readiness.binding_eligibility_status == "denied"


def test_readiness_allows_ready_credentials_and_smoke_tests() -> None:
    readiness = evaluate_installation_readiness(
        required_credential_keys=["calendar-oauth"],
        configured_credentials=[
            CredentialReferenceSummary(
                requirement_key="calendar-oauth",
                credential_kind="delegated_credential",
                reference_id="delegated-1",
                status="ready",
            )
        ],
        compatibility_status="ready",
        permission_status="ready",
        smoke_test_status="passed",
    )

    assert readiness.readiness_state == "ready"
    assert readiness.binding_eligibility_status == "eligible"
