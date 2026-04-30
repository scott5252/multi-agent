from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CredentialReferenceSummary:
    requirement_key: str
    credential_kind: str
    reference_id: str | None
    status: str
    safe_summary: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReadinessFinding:
    code: str
    message: str
    blocking: bool = True


@dataclass(frozen=True, slots=True)
class InstallationReadiness:
    readiness_state: str
    credential_status: str
    compatibility_status: str
    permission_status: str
    smoke_test_status: str
    binding_eligibility_status: str
    findings: tuple[ReadinessFinding, ...] = ()


def evaluate_credential_readiness(
    required_keys: list[str],
    configured: list[CredentialReferenceSummary],
) -> tuple[str, tuple[ReadinessFinding, ...]]:
    by_key = {item.requirement_key: item for item in configured}
    findings: list[ReadinessFinding] = []
    for key in required_keys:
        summary = by_key.get(key)
        if summary is None or summary.status != "ready":
            findings.append(
                ReadinessFinding(
                    code="credential.missing_or_unready",
                    message=f"Credential requirement {key} is not ready.",
                )
            )
    return ("ready" if not findings else "blocked", tuple(findings))


def evaluate_installation_readiness(
    *,
    required_credential_keys: list[str],
    configured_credentials: list[CredentialReferenceSummary],
    compatibility_status: str,
    permission_status: str,
    smoke_test_status: str,
    quarantine_state: str = "clear",
) -> InstallationReadiness:
    credential_status, findings = evaluate_credential_readiness(
        required_credential_keys,
        configured_credentials,
    )
    all_findings = list(findings)
    for status_name, status_value in (
        ("compatibility", compatibility_status),
        ("permission", permission_status),
        ("smoke_test", smoke_test_status),
    ):
        if status_value not in {"ready", "passed", "not_required"}:
            all_findings.append(
                ReadinessFinding(
                    code=f"{status_name}.blocked",
                    message=f"{status_name} status is {status_value}.",
                )
            )
    if quarantine_state != "clear":
        all_findings.append(
            ReadinessFinding(
                code="quarantine.active",
                message="Installation is quarantined or runtime blocked.",
            )
        )
    ready = not any(finding.blocking for finding in all_findings)
    return InstallationReadiness(
        readiness_state="ready" if ready else "blocked",
        credential_status=credential_status,
        compatibility_status=compatibility_status,
        permission_status=permission_status,
        smoke_test_status=smoke_test_status,
        binding_eligibility_status="eligible" if ready else "denied",
        findings=tuple(all_findings),
    )
