from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    AdminMigrationHardeningDashboard,
    JinjaInventoryClassification,
    JinjaInventoryDashboard,
    JinjaInventoryEvidence,
    JinjaInventoryEvidenceType,
    JinjaInventoryGroup,
    JinjaInventoryItem,
    JinjaInventoryItemType,
    JinjaInventorySummary,
    LiveDataCiStatus,
    LiveDataInventoryEvidence,
    LiveDataInventoryEvidenceType,
    LiveDataScanSummary,
    MigrationAccessibilityAudit,
    MigrationEvidenceStatus,
    MigrationHardeningSummary,
    MigrationOverallStatus,
    MigrationPerformanceBudget,
    MigrationPerformanceMeasurement,
    MigrationProblem,
    MigrationProblemSeverity,
    MigrationRollbackPlan,
    MigrationRouteDecision,
    MigrationRouteEntry,
    MigrationRouteGroup,
    MigrationScopeRequirement,
    MigrationSweepSummary,
    TransitionalLabelClassification,
    TransitionalLabelFinding,
    TransitionalLabelGate,
    TransitionalLabelGateSummary,
    TransitionalLabelSeverity,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)


def test_migration_dashboard_schema_accepts_safe_payload() -> None:
    dashboard = _dashboard()

    assert dashboard.page_id == "qa037-react-admin-migration-hardening"
    assert dashboard.summary.total_destinations == 1
    assert dashboard.route_groups[0].entries[0].react_route == "/admin/app"
    assert dashboard.rollback_plan.status == MigrationOverallStatus.READY
    assert dashboard.performance_budget.measurements[0].value == 214
    assert dashboard.accessibility_audit.keyboard_status == MigrationEvidenceStatus.PASS


def test_route_retirement_requires_eligible_decision_and_evidence() -> None:
    with pytest.raises(ValidationError, match="retirement requires approved"):
        _route_entry(
            decision=MigrationRouteDecision.REACT_PRIMARY,
            evidence=(),
            retirement_allowed=True,
        )


def test_schema_rejects_unsafe_marker_strings() -> None:
    with pytest.raises(ValidationError, match="unsafe migration hardening text"):
        _route_entry(admin_area="qa037-secret-value")


def test_jinja_inventory_requires_safe_delete_evidence_and_relative_paths() -> None:
    with pytest.raises(ValidationError, match="safe-to-delete"):
        _inventory_item(
            classification=JinjaInventoryClassification.SAFE_TO_DELETE,
            evidence_refs=(),
        )

    with pytest.raises(ValidationError, match="repository-relative"):
        _inventory_item(source_path="/absolute/template.html")


def test_jinja_inventory_dashboard_accepts_safe_payload() -> None:
    inventory = _jinja_inventory()

    assert inventory.summary.total_items == 1
    assert inventory.groups[0].items[0].source_path == (
        "src/multi_agent_platform/web_admin/templates/admin_react/app.html"
    )
    assert "qa038-secret-value" not in inventory.model_dump_json()


def test_route_group_bounds_entries() -> None:
    entries = tuple(_route_entry(entry_id=f"entry-{index}") for index in range(41))

    with pytest.raises(ValidationError):
        MigrationRouteGroup(
            group_id="oversized",
            label="Oversized",
            spec_refs=("037",),
            group_status=MigrationOverallStatus.READY,
            entries=entries,
        )


def test_failed_sweep_requires_unsafe_match_count() -> None:
    with pytest.raises(ValidationError, match="failed sweep requires unsafe matches"):
        MigrationSweepSummary(
            sweep_id="redaction",
            status=MigrationEvidenceStatus.FAIL,
            checked_artifacts=10,
            unsafe_match_count=0,
            safe_summary="Failed sweep without matches",
            evidence_reference="scan",
        )


def test_performance_measurement_requires_non_negative_values() -> None:
    with pytest.raises(ValidationError):
        MigrationPerformanceMeasurement(
            measurement_id="negative",
            label="Negative",
            value=-1,
            unit="ms",
            limit=500,
            status=MigrationEvidenceStatus.PASS,
            evidence_reference="perf",
        )


def test_rollback_plan_rejects_local_filesystem_paths() -> None:
    with pytest.raises(ValidationError, match="unsafe text"):
        _rollback_plan(asset_version_label="/Users/local/path")


def test_live_data_gate_evidence_rejects_absolute_paths() -> None:
    with pytest.raises(ValidationError, match="unsafe text|relative"):
        LiveDataInventoryEvidence(
            evidence_id="qa058-unsafe",
            evidence_type=LiveDataInventoryEvidenceType.SCANNER,
            reference="/Users/local/report.json",
            status=MigrationEvidenceStatus.PASS,
        )


