from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from multi_agent_platform.admin.migration_hardening import (
    build_transitional_label_gate,
    scan_transitional_label_findings,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    TransitionalLabelClassification,
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

ARTIFACT_PATH = Path(".data/qa059-artifacts/transitional-label-gate-report.json")
SCREENSHOT_DIR = Path("output/playwright/qa059_ui")


def main() -> int:
    root = Path.cwd()
    findings = scan_transitional_label_findings(repository_root=root, ci_mode=True)
    blockers = [
        finding
        for finding in findings
        if finding.classification
        == TransitionalLabelClassification.BLOCKING_TRANSITIONAL_LABEL
    ]
    gate = build_transitional_label_gate(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_platform_principal(),
        repository_root=root,
        ci_mode=True,
    )
    screenshots = sorted(path.as_posix() for path in SCREENSHOT_DIR.glob("*.png"))

    if blockers:
        raise RuntimeError(f"Expected 0 blocked labels, found {len(blockers)}")
    if gate.summary.blocked_count != 0:
        raise RuntimeError("Transitional label gate reported blockers")
    if "React Admin" in gate.model_dump_json():
        raise RuntimeError("Gate report exposed blocked React Admin product label")

    classification_counts = Counter(
        finding.classification.value for finding in findings
    )
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(
        json.dumps(
            {
                "spec": "qa059",
                "ci_status": gate.summary.ci_status.value,
                "blocked_count": gate.summary.blocked_count,
                "allowed_reference_count": gate.summary.allowed_reference_count,
                "surfaces_scanned": gate.summary.surfaces_scanned,
                "routes_scanned": gate.summary.routes_scanned,
                "screenshots_checked": len(screenshots),
                "screenshot_paths": screenshots,
                "classification_counts": dict(classification_counts),
                "evidence": [
                    evidence.model_dump(mode="json") for evidence in gate.evidence
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Verified QA059 transitional label gate")
    print(f"ci_status={gate.summary.ci_status.value}")
    print(f"blocked_count={gate.summary.blocked_count}")
    print(f"allowed_reference_count={gate.summary.allowed_reference_count}")
    print(f"surfaces_scanned={gate.summary.surfaces_scanned}")
    print(f"routes_scanned={gate.summary.routes_scanned}")
    print(f"screenshots_checked={len(screenshots)}")
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
        trace_id="trace-qa059-transitional-label-gate",
    )


if __name__ == "__main__":
    raise SystemExit(main())
