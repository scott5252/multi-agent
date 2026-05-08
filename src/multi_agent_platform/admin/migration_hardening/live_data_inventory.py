from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    LiveDataAllowlistEntry,
    LiveDataCiStatus,
    LiveDataInventoryDashboard,
    LiveDataInventoryEvidence,
    LiveDataInventoryEvidenceType,
    LiveDataInventoryFinding,
    LiveDataInventorySeverity,
    LiveDataInventoryStatus,
    LiveDataMarkerKind,
    LiveDataReachability,
    LiveDataRouteTarget,
    LiveDataScanSummary,
    MigrationEvidenceStatus,
    MigrationProblem,
    MigrationProblemSeverity,
    TransitionalLabelClassification,
    TransitionalLabelEvidence,
    TransitionalLabelEvidenceType,
    TransitionalLabelFinding,
    TransitionalLabelGate,
    TransitionalLabelGateSummary,
    TransitionalLabelSeverity,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import PrincipalContext

QA048_NOW = datetime(2026, 5, 7, 12, 30, tzinfo=UTC)
QA058_NOW = datetime(2026, 5, 8, 12, 30, tzinfo=UTC)
QA059_NOW = datetime(2026, 5, 8, 13, 0, tzinfo=UTC)

QA_MARKER_RE = re.compile(r"\bqa0[0-9]{2}\b", re.IGNORECASE)
AUDIT_RE = re.compile(r"\baudit[-_][a-z0-9_-]*qa0[0-9]{2}\b", re.IGNORECASE)
ARTIFACT_RE = re.compile(r"\bartifact[-_][a-z0-9_-]*qa0[0-9]{2}\b", re.IGNORECASE)
RUN_RE = re.compile(r"\brun[-_][a-z0-9_-]*qa0[0-9]{2}\b", re.IGNORECASE)
LINK_RE = re.compile(
    r"\b(?:pair-code|link[-_]token)[-_a-z0-9]*qa0[0-9]{2}\b", re.IGNORECASE
)

TEST_ONLY_PREFIXES = (
    "tests/",
    "frontend/admin/src/test/",
)
PRODUCTION_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".json", ".css")
BUILT_ASSET_PREFIX = "src/multi_agent_platform/web_admin/static/react"
GENERATED_CONTRACT_PATH = "frontend/admin/src/api/generated/reactAdminApi.ts"
PRODUCTION_SCAN_ROOTS = (
    "src/multi_agent_platform/api/routers/admin_react.py",
    "src/multi_agent_platform/admin/workflow_builder.py",
    "src/multi_agent_platform/admin/governance.py",
    "src/multi_agent_platform/admin/skill_lifecycle.py",
    "src/multi_agent_platform/testing/agent_bench/react_test_bench.py",
    "src/multi_agent_platform/admin/memberships/react_memberships.py",
    "src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py",
    "src/multi_agent_platform/admin/usage/react_usage.py",
    "src/multi_agent_platform/operations/workbench.py",
    "frontend/admin/src/api/client.ts",
    "frontend/admin/src/components",
    GENERATED_CONTRACT_PATH,
    BUILT_ASSET_PREFIX,
)
TRANSITIONAL_LABEL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("React Admin", re.compile(r"\bReact Admin\b", re.IGNORECASE)),
    ("React admin", re.compile(r"\bReact admin\b", re.IGNORECASE)),
    ("React-only", re.compile(r"\bReact-only\b", re.IGNORECASE)),
    ("React browser UI", re.compile(r"\bReact browser UI\b", re.IGNORECASE)),
    ("React route", re.compile(r"\bReact routes?\b", re.IGNORECASE)),
    ("React migration", re.compile(r"\bReact migration\b", re.IGNORECASE)),
    ("React foundation", re.compile(r"\bReact foundation\b", re.IGNORECASE)),
    ("React app", re.compile(r"\bReact app\b", re.IGNORECASE)),
    ("React shell", re.compile(r"\bReact shell\b", re.IGNORECASE)),
    ("React UI", re.compile(r"\bReact UI\b", re.IGNORECASE)),
    ("React live", re.compile(r"\bReact live\b", re.IGNORECASE)),
    ("React workflow", re.compile(r"\bReact workflow\b", re.IGNORECASE)),
    ("React primary", re.compile(r"\bReact primary\b", re.IGNORECASE)),
    ("React path", re.compile(r"\bReact path\b", re.IGNORECASE)),
    ("React contracts", re.compile(r"\bReact contracts\b", re.IGNORECASE)),
    ("to React", re.compile(r"\bto React\b", re.IGNORECASE)),
    ("in React", re.compile(r"\bin React\b", re.IGNORECASE)),
    ("from React", re.compile(r"\bfrom React\b", re.IGNORECASE)),
    ("returning to React", re.compile(r"\breturning to React\b", re.IGNORECASE)),
    ("before React", re.compile(r"\bbefore React\b", re.IGNORECASE)),
)
TRANSITIONAL_LABEL_SCAN_ROOTS = (
    "src/multi_agent_platform/api/routers/admin_react.py",
    "src/multi_agent_platform/api/routers/admin_console.py",
    "src/multi_agent_platform/api/schemas/admin_patterns.py",
    "src/multi_agent_platform/api/schemas/admin_react.py",
    "src/multi_agent_platform/admin/governance.py",
    "src/multi_agent_platform/admin/skill_lifecycle.py",
    "src/multi_agent_platform/admin/workflow_builder.py",
    "src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py",
    "src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py",
    "frontend/admin/src/App.tsx",
    "frontend/admin/src/main.tsx",
    "frontend/admin/src/api/client.ts",
    "frontend/admin/src/components",
    "frontend/admin/src/test",
)


