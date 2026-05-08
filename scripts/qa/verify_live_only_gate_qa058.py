from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from multi_agent_platform.admin.migration_hardening import (
    build_live_data_inventory_dashboard,
    live_data_route_targets,
    live_only_gate_blockers,
    missed_static_route_targets,
    route_probe_expectations,
    scan_live_data_findings,
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

ARTIFACT_PATH = Path(".data/qa058-artifacts/live-only-gate-report.json")


def main() -> int:
    root = Path.cwd()
    source_text = (
        root / "src/multi_agent_platform/api/routers/admin_react.py"
    ).read_text(encoding="utf-8")
    missed_routes = missed_static_route_targets(source_text)
    findings = scan_live_data_findings(repository_root=root, ci_mode=True)
    blockers = live_only_gate_blockers(repository_root=root)
    built_asset_blockers = [
        finding for finding in blockers if finding.reachability.value == "built_asset"
    ]
    dashboard = build_live_data_inventory_dashboard(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_platform_principal(),
        repository_root=root,
        ci_mode=True,
    )

    if blockers:
        raise RuntimeError(f"Expected 0 blocking findings, found {len(blockers)}")
    if missed_routes:
        raise RuntimeError(f"Expected 0 missed static routes, found {missed_routes}")
    if dashboard.summary.blocking_findings != 0:
        raise RuntimeError("Dashboard summary reported blocking findings")
    if dashboard.summary.route_targets != len(live_data_route_targets()):
        raise RuntimeError("Dashboard route target count is out of sync")

    status_counts = Counter(finding.status.value for finding in findings)
    reachability_counts = Counter(finding.reachability.value for finding in findings)
    probe_count = len(route_probe_expectations())
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(
            {
                "spec": "qa058",
                "ci_status": dashboard.summary.ci_status.value,
                "blocking_findings": len(blockers),
                "mapped_legacy_findings": status_counts.get("mapped_legacy", 0),
                "allowed_computed_metadata": status_counts.get(
                    "allowed_computed_metadata",
                    0,
                ),
                "route_targets": len(live_data_route_targets()),
                "route_probe_expectations": probe_count,
                "missed_static_routes": list(missed_routes),
                "built_asset_blockers": len(built_asset_blockers),
                "reachability_counts": dict(reachability_counts),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Verified QA058 live-only gate")
    print(f"ci_status={dashboard.summary.ci_status.value}")
    print(f"blocking_findings={len(blockers)}")
    print(f"mapped_legacy_findings={status_counts.get('mapped_legacy', 0)}")
    print(
        f"allowed_computed_metadata={status_counts.get('allowed_computed_metadata', 0)}"
    )
    print(f"route_targets={len(live_data_route_targets())}")
    print(f"route_probe_expectations={probe_count}")
    print(f"missed_static_routes={len(missed_routes)}")
    print(f"built_asset_blockers={len(built_asset_blockers)}")
    print(f"evidence_path={ARTIFACT_PATH.as_posix()}")
    return 0


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=None,
        org_id="platform",
        role_codes=("platform_admin",),
        permission_codes=("platform:admin", "tenant:read", "tenant:admin"),
        trace_id="trace-qa058-live-only-gate",
    )


if __name__ == "__main__":
    raise SystemExit(main())