def test_live_data_gate_summary_requires_failed_blockers() -> None:
    with pytest.raises(ValidationError, match="failed live-data scan"):
        LiveDataScanSummary(
            total_findings=0,
            blocking_findings=0,
            mapped_legacy_findings=0,
            allowed_computed_metadata=0,
            test_only_markers=0,
            route_targets=1,
            empty_state_scans=1,
            seeded_state_scans=1,
            ci_status=LiveDataCiStatus.FAIL,
            next_step="Fix blockers.",
        )


def test_transitional_label_gate_summary_matches_findings() -> None:
    finding = TransitionalLabelFinding(
        finding_id="blocking",
        surface_id="frontend/admin/src/App.tsx",
        matched_text="React Admin",
        classification=TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL,
        severity=TransitionalLabelSeverity.BLOCKING,
        rationale="Product labels must use Admin terminology.",
        owner="admin platform",
        remediation="Replace with Admin.",
    )

    with pytest.raises(ValidationError, match="blocked count"):
        TransitionalLabelGate(
            page_id="qa059-transitional-label-gate",
            generated_at=datetime(2026, 5, 8, 13, tzinfo=UTC),
            summary=TransitionalLabelGateSummary(
                blocked_count=0,
                allowed_reference_count=0,
                surfaces_scanned=1,
                routes_scanned=1,
                screenshots_checked=0,
                ci_status=LiveDataCiStatus.PASS,
                next_step="Fix blockers.",
            ),
            findings=(finding,),
            evidence=(),
        )


def test_transitional_blocking_label_requires_remediation() -> None:
    with pytest.raises(ValidationError, match="require remediation"):
        TransitionalLabelFinding(
            finding_id="blocking",
            surface_id="frontend/admin/src/App.tsx",
            matched_text="React Admin",
            classification=TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL,
            severity=TransitionalLabelSeverity.BLOCKING,
            rationale="Product labels must use Admin terminology.",
            owner="admin platform",
            remediation=None,
        )


def _dashboard() -> AdminMigrationHardeningDashboard:
    return AdminMigrationHardeningDashboard(
        page_id="qa037-react-admin-migration-hardening",
        title="Admin Migration Hardening",
        description="Safe migration dashboard",
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.TENANT,
            tenant_id="11111111-1111-1111-1111-111111111111",
            label="Acme",
        ),
        updated_at=datetime(2026, 5, 5, 18, tzinfo=UTC),
        summary=MigrationHardeningSummary(
            total_destinations=1,
            react_primary_count=1,
            redirect_count=0,
            retained_fallback_count=0,
            retirement_candidate_count=0,
            blocked_count=0,
            overall_status=MigrationOverallStatus.READY,
            next_step="Review retained fallbacks after release evidence.",
        ),
        route_groups=(
            MigrationRouteGroup(
                group_id="foundation",
                label="Foundation",
                spec_refs=("037",),
                group_status=MigrationOverallStatus.READY,
                entries=(_route_entry(),),
            ),
        ),
        rollback_plan=_rollback_plan(),
        performance_budget=MigrationPerformanceBudget(
            budget_id="budget",
            route_bootstrap_ms_limit=500,
            primary_interactive_ms_limit=2000,
            compressed_asset_kb_limit=250,
            status=MigrationEvidenceStatus.PASS,
            mitigation=None,
            measurements=(
                MigrationPerformanceMeasurement(
                    measurement_id="bootstrap",
                    label="Bootstrap",
                    value=214,
                    unit="ms",
                    limit=500,
                    status=MigrationEvidenceStatus.PASS,
                    evidence_reference="perf-bootstrap",
                ),
            ),
        ),
        accessibility_audit=MigrationAccessibilityAudit(
            audit_id="a11y",
            status=MigrationEvidenceStatus.PASS,
            viewport_coverage=("desktop", "mobile"),
            keyboard_status=MigrationEvidenceStatus.PASS,
            focus_status=MigrationEvidenceStatus.PASS,
            landmark_status=MigrationEvidenceStatus.PASS,
            label_status=MigrationEvidenceStatus.PASS,
            contrast_state_status=MigrationEvidenceStatus.PASS,
            text_overlap_status=MigrationEvidenceStatus.PASS,
            evidence_references=("a11y-desktop",),
        ),
        redaction_sweep=MigrationSweepSummary(
            sweep_id="redaction",
            status=MigrationEvidenceStatus.PASS,
            checked_artifacts=10,
            unsafe_match_count=0,
            safe_summary="No unsafe markers found.",
            evidence_reference="scan",
        ),
        tenant_isolation_sweep=MigrationSweepSummary(
            sweep_id="tenant",
            status=MigrationEvidenceStatus.PASS,
            checked_artifacts=5,
            unsafe_match_count=0,
            safe_summary="Tenant scope held.",
            evidence_reference="tenant-scan",
        ),
        jinja_inventory=_jinja_inventory(),
        states=(
            MigrationProblem(
                reason="fallback",
                title="Fallback active",
                detail="Fallback remains reviewed.",
                next_action="Review after release.",
                severity=MigrationProblemSeverity.INFO,
                audit_reference="audit-fallback",
            ),
        ),
    )