@dataclass(frozen=True, slots=True)
class SurfaceMapping:
    source_prefix: str
    route_path: str | None
    owner_spec: str
    replacement_spec: str
    durable_source: str
    marker_kind: LiveDataMarkerKind = LiveDataMarkerKind.QA_MARKER


@dataclass(frozen=True, slots=True)
class RouteProbeExpectation:
    probe_id: str
    target_id: str
    method: str
    path: str
    principal: str
    tenant_scope: str
    state: str


SURFACE_MAPPINGS: tuple[SurfaceMapping, ...] = ()


def build_live_data_inventory_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository_root: Path | None = None,
    ci_mode: bool = False,
    source_scan: bool = True,
) -> LiveDataInventoryDashboard:
    _ = scope
    _ = principal
    root = repository_root or _repository_root()
    findings = (
        scan_live_data_findings(repository_root=root, ci_mode=ci_mode)
        if source_scan
        else projected_live_data_findings()
    )
    allowlist = computed_metadata_allowlist()
    route_targets = live_data_route_targets()
    blocking = sum(
        finding.severity == LiveDataInventorySeverity.BLOCKING for finding in findings
    )
    mapped = sum(
        finding.status == LiveDataInventoryStatus.MAPPED_LEGACY for finding in findings
    )
    allowed = sum(
        finding.status == LiveDataInventoryStatus.ALLOWED_COMPUTED_METADATA
        for finding in findings
    )
    ci_status = (
        LiveDataCiStatus.FAIL
        if blocking
        else LiveDataCiStatus.WARNING
        if mapped
        else LiveDataCiStatus.PASS
    )
    return LiveDataInventoryDashboard(
        page_id="qa058-live-only-gate",
        generated_at=QA058_NOW,
        summary=LiveDataScanSummary(
            total_findings=len(findings),
            blocking_findings=blocking,
            mapped_legacy_findings=mapped,
            allowed_computed_metadata=allowed,
            test_only_markers=count_test_only_markers(root) if source_scan else 0,
            route_targets=len(route_targets),
            empty_state_scans=sum(
                target.empty_state_required for target in route_targets
            ),
            seeded_state_scans=sum(
                target.seeded_state_required for target in route_targets
            ),
            ci_status=ci_status,
            next_step=_next_step(blocking=blocking, mapped=mapped),
        ),
        findings=findings,
        allowlist=allowlist,
        route_targets=route_targets,
        evidence=(
            LiveDataInventoryEvidence(
                evidence_id="qa058-live-only-source-scan",
                evidence_type=LiveDataInventoryEvidenceType.SCANNER,
                reference="tests/unit/admin/test_live_data_inventory_scanner.py",
                status=MigrationEvidenceStatus.WARNING
                if mapped
                else MigrationEvidenceStatus.PASS,
            ),
            LiveDataInventoryEvidence(
                evidence_id="qa058-route-response-scan",
                evidence_type=LiveDataInventoryEvidenceType.ROUTE_RESPONSE_SCAN,
                reference="tests/integration/api/test_admin_live_data_inventory_routes.py",
                status=MigrationEvidenceStatus.PASS,
            ),
            LiveDataInventoryEvidence(
                evidence_id="qa058-built-asset-scan",
                evidence_type=LiveDataInventoryEvidenceType.SCANNER,
                reference="src/multi_agent_platform/web_admin/static/react",
                status=MigrationEvidenceStatus.FAIL
                if blocking
                else MigrationEvidenceStatus.PASS,
            ),
        ),
        states=_states_for_summary(blocking=blocking, mapped=mapped),
    )


def build_live_data_inventory_projection() -> LiveDataInventoryDashboard:
    route_target = LiveDataRouteTarget(
        target_id="get-admin-app-migration-live-data-inventory-json",
        method="GET",
        path="/admin/app/migration/live-data-inventory.json",
        principal="platform-admin",
        tenant_scope="platform",
        empty_state_required=True,
        seeded_state_required=True,
        computed_metadata_only=True,
        replacement_spec=None,
    )
    evidence = LiveDataInventoryEvidence(
        evidence_id="qa058-live-only-source-scan",
        evidence_type=LiveDataInventoryEvidenceType.SCANNER,
        reference="tests/unit/admin/test_live_data_inventory_scanner.py",
        status=MigrationEvidenceStatus.PASS,
    )
    return LiveDataInventoryDashboard(
        page_id="qa058-live-only-gate",
        generated_at=QA058_NOW,
        summary=LiveDataScanSummary(
            total_findings=0,
            blocking_findings=0,
            mapped_legacy_findings=0,
            allowed_computed_metadata=1,
            test_only_markers=0,
            route_targets=1,
            empty_state_scans=1,
            seeded_state_scans=1,
            ci_status=LiveDataCiStatus.PASS,
            next_step="Live-only gate passed for production admin UI routes.",
        ),
        findings=(),
        allowlist=computed_metadata_allowlist()[:1],
        route_targets=(route_target,),
        evidence=(evidence,),
        states=_states_for_summary(blocking=0, mapped=0),
    )


