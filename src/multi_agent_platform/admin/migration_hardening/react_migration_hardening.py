from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    AdminMigrationHardeningDashboard,
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
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import PrincipalContext

from .jinja_inventory import build_jinja_inventory_dashboard

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
QA037_NOW = datetime(2026, 5, 5, 18, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class MigrationActor:
    platform_admin: bool
    tenant_admin: bool
    tenant_user: bool
    active_tenant_id: UUID | None
    principal_label: str


def build_migration_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> AdminMigrationHardeningDashboard:
    actor = _actor(scope=scope, principal=principal)
    groups = build_migration_route_groups(scope=scope, principal=principal)
    entries = tuple(entry for group in groups for entry in group.entries)
    return AdminMigrationHardeningDashboard(
        page_id="qa037-react-admin-migration-hardening",
        title="React Admin Migration Hardening",
        description=(
            "Verify route parity, direct-link safety, rollback readiness, "
            "accessibility, performance, redaction, and tenant isolation."
        ),
        scope=scope,
        updated_at=QA037_NOW,
        summary=_summary(entries),
        route_groups=groups,
        rollback_plan=build_migration_rollback_plan(
            scope=scope,
            principal=principal,
        ),
        performance_budget=_performance_budget(),
        accessibility_audit=_accessibility_audit(),
        redaction_sweep=_redaction_sweep(),
        tenant_isolation_sweep=_tenant_isolation_sweep(actor),
        jinja_inventory=build_jinja_inventory_dashboard(
            scope=scope,
            principal=principal,
            item_limit_per_group=0,
        ),
        states=_states(entries, actor),
    )


def build_migration_route_groups(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> tuple[MigrationRouteGroup, ...]:
    actor = _actor(scope=scope, principal=principal)
    groups = _all_route_groups()
    if actor.platform_admin:
        return groups
    if actor.tenant_admin:
        return tuple(_filter_group_for_tenant_admin(group) for group in groups)
    if actor.tenant_user:
        return tuple(_filter_group_for_tenant_user(group) for group in groups)
    return ()


def build_migration_rollback_plan(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> MigrationRollbackPlan:
    _ = scope
    _ = principal
    return MigrationRollbackPlan(
        plan_id="rollback-plan-qa037",
        status=MigrationOverallStatus.READY,
        feature_flag_label="React admin primary routing flag",
        asset_version_label="React asset manifest qa037-safe",
        steps=(
            "Set React admin primary routing flag to fallback mode.",
            "Pin the previous reviewed React asset manifest.",
            "Keep backend domain services running without data rollback.",
            "Verify legacy fallback routes and retained direct links.",
        ),
        verification_steps=(
            "Open retained admin fallback route as platform administrator.",
            "Open Acme tenant route with tenant scope preserved.",
            "Confirm redaction sweep still reports zero unsafe matches.",
        ),
        owner_label="Platform operations",
        last_reviewed_at=QA037_NOW,
        audit_reference="audit-qa037-rollback-plan",
    )


def _actor(*, scope: ReactAdminScope, principal: PrincipalContext) -> MigrationActor:
    roles = set(principal.role_codes)
    return MigrationActor(
        platform_admin="platform_admin" in roles,
        tenant_admin="tenant_admin" in roles,
        tenant_user="tenant_user" in roles or "tenant_admin" in roles,
        active_tenant_id=(
            scope.tenant_id if scope.scope_type == ReactAdminScopeType.TENANT else None
        ),
        principal_label=principal.principal_id,
    )


def _summary(
    entries: tuple[MigrationRouteEntry, ...],
) -> MigrationHardeningSummary:
    return MigrationHardeningSummary(
        total_destinations=len(entries),
        react_primary_count=sum(
            entry.decision == MigrationRouteDecision.REACT_PRIMARY for entry in entries
        ),
        redirect_count=sum(
            entry.decision == MigrationRouteDecision.REDIRECT for entry in entries
        ),
        retained_fallback_count=sum(
            entry.decision == MigrationRouteDecision.RETAINED_FALLBACK
            for entry in entries
        ),
        retirement_candidate_count=sum(
            entry.decision == MigrationRouteDecision.RETIREMENT_CANDIDATE
            for entry in entries
        ),
        blocked_count=sum(
            entry.decision == MigrationRouteDecision.BLOCKED for entry in entries
        ),
        overall_status=MigrationOverallStatus.READY
        if entries
        and not any(
            entry.decision == MigrationRouteDecision.BLOCKED for entry in entries
        )
        else MigrationOverallStatus.PARTIAL,
        next_step=(
            "Keep retained fallbacks for the soak window and review "
            "retirement candidates after release evidence is complete."
        ),
    )


def _entry(
    *,
    entry_id: str,
    admin_area: str,
    legacy_route: str | None,
    react_route: str | None,
    decision: MigrationRouteDecision,
    scope_requirement: MigrationScopeRequirement,
    evidence: tuple[str, ...],
    retirement_allowed: bool = False,
    fallback_notice: str | None = None,
    redirect_preserves: tuple[str, ...] = ("tenant scope", "query filters"),
) -> MigrationRouteEntry:
    return MigrationRouteEntry(
        entry_id=entry_id,
        admin_area=admin_area,
        legacy_route=legacy_route,
        react_route=react_route,
        decision=decision,
        scope_requirement=scope_requirement,
        auth_modes=("auth0-shaped", "local-principal"),
        parity_evidence=evidence,
        redirect_preserves=redirect_preserves,
        fallback_notice=fallback_notice,
        retirement_allowed=retirement_allowed,
        rollback_reference="rollback-plan-qa037",
        audit_reference=f"audit-qa037-{entry_id}",
    )


def _all_route_groups() -> tuple[MigrationRouteGroup, ...]:
    groups: list[MigrationRouteGroup] = [
        MigrationRouteGroup(
            group_id="foundation-shell-qa037",
            label="React foundation and shell",
            spec_refs=("026", "027", "028"),
            group_status=MigrationOverallStatus.READY,
            entries=(
                _entry(
                    entry_id="react-home-qa037",
                    admin_area="React admin home",
                    legacy_route="/admin",
                    react_route="/admin/app",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.MIXED,
                    evidence=("qa037-react-home", "audit-qa037-shell"),
                    retirement_allowed=False,
                    fallback_notice="Existing admin index remains a rollback entry.",
                ),
                _entry(
                    entry_id="patterns-qa037",
                    admin_area="Shared data and form patterns",
                    legacy_route="/admin/patterns",
                    react_route="/admin/app/patterns",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.MIXED,
                    evidence=("qa028-react-patterns",),
                ),
            ),
        ),
        MigrationRouteGroup(
            group_id="operations-workflows-qa037",
            label="Operations and workflow authoring",
            spec_refs=("003", "008", "009", "013", "019", "020", "024", "029", "030"),
            group_status=MigrationOverallStatus.PARTIAL,
            entries=(
                _entry(
                    entry_id="operations-qa037",
                    admin_area="Operations workbench",
                    legacy_route="/admin/operations",
                    react_route="/admin/app/operations",
                    decision=MigrationRouteDecision.RETAINED_FALLBACK,
                    scope_requirement=MigrationScopeRequirement.PLATFORM,
                    evidence=("qa029-react-operations",),
                    fallback_notice="Retained for two-release operations fallback.",
                ),
                _entry(
                    entry_id="workflow-builder-qa037",
                    admin_area="Workflow builder",
                    legacy_route="/admin/workflows/ui",
                    react_route="/admin/app/workflows",
                    decision=MigrationRouteDecision.RETAINED_FALLBACK,
                    scope_requirement=MigrationScopeRequirement.TENANT_ADMIN,
                    evidence=("qa030-react-workflows",),
                    fallback_notice="Retained until publish rollback window closes.",
                ),
                _entry(
                    entry_id="run-workbench-qa037",
                    admin_area="Run debug workbench",
                    legacy_route="/admin/runs",
                    react_route="/admin/app/operations",
                    decision=MigrationRouteDecision.ALIAS,
                    scope_requirement=MigrationScopeRequirement.PLATFORM,
                    evidence=("qa029-run-debug-workbench",),
                    retirement_allowed=True,
                ),
            ),
        ),
        MigrationRouteGroup(
            group_id="governance-skills-tests-qa037",
            label="Governance, skills, and test bench",
            spec_refs=(
                "007",
                "011",
                "012",
                "014",
                "014-v2",
                "015",
                "021",
                "025",
                "031",
                "032",
                "033",
            ),
            group_status=MigrationOverallStatus.READY,
            entries=(
                _entry(
                    entry_id="governance-qa037",
                    admin_area="Model, prompt, profile, and provider governance",
                    legacy_route="/admin/model-providers",
                    react_route="/admin/app/governance",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.PLATFORM,
                    evidence=("qa031-react-governance",),
                    retirement_allowed=True,
                ),
                _entry(
                    entry_id="skills-qa037",
                    admin_area="Skill registry and tool execution",
                    legacy_route="/admin/skills",
                    react_route="/admin/app/skills",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.TENANT_ADMIN,
                    evidence=("qa032-react-skills",),
                    retirement_allowed=True,
                ),
                _entry(
                    entry_id="test-bench-qa037",
                    admin_area="Agent and workflow test bench",
                    legacy_route="/admin/test-bench",
                    react_route="/admin/app/test-bench",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.TENANT_ADMIN,
                    evidence=("qa033-react-test-bench",),
                    retirement_allowed=True,
                ),
            ),
        ),
        MigrationRouteGroup(
            group_id="people-usage-channels-qa037",
            label="People, usage, channels, and preferences",
            spec_refs=("006", "016", "017", "018", "022", "023", "034", "035", "036"),
            group_status=MigrationOverallStatus.READY,
            entries=(
                _entry(
                    entry_id="memberships-qa037",
                    admin_area="Membership administration",
                    legacy_route="/admin/memberships",
                    react_route="/admin/app/memberships",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.TENANT_ADMIN,
                    evidence=("qa034-react-memberships",),
                    retirement_allowed=True,
                ),
                _entry(
                    entry_id="usage-qa037",
                    admin_area="Usage and cost analytics",
                    legacy_route="/admin/usage",
                    react_route="/admin/app/usage",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.TENANT_ADMIN,
                    evidence=("qa035-react-usage",),
                    retirement_allowed=True,
                ),
                _entry(
                    entry_id="channels-qa037",
                    admin_area="Channel, Telegram, and briefing preferences",
                    legacy_route="/admin/telegram",
                    react_route="/admin/app/channels",
                    decision=MigrationRouteDecision.REACT_PRIMARY,
                    scope_requirement=MigrationScopeRequirement.MIXED,
                    evidence=("qa036-react-channels",),
                    retirement_allowed=True,
                    redirect_preserves=("tenant scope", "run status link"),
                ),
            ),
        ),
    ]
    return tuple(groups)


def _filter_group_for_tenant_admin(group: MigrationRouteGroup) -> MigrationRouteGroup:
    allowed = {
        MigrationScopeRequirement.TENANT_ADMIN,
        MigrationScopeRequirement.TENANT_USER,
        MigrationScopeRequirement.MIXED,
    }
    entries = tuple(
        entry for entry in group.entries if entry.scope_requirement in allowed
    )
    return group.model_copy(update={"entries": entries})


def _filter_group_for_tenant_user(group: MigrationRouteGroup) -> MigrationRouteGroup:
    allowed = {MigrationScopeRequirement.TENANT_USER, MigrationScopeRequirement.MIXED}
    entries = tuple(
        entry for entry in group.entries if entry.scope_requirement in allowed
    )
    return group.model_copy(update={"entries": entries})


def _performance_budget() -> MigrationPerformanceBudget:
    return MigrationPerformanceBudget(
        budget_id="performance-budget-qa037",
        route_bootstrap_ms_limit=500,
        primary_interactive_ms_limit=2000,
        compressed_asset_kb_limit=250,
        status=MigrationEvidenceStatus.PASS,
        mitigation="No mitigation required for deterministic QA037 evidence.",
        measurements=(
            MigrationPerformanceMeasurement(
                measurement_id="bootstrap-home-qa037",
                label="React admin home bootstrap",
                value=214,
                unit="ms",
                limit=500,
                status=MigrationEvidenceStatus.PASS,
                evidence_reference="perf-qa037-home-bootstrap",
            ),
            MigrationPerformanceMeasurement(
                measurement_id="interactive-matrix-qa037",
                label="Migration matrix interactive",
                value=820,
                unit="ms",
                limit=2000,
                status=MigrationEvidenceStatus.PASS,
                evidence_reference="perf-qa037-matrix-interactive",
            ),
            MigrationPerformanceMeasurement(
                measurement_id="compressed-assets-qa037",
                label="React admin compressed assets",
                value=159,
                unit="kb",
                limit=250,
                status=MigrationEvidenceStatus.PASS,
                evidence_reference="asset-budget-qa037",
            ),
        ),
    )


def _accessibility_audit() -> MigrationAccessibilityAudit:
    return MigrationAccessibilityAudit(
        audit_id="accessibility-audit-qa037",
        status=MigrationEvidenceStatus.PASS,
        viewport_coverage=("desktop 1440x900", "mobile 390x844"),
        keyboard_status=MigrationEvidenceStatus.PASS,
        focus_status=MigrationEvidenceStatus.PASS,
        landmark_status=MigrationEvidenceStatus.PASS,
        label_status=MigrationEvidenceStatus.PASS,
        contrast_state_status=MigrationEvidenceStatus.PASS,
        text_overlap_status=MigrationEvidenceStatus.PASS,
        evidence_references=(
            "qa037-react-home-desktop",
            "qa037-react-home-mobile",
            "qa037-keyboard-checklist",
        ),
    )


def _redaction_sweep() -> MigrationSweepSummary:
    return MigrationSweepSummary(
        sweep_id="redaction-sweep-qa037",
        status=MigrationEvidenceStatus.PASS,
        checked_artifacts=37,
        unsafe_match_count=0,
        safe_summary="No unsafe migration evidence markers found.",
        evidence_reference="redaction-scan-qa037",
    )


def _tenant_isolation_sweep(actor: MigrationActor) -> MigrationSweepSummary:
    checked = 12 if actor.platform_admin else 6
    return MigrationSweepSummary(
        sweep_id="tenant-isolation-sweep-qa037",
        status=MigrationEvidenceStatus.PASS,
        checked_artifacts=checked,
        unsafe_match_count=0,
        safe_summary="Tenant-scoped route evidence stayed within authorized scope.",
        evidence_reference="tenant-isolation-qa037",
    )


def _states(
    entries: tuple[MigrationRouteEntry, ...],
    actor: MigrationActor,
) -> tuple[MigrationProblem, ...]:
    states = [
        MigrationProblem(
            reason="retained_fallbacks",
            title="Fallback window active",
            detail="Read-only fallback routes remain available during the soak window.",
            next_action=(
                "Review retained fallback counts after release evidence is complete."
            ),
            severity=MigrationProblemSeverity.INFO,
            audit_reference="audit-qa037-retained-fallbacks",
        )
    ]
    if any(not entry.retirement_allowed for entry in entries):
        states.append(
            MigrationProblem(
                reason="retirement_blocked",
                title="Some routes are not retirement-ready",
                detail=(
                    "Routes without complete parity evidence remain retained fallbacks."
                ),
                next_action="Keep rollback and direct-link guidance visible.",
                severity=MigrationProblemSeverity.WARNING,
                audit_reference="audit-qa037-retirement-blocked",
            )
        )
    if actor.tenant_user and not actor.tenant_admin:
        states.append(
            MigrationProblem(
                reason="user_scope_limited",
                title="User scope limited",
                detail="Only user-safe migration coverage is shown for this principal.",
                next_action="Use a tenant administrator for tenant route decisions.",
                severity=MigrationProblemSeverity.INFO,
                audit_reference="audit-qa037-user-scope",
            )
        )
    return tuple(states)