def _jinja_inventory() -> JinjaInventoryDashboard:
    return JinjaInventoryDashboard(
        summary=JinjaInventorySummary(
            generated_at=datetime(2026, 5, 6, 12, tzinfo=UTC),
            total_items=1,
            template_count=1,
            route_count=0,
            static_asset_count=0,
            direct_link_count=0,
            blocked_count=0,
            safe_to_delete_count=0,
            reviewer_signoff_required=True,
        ),
        groups=(
            JinjaInventoryGroup(
                group_id="spec-039-shell-auth",
                label="Spec 039: Shell Auth",
                planned_removal_spec="039",
                blocked_count=0,
                safe_to_delete_count=0,
                items=(_inventory_item(),),
            ),
        ),
        evidence=(
            JinjaInventoryEvidence(
                evidence_id="scanner-qa038",
                evidence_type=JinjaInventoryEvidenceType.SCANNER,
                reference=(
                    "specs/038-jinja-surface-inventory-and-deletion-plan/"
                    "jinja_inventory.json"
                ),
                status=MigrationEvidenceStatus.PASS,
            ),
        ),
    )


def _inventory_item(
    *,
    classification: JinjaInventoryClassification = (
        JinjaInventoryClassification.REACT_PARITY_MISSING
    ),
    evidence_refs: tuple[str, ...] = ("scanner-qa038",),
    source_path: str | None = (
        "src/multi_agent_platform/web_admin/templates/admin_react/app.html"
    ),
) -> JinjaInventoryItem:
    return JinjaInventoryItem(
        item_id="template-admin-react-app",
        item_type=JinjaInventoryItemType.REACT_HOST,
        label="app.html",
        source_path=source_path,
        source_line=None,
        legacy_route="/admin/app",
        react_path="/admin/app",
        methods=(),
        owner_category="shell-auth",
        planned_removal_spec="039",
        classification=classification,
        evidence_refs=evidence_refs,
        blocker_refs=(),
        redirect_preserves=(),
        behaviors=(),
        reviewer_signoff_required=True,
        notes="Inventory item retained until deletion-grade parity is reviewed.",
    )


def _rollback_plan(
    asset_version_label: str = "Admin asset manifest qa037-safe",
) -> MigrationRollbackPlan:
    return MigrationRollbackPlan(
        plan_id="rollback-plan-qa037",
        status=MigrationOverallStatus.READY,
        feature_flag_label="Admin primary routing flag",
        asset_version_label=asset_version_label,
        steps=("Set fallback mode.",),
        verification_steps=("Open retained fallback.",),
        owner_label="Platform operations",
        last_reviewed_at=datetime(2026, 5, 5, 18, tzinfo=UTC),
        audit_reference="audit-qa037-rollback-plan",
    )


def _route_entry(
    *,
    admin_area: str = "Admin home",
    decision: MigrationRouteDecision = MigrationRouteDecision.REACT_PRIMARY,
    entry_id: str = "react-home",
    evidence: tuple[str, ...] = ("qa037-react-home",),
    retirement_allowed: bool = False,
) -> MigrationRouteEntry:
    return MigrationRouteEntry(
        entry_id=entry_id,
        admin_area=admin_area,
        legacy_route="/admin",
        react_route="/admin/app",
        decision=decision,
        scope_requirement=MigrationScopeRequirement.MIXED,
        auth_modes=("auth0-shaped", "local-principal"),
        parity_evidence=evidence,
        redirect_preserves=("tenant scope",),
        fallback_notice=None,
        retirement_allowed=retirement_allowed,
        rollback_reference="rollback-plan-qa037",
        audit_reference=f"audit-{entry_id}",
    )