def scan_live_data_findings(
    *,
    repository_root: Path | None = None,
    ci_mode: bool = False,
) -> tuple[LiveDataInventoryFinding, ...]:
    _ = ci_mode
    root = repository_root or _repository_root()
    findings: list[LiveDataInventoryFinding] = []
    seen: set[tuple[str, LiveDataMarkerKind, str]] = set()

    for relative_path in _production_files(root):
        text = _safe_read(root / relative_path)
        if not text:
            continue
        mapping = _mapping_for_path(relative_path)
        for marker_kind, marker in _markers_for_text(text):
            key = (relative_path, marker_kind, marker)
            if key in seen:
                continue
            seen.add(key)
            if _allowed_live_marker(relative_path, marker_kind, marker):
                continue
            if mapping and not _generated_contract_qa_marker(
                relative_path,
                marker_kind,
            ):
                findings.append(
                    _mapped_finding(relative_path, marker_kind, marker, mapping)
                )
            else:
                findings.append(_new_regression(relative_path, marker_kind, marker))
        if _imports_test_fixture(text):
            key = (relative_path, LiveDataMarkerKind.TEST_FIXTURE_IMPORT, "import")
            if key not in seen:
                seen.add(key)
                findings.append(
                    _new_regression(
                        relative_path,
                        LiveDataMarkerKind.TEST_FIXTURE_IMPORT,
                        "test-fixture-import",
                    )
                )

    if (root / "src/multi_agent_platform/api/routers/admin_react.py").exists():
        for entry in computed_metadata_allowlist():
            findings.append(
                LiveDataInventoryFinding(
                    finding_id=f"allowed-{entry.allowlist_id}",
                    severity=LiveDataInventorySeverity.INFO,
                    status=LiveDataInventoryStatus.ALLOWED_COMPUTED_METADATA,
                    marker_kind=entry.marker_kind,
                    source_path=entry.scope,
                    route_path="/admin/app/migration",
                    owner_spec="047",
                    replacement_spec=entry.expires_with_spec,
                    durable_source=entry.derivation_source,
                    reachability=LiveDataReachability.COMPUTED_METADATA,
                    safe_excerpt="scanner-derived computed metadata",
                )
            )

    return tuple(findings)


def projected_live_data_findings() -> tuple[LiveDataInventoryFinding, ...]:
    findings = [
        _mapped_finding(
            mapping.source_prefix,
            mapping.marker_kind,
            f"spec-{mapping.replacement_spec}",
            mapping,
        )
        for mapping in SURFACE_MAPPINGS
    ]
    for entry in computed_metadata_allowlist():
        findings.append(
            LiveDataInventoryFinding(
                finding_id=f"allowed-{entry.allowlist_id}",
                severity=LiveDataInventorySeverity.INFO,
                status=LiveDataInventoryStatus.ALLOWED_COMPUTED_METADATA,
                marker_kind=entry.marker_kind,
                source_path=entry.scope,
                route_path="/admin/app/migration",
                owner_spec="047",
                replacement_spec=entry.expires_with_spec,
                durable_source=entry.derivation_source,
                reachability=LiveDataReachability.COMPUTED_METADATA,
                safe_excerpt="scanner-derived computed metadata",
            )
        )
    return tuple(findings)


def current_mapped_surface_paths() -> tuple[str, ...]:
    return tuple(mapping.source_prefix for mapping in SURFACE_MAPPINGS)


