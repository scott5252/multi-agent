from __future__ import annotations

from pathlib import Path

from multi_agent_platform.admin.migration_hardening import (
    build_transitional_label_gate,
    scan_transitional_label_findings,
    transitional_label_projection,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    TransitionalLabelClassification,
    TransitionalLabelSeverity,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def test_current_admin_visible_text_has_no_blocking_transitional_labels() -> None:
    findings = scan_transitional_label_findings()

    assert findings
    assert not [
        finding
        for finding in findings
        if finding.classification
        == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
    ]
    serialized = "\n".join(finding.model_dump_json() for finding in findings)
    assert "React Admin" not in serialized
    assert "/Users/" not in serialized
    assert "raw prompt" not in serialized.lower()


def test_synthetic_user_visible_react_admin_label_is_blocking(
    tmp_path: Path,
) -> None:
    source = tmp_path / "frontend/admin/src/components/new/Foo.tsx"
    source.parent.mkdir(parents=True)
    source.write_text('export const title = "React Admin";\n', encoding="utf-8")

    findings = scan_transitional_label_findings(repository_root=tmp_path)

    blockers = [
        finding
        for finding in findings
        if finding.classification
        == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
    ]
    assert len(blockers) == 1
    assert blockers[0].matched_text == "React Admin"
    assert blockers[0].severity == TransitionalLabelSeverity.BLOCKING
    assert blockers[0].remediation


def test_projection_preserves_allowed_implementation_references() -> None:
    findings = transitional_label_projection()

    classifications = {finding.classification for finding in findings}
    assert (
        TransitionalLabelClassification.INTERNAL_GENERATED_IDENTIFIER in classifications
    )
    assert TransitionalLabelClassification.HISTORICAL_REFERENCE in classifications
    assert TransitionalLabelClassification.TECHNICAL_QA_CONTEXT in classifications
    assert all(
        finding.severity == TransitionalLabelSeverity.INFO for finding in findings
    )


def test_transitional_label_gate_report_is_redaction_safe() -> None:
    gate = build_transitional_label_gate(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_platform_principal(),
    )

    assert gate.page_id == "qa059-transitional-label-gate"
    assert gate.summary.blocked_count == 0
    assert gate.summary.allowed_reference_count >= 3
    assert gate.summary.ci_status.value == "pass"
    serialized = gate.model_dump_json()
    assert "React Admin" not in serialized
    assert "/Users/" not in serialized
    assert "raw completion" not in serialized.lower()


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=None,
        org_id=None,
        role_codes=("platform_admin",),
        permission_codes=("platform:admin",),
        trace_id="trace-qa059-scanner",
    )