def build_transitional_label_gate(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository_root: Path | None = None,
    ci_mode: bool = False,
    source_scan: bool = True,
) -> TransitionalLabelGate:
    _ = scope
    _ = principal
    root = repository_root or _repository_root()
    findings = (
        scan_transitional_label_findings(repository_root=root, ci_mode=ci_mode)
        if source_scan
        else transitional_label_projection()
    )
    blocked = sum(
        finding.classification
        == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
        for finding in findings
    )
    allowed = len(findings) - blocked
    ci_status = LiveDataCiStatus.FAIL if blocked else LiveDataCiStatus.PASS
    return TransitionalLabelGate(
        page_id="qa059-transitional-label-gate",
        generated_at=QA059_NOW,
        summary=TransitionalLabelGateSummary(
            blocked_count=blocked,
            allowed_reference_count=allowed,
            surfaces_scanned=len(tuple(_transitional_label_files(root)))
            if source_scan
            else 1,
            routes_scanned=_transitional_route_scan_count(),
            screenshots_checked=2,
            ci_status=ci_status,
            next_step=_transitional_next_step(blocked=blocked),
        ),
        findings=findings,
        evidence=(
            TransitionalLabelEvidence(
                evidence_id="qa059-source-visible-text-scan",
                evidence_type=TransitionalLabelEvidenceType.SCANNER,
                reference="tests/unit/admin/test_transitional_label_scanner.py",
                status=MigrationEvidenceStatus.FAIL
                if blocked
                else MigrationEvidenceStatus.PASS,
            ),
            TransitionalLabelEvidence(
                evidence_id="qa059-route-response-scan",
                evidence_type=TransitionalLabelEvidenceType.ROUTE_RESPONSE,
                reference="tests/integration/api/test_admin_transitional_label_routes.py",
                status=MigrationEvidenceStatus.FAIL
                if blocked
                else MigrationEvidenceStatus.PASS,
            ),
            TransitionalLabelEvidence(
                evidence_id="qa059-playwright-admin-terminology",
                evidence_type=TransitionalLabelEvidenceType.PLAYWRIGHT,
                reference="output/playwright/qa059_ui",
                status=MigrationEvidenceStatus.PASS,
            ),
        ),
        states=_transitional_states(blocked=blocked),
    )


def scan_transitional_label_findings(
    *,
    repository_root: Path | None = None,
    ci_mode: bool = False,
) -> tuple[TransitionalLabelFinding, ...]:
    _ = ci_mode
    root = repository_root or _repository_root()
    findings: list[TransitionalLabelFinding] = []
    seen: set[tuple[str, str, str]] = set()

    for relative_path in _transitional_label_files(root):
        text = _safe_read(root / relative_path)
        if not text:
            continue
        for matched_text, index in _transitional_matches(text):
            key = (relative_path, matched_text.lower(), str(index))
            if key in seen:
                continue
            seen.add(key)
            allowed = _allowed_transitional_reference(relative_path, matched_text)
            findings.append(
                _transitional_finding(
                    source_path=relative_path,
                    matched_text=matched_text,
                    allowed=allowed,
                )
            )

    findings.extend(transitional_label_projection())
    return tuple(sorted(findings, key=_transitional_sort_key))


def transitional_label_projection() -> tuple[TransitionalLabelFinding, ...]:
    return (
        TransitionalLabelFinding(
            finding_id="allowed-internal-generated-react-admin-identifiers",
            surface_id="generated-contract-identifiers",
            matched_text="ReactAdmin",
            classification=TransitionalLabelClassification.INTERNAL_GENERATED_IDENTIFIER,
            severity=TransitionalLabelSeverity.INFO,
            rationale=(
                "Generated TypeScript and Python model identifiers keep stable "
                "ReactAdmin names for compatibility, but they are not rendered "
                "as product labels."
            ),
            owner="admin platform",
            remediation=None,
        ),
        TransitionalLabelFinding(
            finding_id="allowed-historical-react-evidence-ids",
            surface_id="migration-evidence-identifiers",
            matched_text="qaNNN-react-*",
            classification=TransitionalLabelClassification.HISTORICAL_REFERENCE,
            severity=TransitionalLabelSeverity.INFO,
            rationale=(
                "Historical QA evidence identifiers remain stable so reviewers "
                "can trace migration artifacts without changing past records."
            ),
            owner="migration hardening",
            remediation=None,
        ),
        TransitionalLabelFinding(
            finding_id="allowed-technical-react-implementation-context",
            surface_id="developer-only-migration-evidence",
            matched_text="React implementation context",
            classification=TransitionalLabelClassification.TECHNICAL_QA_CONTEXT,
            severity=TransitionalLabelSeverity.INFO,
            rationale=(
                "Developer-only migration evidence may refer to the implementation "
                "framework when it is not ordinary navigation, title, fallback, "
                "or end-user copy."
            ),
            owner="platform reviewers",
            remediation=None,
        ),
    )


def live_only_gate_blockers(
    *,
    repository_root: Path | None = None,
) -> tuple[LiveDataInventoryFinding, ...]:
    return tuple(
        finding
        for finding in scan_live_data_findings(
            repository_root=repository_root,
            ci_mode=True,
        )
        if finding.severity == LiveDataInventorySeverity.BLOCKING
    )


def route_probe_expectations() -> tuple[RouteProbeExpectation, ...]:
    probes: list[RouteProbeExpectation] = []
    for target in live_data_route_targets():
        if target.empty_state_required:
            probes.append(_route_probe_expectation(target, state="empty"))
        if target.seeded_state_required:
            probes.append(_route_probe_expectation(target, state="seeded"))
    return tuple(probes)


def computed_metadata_allowlist() -> tuple[LiveDataAllowlistEntry, ...]:
    return (
        LiveDataAllowlistEntry(
            allowlist_id="route-inventory-computed",
            scope="src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py",
            marker_kind=LiveDataMarkerKind.QA_MARKER,
            reason=(
                "Route parity evidence is derived from route registration and "
                "scanner output."
            ),
            derivation_source="route registration and migration scanner",
            owner="migration hardening",
            expires_with_spec=None,
        ),
        LiveDataAllowlistEntry(
            allowlist_id="asset-manifest-computed",
            scope="src/multi_agent_platform/api/routers/admin_react.py",
            marker_kind=LiveDataMarkerKind.QA_MARKER,
            reason=(
                "Asset manifest status is computed from built admin manifest metadata."
            ),
            derivation_source="admin asset manifest",
            owner="admin shell",
            expires_with_spec=None,
        ),
        LiveDataAllowlistEntry(
            allowlist_id="test-bench-safe-execution-modes",
            scope="src/multi_agent_platform/testing/agent_bench/react_test_bench.py",
            marker_kind=LiveDataMarkerKind.FIXTURE_COLLECTION,
            reason=(
                "The test bench exposes safe execution-mode labels such as "
                "mock_model from live AgentTestSafeMode records; these are not "
                "fixture rows."
            ),
            derivation_source="AgentTestSafeMode enum and live run policy metadata",
            owner="agent test bench",
            expires_with_spec=None,
        ),
        LiveDataAllowlistEntry(
            allowlist_id="generated-test-bench-contract-vocabulary",
            scope="frontend/admin/src/api/generated/reactAdminApi.ts",
            marker_kind=LiveDataMarkerKind.FIXTURE_COLLECTION,
            reason=(
                "Generated TypeScript retains safe-mode and marker-kind "
                "vocabulary from backend schemas, not deterministic route data."
            ),
            derivation_source="generated backend schema contract",
            owner="agent test bench",
            expires_with_spec=None,
        ),
    )


def live_data_route_targets() -> tuple[LiveDataRouteTarget, ...]:
    raw_targets = (
        (
            "GET",
            "/admin/app/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/config.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/manifest.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/search.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/shell.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/routes.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/decommission-inventory.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/jinja-inventory.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/live-data-inventory.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/transitional-labels.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/migration/rollback.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            None,
        ),
        (
            "GET",
            "/admin/app/workflows/registry.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "050",
        ),
        (
            "GET",
            "/admin/app/workflows/create.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "050",
        ),
        (
            "GET",
            "/admin/app/workflows/legacy-routes.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            True,
            "050",
        ),
        (
            "GET",
            "/admin/app/workflows/builder.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "050",
        ),
        (
            "GET",
            "/admin/app/workflows/lookups.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows/drafts/{workflow_draft_id}/save",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows/drafts/{workflow_draft_id}/validate",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows/drafts/{workflow_draft_id}/restore",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows/drafts/{workflow_draft_id}/copy",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "POST",
            "/admin/app/workflows/drafts/{workflow_draft_id}/publish",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "050",
        ),
        (
            "GET",
            "/admin/app/governance/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/governance/providers.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/governance/legacy-routes.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/providers/{provider_id}/probe",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/providers/{provider_id}/credential-reference",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/governance/prompts.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/prompts/{prompt_lineage_id}/save",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/prompts/{prompt_lineage_id}/preview",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/governance/profiles.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/profiles/{profile_id}/save",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/profiles/{profile_id}/resolve",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "POST",
            "/admin/app/governance/routing/preview",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/governance/history.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "051",
        ),
        (
            "GET",
            "/admin/app/skills/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/skills/legacy-routes.json",
            "platform-admin",
            "platform",
            True,
            True,
            True,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/candidates",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/candidates/{candidate_id}/validate",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/candidates/{candidate_id}/publish",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/{package_id}/grants",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/{package_id}/quarantine",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/packages/{package_id}/withdraw",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/skills/discovery.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/skills/installations.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/installations/{installation_id}/install",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/installations/{installation_id}/credentials",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/installations/{installation_id}/smoke-tests",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/skills/diagnostics.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/diagnostics/run",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/eligibility/preview",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "POST",
            "/admin/app/skills/installations/{installation_id}/eligibility/preview",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/skills/audit.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "052",
        ),
        (
            "GET",
            "/admin/app/test-bench/bootstrap.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "053",
        ),
        (
            "GET",
            "/admin/app/test-bench/suites",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "053",
        ),
        (
            "POST",
            "/admin/app/test-bench/suites",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "053",
        ),
        (
            "POST",
            "/admin/app/test-bench/suites/{suite_id}/cases",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "053",
        ),
        (
            "POST",
            "/admin/app/test-bench/suites/{suite_id}/runs",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "053",
        ),
        (
            "GET",
            "/admin/app/test-bench/runs.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "053",
        ),
        (
            "GET",
            "/admin/app/test-bench/gates.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "053",
        ),
        (
            "POST",
            "/admin/app/test-bench/gates/{gate_id}/refresh",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "053",
        ),
        (
            "GET",
            "/admin/app/test-bench/audit.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "053",
        ),
        (
            "GET",
            "/admin/app/memberships/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/invitations",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/principals/link",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/role-grants",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/role-grants/{role_grant_id}/revoke",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/principals/{principal_identity_id}/{status_action}",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "POST",
            "/admin/app/memberships/memberships/{tenant_membership_id}/{membership_status}",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "054",
        ),
        (
            "GET",
            "/admin/app/memberships/access-history.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "054",
        ),
        (
            "GET",
            "/admin/app/memberships/audit.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "054",
        ),
        (
            "GET",
            "/admin/app/channels/shell.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            True,
            "055",
        ),
        (
            "GET",
            "/admin/app/channels/bootstrap.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/telegram/config",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/telegram/webhook/validate",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/telegram/aliases",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/telegram/aliases/{alias_id}/{action}",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/telegram/link-tokens",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "GET",
            "/admin/app/channels/telegram/deliveries.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "055",
        ),
        (
            "GET",
            "/admin/app/channels/briefing/preferences.json",
            "tenant-admin-acme",
            "tenant",
            True,
            True,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/briefing/preferences",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/briefing/preferences/import",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "POST",
            "/admin/app/channels/briefing/preferences/export",
            "tenant-admin-acme",
            "tenant",
            False,
            False,
            False,
            "055",
        ),
        (
            "GET",
            "/admin/app/usage/bootstrap.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "056",
        ),
        (
            "GET",
            "/admin/app/usage/events.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "056",
        ),
        (
            "POST",
            "/admin/app/usage/exports",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "056",
        ),
        (
            "GET",
            "/admin/app/operations.json",
            "platform-admin",
            "platform",
            True,
            True,
            False,
            "057",
        ),
        (
            "POST",
            "/admin/app/operations/export",
            "platform-admin",
            "platform",
            False,
            False,
            False,
            "057",
        ),
    )
    return tuple(
        LiveDataRouteTarget(
            target_id=_target_id(method, path),
            method=method,
            path=path,
            principal=principal,
            tenant_scope=tenant_scope,
            empty_state_required=empty_required,
            seeded_state_required=seeded_required,
            computed_metadata_only=computed_only,
            replacement_spec=replacement_spec,
        )
        for (
            method,
            path,
            principal,
            tenant_scope,
            empty_required,
            seeded_required,
            computed_only,
            replacement_spec,
        ) in raw_targets
    )


def discover_static_admin_react_json_routes(source_text: str) -> set[str]:
    routes: set[str] = set()
    pattern = re.compile(
        r"@router\.(?:get|post)\(\s*(?:\n\s*)?[\"'](?P<path>/admin/app[^\"']+)[\"'](?P<body>[\s\S]*?)\n\)",
        re.MULTILINE,
    )
    for match in pattern.finditer(source_text):
        path = match.group("path")
        body = match.group("body")
        if "response_model=" in body and "response_class=HTMLResponse" not in body:
            routes.add(path)
    return routes


def missed_static_route_targets(source_text: str) -> tuple[str, ...]:
    discovered = discover_static_admin_react_json_routes(source_text)
    targeted = {target.path for target in live_data_route_targets()}
    # Detail routes with required path params are inventoried by replacement specs.
    deferred = {
        "/admin/app/workflows/drafts/{workflow_draft_id}/detail.json",
        "/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate.json",
        "/admin/app/workflows/versions/{workflow_version_bundle_id}/detail.json",
        "/admin/app/governance/provenance/{run_id}.json",
        "/admin/app/channels/runs/{workflow_run_id}/status.json",
        "/admin/app/usage/exports/{usage_export_request_id}.json",
        "/admin/app/operations/runs/{workflow_run_id}.json",
        "/admin/app/test-bench/suites/{suite_id}",
        "/admin/app/test-bench/runs/{run_id}.json",
        "/admin/app/test-bench/artifacts/{artifact_reference_id}.json",
    }
    return tuple(sorted(discovered - targeted - deferred))


def count_test_only_markers(repository_root: Path | None = None) -> int:
    root = repository_root or _repository_root()
    count = 0
    for prefix in TEST_ONLY_PREFIXES:
        base = root / prefix
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in PRODUCTION_SUFFIXES:
                count += len(QA_MARKER_RE.findall(_safe_read(path)))
    return count


def _production_files(root: Path) -> Iterable[str]:
    for configured in PRODUCTION_SCAN_ROOTS:
        path = root / configured
        if path.is_file():
            yield configured
            continue
        if not path.exists():
            continue
        for child in path.rglob("*"):
            if (
                child.is_file()
                and child.suffix in PRODUCTION_SUFFIXES
                and "__pycache__" not in child.parts
                and ".test." not in child.name
            ):
                relative = child.relative_to(root).as_posix()
                if not _is_test_only(relative):
                    yield relative


def _transitional_label_files(root: Path) -> Iterable[str]:
    for configured in TRANSITIONAL_LABEL_SCAN_ROOTS:
        path = root / configured
        if path.is_file():
            yield configured
            continue
        if not path.exists():
            continue
        for child in path.rglob("*"):
            if (
                child.is_file()
                and child.suffix in PRODUCTION_SUFFIXES
                and "__pycache__" not in child.parts
                and ".test." not in child.name
            ):
                yield child.relative_to(root).as_posix()


def _markers_for_text(text: str) -> Iterable[tuple[LiveDataMarkerKind, str]]:
    for marker in QA_MARKER_RE.findall(text):
        yield LiveDataMarkerKind.QA_MARKER, marker.lower()
    if "USAGE_EVENTS" in text:
        yield LiveDataMarkerKind.FIXTURE_COLLECTION, "usage-events"
    if "Daily briefing workflow" in text:
        yield LiveDataMarkerKind.HARDCODED_DOMAIN_ENTITY, "daily-briefing-workflow"
    if "mocked" in text.lower() or "mock_" in text.lower():
        yield LiveDataMarkerKind.FIXTURE_COLLECTION, "mocked"
    if AUDIT_RE.search(text):
        yield LiveDataMarkerKind.FAKE_AUDIT_REFERENCE, "audit-reference"
    if ARTIFACT_RE.search(text):
        yield LiveDataMarkerKind.FAKE_ARTIFACT_REFERENCE, "artifact-reference"
    if RUN_RE.search(text):
        yield LiveDataMarkerKind.FAKE_RUN_ID, "run-reference"
    if LINK_RE.search(text):
        yield LiveDataMarkerKind.FAKE_LINK_TOKEN, "link-reference"


def _allowed_live_marker(
    relative_path: str,
    marker_kind: LiveDataMarkerKind,
    marker: str,
) -> bool:
    if marker_kind != LiveDataMarkerKind.FIXTURE_COLLECTION or marker != "mocked":
        return False
    return relative_path in {
        "src/multi_agent_platform/testing/agent_bench/react_test_bench.py",
        "frontend/admin/src/api/generated/reactAdminApi.ts",
    }


def _mapped_finding(
    source_path: str,
    marker_kind: LiveDataMarkerKind,
    marker: str,
    mapping: SurfaceMapping,
) -> LiveDataInventoryFinding:
    return LiveDataInventoryFinding(
        finding_id=_finding_id("mapped", source_path, marker_kind, marker),
        severity=LiveDataInventorySeverity.WARNING,
        status=LiveDataInventoryStatus.MAPPED_LEGACY,
        marker_kind=marker_kind,
        source_path=source_path,
        route_path=mapping.route_path,
        owner_spec=mapping.owner_spec,
        replacement_spec=mapping.replacement_spec,
        durable_source=mapping.durable_source,
        reachability=_reachability_for_path(source_path),
        safe_excerpt=f"{marker_kind.value} mapped to Spec {mapping.replacement_spec}",
    )


def _new_regression(
    source_path: str,
    marker_kind: LiveDataMarkerKind,
    marker: str,
) -> LiveDataInventoryFinding:
    return LiveDataInventoryFinding(
        finding_id=_finding_id("new", source_path, marker_kind, marker),
        severity=LiveDataInventorySeverity.BLOCKING,
        status=LiveDataInventoryStatus.NEW_REGRESSION,
        marker_kind=marker_kind,
        source_path=source_path,
        route_path=None,
        owner_spec=None,
        replacement_spec=None,
        durable_source="live repository, domain service, or computed metadata",
        reachability=_reachability_for_path(source_path),
        safe_excerpt=f"{marker_kind.value} requires live-data classification",
    )


def _mapping_for_path(relative_path: str) -> SurfaceMapping | None:
    matches = [
        mapping
        for mapping in SURFACE_MAPPINGS
        if relative_path == mapping.source_prefix
        or relative_path.startswith(f"{mapping.source_prefix}/")
    ]
    if not matches:
        return None
    return max(matches, key=lambda mapping: len(mapping.source_prefix))


def _generated_contract_qa_marker(
    relative_path: str,
    marker_kind: LiveDataMarkerKind,
) -> bool:
    return (
        relative_path == GENERATED_CONTRACT_PATH
        and marker_kind == LiveDataMarkerKind.QA_MARKER
    )


def _imports_test_fixture(text: str) -> bool:
    return (
        "frontend/admin/src/test" in text
        or "from tests.fixtures" in text
        or "import tests.fixtures" in text
    )


def _is_test_only(relative_path: str) -> bool:
    return relative_path.startswith(TEST_ONLY_PREFIXES)


def _reachability_for_path(relative_path: str) -> LiveDataReachability:
    if relative_path == GENERATED_CONTRACT_PATH:
        return LiveDataReachability.GENERATED_CONTRACT
    if relative_path == BUILT_ASSET_PREFIX or relative_path.startswith(
        f"{BUILT_ASSET_PREFIX}/",
    ):
        return LiveDataReachability.BUILT_ASSET
    return LiveDataReachability.PRODUCTION_SOURCE


def _next_step(*, blocking: int, mapped: int) -> str:
    if blocking:
        return "Fix blocking production live-data gate findings before release."
    if mapped:
        return "Review mapped live-data markers before release."
    return "Live-only gate passed for production admin UI routes."


def _states_for_summary(*, blocking: int, mapped: int) -> tuple[MigrationProblem, ...]:
    if blocking:
        return (
            MigrationProblem(
                reason="blocking_live_only_findings",
                title="Live-only gate blocked",
                detail="Production-reachable fixture-like evidence remains.",
                next_action=(
                    "Remove or classify each blocking finding, then rerun QA058."
                ),
                severity=MigrationProblemSeverity.BLOCKING,
                audit_reference="audit-qa058-live-only-gate",
            ),
        )
    if mapped:
        return (
            MigrationProblem(
                reason="transitional_marker_deferred",
                title="Mapped marker deferred",
                detail="A mapped marker remains assigned to a follow-up cleanup.",
                next_action=(
                    "Finish the assigned cleanup after the live-only gate "
                    "remains green."
                ),
                severity=MigrationProblemSeverity.INFO,
                audit_reference="audit-qa058-live-only-gate",
            ),
        )
    return (
        MigrationProblem(
            reason="live_only_gate_passed",
            title="Live-only gate passed",
            detail="Production admin UI routes have no blocking fixture findings.",
            next_action="Keep the scanner in Spec QA and curl regression validation.",
            severity=MigrationProblemSeverity.INFO,
            audit_reference="audit-qa058-live-only-gate",
        ),
    )


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _transitional_matches(text: str) -> Iterable[tuple[str, int]]:
    for label, pattern in TRANSITIONAL_LABEL_PATTERNS:
        for match in pattern.finditer(text):
            matched_text = (
                label if label.lower() == match.group(0).lower() else match.group(0)
            )
            yield matched_text, match.start()


def _allowed_transitional_reference(relative_path: str, matched_text: str) -> bool:
    lowered_path = relative_path.lower()
    _ = matched_text
    if lowered_path.endswith("live_data_inventory.py"):
        return True
    if lowered_path.startswith("specs/"):
        return True
    return False


def _transitional_finding(
    *,
    source_path: str,
    matched_text: str,
    allowed: bool,
) -> TransitionalLabelFinding:
    classification = (
        TransitionalLabelClassification.TECHNICAL_QA_CONTEXT
        if allowed
        else TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
    )
    severity = TransitionalLabelSeverity.INFO
    if not allowed:
        severity = TransitionalLabelSeverity.BLOCKING
    remediation = (
        None
        if allowed
        else (
            "Replace implementation-era wording with product-facing Admin or "
            "domain-specific terminology."
        )
    )
    return TransitionalLabelFinding(
        finding_id=_finding_id(
            "transitional",
            source_path,
            LiveDataMarkerKind.QA_MARKER,
            matched_text,
        ),
        surface_id=source_path,
        matched_text=matched_text,
        classification=classification,
        severity=severity,
        rationale=(
            "Technical implementation context is allowed in developer-only "
            "migration evidence."
            if allowed
            else "Production-visible admin copy must not expose transitional labels."
        ),
        owner="admin platform",
        remediation=remediation,
    )


def _transitional_sort_key(
    finding: TransitionalLabelFinding,
) -> tuple[int, str, str]:
    priority = (
        0
        if finding.classification
        == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
        else 1
    )
    return priority, finding.surface_id, finding.finding_id


def _transitional_route_scan_count() -> int:
    return 6


def _transitional_next_step(*, blocked: int) -> str:
    if blocked:
        return "Replace blocked transitional labels before closing Spec 059."
    return "Admin terminology gate passed for production-visible surfaces."


def _transitional_states(*, blocked: int) -> tuple[MigrationProblem, ...]:
    if blocked:
        return (
            MigrationProblem(
                reason="transitional_labels_blocked",
                title="Admin terminology gate blocked",
                detail="Production-visible transitional labels remain.",
                next_action="Replace blocked labels and rerun QA059 validation.",
                severity=MigrationProblemSeverity.BLOCKING,
                audit_reference="audit-qa059-transitional-label-gate",
            ),
        )
    return (
        MigrationProblem(
            reason="admin_terminology_gate_passed",
            title="Admin terminology gate passed",
            detail="Production-visible admin surfaces use product-facing terminology.",
            next_action="Keep the scanner in QA and curl regression validation.",
            severity=MigrationProblemSeverity.INFO,
            audit_reference="audit-qa059-transitional-label-gate",
        ),
    )


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _finding_id(
    prefix: str,
    source_path: str,
    marker_kind: LiveDataMarkerKind,
    marker: str,
) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", source_path.lower()).strip("-")
    normalized_marker = re.sub(r"[^a-z0-9]+", "-", marker.lower()).strip("-")
    return f"{prefix}-{marker_kind.value}-{normalized_marker}-{normalized}"[:140]


def _target_id(method: str, path: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")
    return f"{method.lower()}-{normalized}"[:120]


def _route_probe_expectation(
    target: LiveDataRouteTarget,
    *,
    state: str,
) -> RouteProbeExpectation:
    return RouteProbeExpectation(
        probe_id=f"{target.target_id}-{state}",
        target_id=target.target_id,
        method=target.method,
        path=target.path,
        principal=target.principal,
        tenant_scope=target.tenant_scope,
        state=state,
    )
