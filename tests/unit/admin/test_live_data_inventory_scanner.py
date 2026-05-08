from __future__ import annotations

from pathlib import Path

import pytest

from multi_agent_platform.admin.migration_hardening import (
    computed_metadata_allowlist,
    count_test_only_markers,
    current_mapped_surface_paths,
    live_data_route_targets,
    missed_static_route_targets,
    route_probe_expectations,
    scan_live_data_findings,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    LiveDataInventorySeverity,
    LiveDataInventoryStatus,
    LiveDataMarkerKind,
    LiveDataReachability,
)


def test_current_inventory_maps_all_roadmap_surfaces() -> None:
    findings = scan_live_data_findings()

    assert findings
    assert not [
        finding
        for finding in findings
        if finding.status == LiveDataInventoryStatus.NEW_REGRESSION
    ]
    replacement_specs = {
        finding.replacement_spec
        for finding in findings
        if finding.status == LiveDataInventoryStatus.MAPPED_LEGACY
    }
    assert replacement_specs == set()
    assert "057" not in replacement_specs
    assert "056" not in replacement_specs
    assert "055" not in replacement_specs
    assert "054" not in replacement_specs
    assert "053" not in replacement_specs
    assert "052" not in replacement_specs
    route_specs = {target.replacement_spec for target in live_data_route_targets()}
    assert "052" in route_specs
    assert "051" in route_specs
    assert "050" in route_specs
    mapped_paths = current_mapped_surface_paths()
    assert "frontend/admin/src/components/patterns" not in mapped_paths
    assert "src/multi_agent_platform/admin/workflow_builder.py" not in mapped_paths
    assert "frontend/admin/src/components/workflows" not in mapped_paths
    assert (
        "src/multi_agent_platform/testing/agent_bench/react_test_bench.py"
        not in mapped_paths
    )
    assert "frontend/admin/src/components/testBench" not in mapped_paths
    assert (
        "src/multi_agent_platform/admin/memberships/react_memberships.py"
        not in mapped_paths
    )
    assert "frontend/admin/src/components/memberships" not in mapped_paths
    assert "src/multi_agent_platform/admin/skill_lifecycle.py" not in mapped_paths
    assert "frontend/admin/src/components/skills" not in mapped_paths
    assert "src/multi_agent_platform/admin/governance.py" not in mapped_paths
    assert "frontend/admin/src/components/governance" not in mapped_paths
    assert (
        "src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py"
        not in mapped_paths
    )
    assert "src/multi_agent_platform/admin/usage/react_usage.py" not in mapped_paths
    assert "frontend/admin/src/components/usage" not in mapped_paths
    assert "src/multi_agent_platform/operations/workbench.py" not in mapped_paths
    assert "frontend/admin/src/components/workbench" not in mapped_paths


def test_scanner_excludes_test_only_fixture_markers() -> None:
    findings = scan_live_data_findings()

    assert count_test_only_markers() > 0
    assert all(not finding.source_path.startswith("tests/") for finding in findings)
    assert all(
        not finding.source_path.startswith("frontend/admin/src/test/")
        for finding in findings
    )


def test_synthetic_unmapped_production_marker_is_blocking(
    tmp_path: Path,
) -> None:
    source = tmp_path / "frontend/admin/src/components/new/Foo.tsx"
    source.parent.mkdir(parents=True)
    source.write_text('export const marker = "qa048";\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.status == LiveDataInventoryStatus.NEW_REGRESSION
    assert finding.severity == LiveDataInventorySeverity.BLOCKING
    assert finding.source_path == "frontend/admin/src/components/new/Foo.tsx"
    assert "/Users/" not in finding.model_dump_json()


def test_scanner_deduplicates_markers_and_flags_fixture_imports(
    tmp_path: Path,
) -> None:
    empty_route = tmp_path / "src/multi_agent_platform/api/routers/admin_react.py"
    empty_route.parent.mkdir(parents=True)
    empty_route.write_text("", encoding="utf-8")
    source = tmp_path / "frontend/admin/src/components/new/Foo.tsx"
    source.parent.mkdir(parents=True)
    source.write_text(
        "\n".join(
            (
                'export const marker = "qa048 qa048";',
                'export const runId = "run-qa048-live";',
                "from tests.fixtures import sample",
            )
        ),
        encoding="utf-8",
    )

    findings = [
        finding
        for finding in scan_live_data_findings(repository_root=tmp_path)
        if finding.source_path == "frontend/admin/src/components/new/Foo.tsx"
    ]

    assert [
        finding.marker_kind
        for finding in findings
        if finding.marker_kind == LiveDataMarkerKind.QA_MARKER
    ] == [LiveDataMarkerKind.QA_MARKER]
    assert {finding.marker_kind for finding in findings} >= {
        LiveDataMarkerKind.QA_MARKER,
        LiveDataMarkerKind.FAKE_RUN_ID,
        LiveDataMarkerKind.TEST_FIXTURE_IMPORT,
    }


def test_computed_metadata_allowlist_is_narrow_and_sourced() -> None:
    allowlist = computed_metadata_allowlist()

    assert allowlist
    assert all(entry.scope not in {"src", "frontend"} for entry in allowlist)
    assert all(entry.reason and entry.derivation_source for entry in allowlist)


def test_route_target_registry_covers_static_admin_react_json_routes() -> None:
    source = Path("src/multi_agent_platform/api/routers/admin_react.py").read_text(
        encoding="utf-8",
    )

    assert missed_static_route_targets(source) == ()
    target_paths = {target.path for target in live_data_route_targets()}
    assert "/admin/app/patterns.json" not in target_paths
    assert "/admin/app/patterns/actions/sample" not in target_paths
    assert "/admin/app/patterns/export" not in target_paths
    assert "/admin/app/migration/live-data-inventory.json" in target_paths
    assert "/admin/app/workflows/builder.json" in target_paths
    assert "/admin/app/operations.json" in target_paths


def test_route_probe_expectations_cover_empty_and_seeded_targets() -> None:
    targets = live_data_route_targets()
    probes = route_probe_expectations()

    expected = sum(target.empty_state_required for target in targets) + sum(
        target.seeded_state_required for target in targets
    )
    assert len(probes) == expected
    assert {probe.state for probe in probes} == {"empty", "seeded"}
    assert all(probe.path.startswith("/admin/app") for probe in probes)


def test_generated_contract_marker_is_blocking_after_spec_049(
    tmp_path: Path,
) -> None:
    source = tmp_path / "frontend/admin/src/api/generated/reactAdminApi.ts"
    source.parent.mkdir(parents=True)
    source.write_text('export const stale = "qa049";\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 1
    assert (
        findings[0].source_path == "frontend/admin/src/api/generated/reactAdminApi.ts"
    )
    assert findings[0].status == LiveDataInventoryStatus.NEW_REGRESSION
    assert findings[0].severity == LiveDataInventorySeverity.BLOCKING


def test_membership_marker_is_blocking_after_spec_054(tmp_path: Path) -> None:
    source = (
        tmp_path / "src/multi_agent_platform/admin/memberships/react_memberships.py"
    )
    source.parent.mkdir(parents=True)
    source.write_text('FIXED_USER = "principal-qa034-maya"\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 1
    assert findings[0].source_path == (
        "src/multi_agent_platform/admin/memberships/react_memberships.py"
    )
    assert findings[0].status == LiveDataInventoryStatus.NEW_REGRESSION
    assert findings[0].severity == LiveDataInventorySeverity.BLOCKING


def test_channel_marker_is_blocking_after_spec_055(tmp_path: Path) -> None:
    source_path = (
        "src/multi_agent_platform/admin/channel_telegram_briefing/"
        "react_channel_telegram_briefing.py"
    )
    source = tmp_path / source_path
    source.parent.mkdir(parents=True)
    source.write_text('SAFE_RUN_ID = "qa036-run-morning-briefing"\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 1
    assert findings[0].source_path == source_path
    assert findings[0].status == LiveDataInventoryStatus.NEW_REGRESSION
    assert findings[0].severity == LiveDataInventorySeverity.BLOCKING


def test_usage_marker_is_blocking_after_spec_056(tmp_path: Path) -> None:
    source_path = "src/multi_agent_platform/admin/usage/react_usage.py"
    source = tmp_path / source_path
    source.parent.mkdir(parents=True)
    source.write_text('USAGE_EVENTS = ("qa035-fixed-usage",)\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 2
    assert {finding.marker_kind for finding in findings} == {
        LiveDataMarkerKind.FIXTURE_COLLECTION,
        LiveDataMarkerKind.QA_MARKER,
    }
    assert all(finding.source_path == source_path for finding in findings)
    assert all(
        finding.status == LiveDataInventoryStatus.NEW_REGRESSION for finding in findings
    )
    assert all(
        finding.severity == LiveDataInventorySeverity.BLOCKING for finding in findings
    )


def test_operations_marker_is_blocking_after_spec_057(tmp_path: Path) -> None:
    source_path = "src/multi_agent_platform/operations/workbench.py"
    source = tmp_path / source_path
    source.parent.mkdir(parents=True)
    source.write_text('RUN_DEBUG = "gateway-attempt-qa029"\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert findings
    assert {finding.marker_kind for finding in findings} == {
        LiveDataMarkerKind.QA_MARKER,
    }
    assert all(finding.source_path == source_path for finding in findings)
    assert all(
        finding.status == LiveDataInventoryStatus.NEW_REGRESSION for finding in findings
    )
    assert all(
        finding.severity == LiveDataInventorySeverity.BLOCKING for finding in findings
    )


def test_built_asset_markers_are_blocking_after_spec_058(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src/multi_agent_platform/web_admin/static/react/assets/main.js"
    source.parent.mkdir(parents=True)
    source.write_text('window.__asset = "qa058";\n', encoding="utf-8")

    findings = scan_live_data_findings(repository_root=tmp_path)

    assert len(findings) == 1
    assert findings[0].source_path.endswith("/assets/main.js")
    assert findings[0].status == LiveDataInventoryStatus.NEW_REGRESSION
    assert findings[0].severity == LiveDataInventorySeverity.BLOCKING
    assert findings[0].reachability == LiveDataReachability.BUILT_ASSET


def test_final_gate_blockers_reports_only_blocking_findings(tmp_path: Path) -> None:
    from multi_agent_platform.admin.migration_hardening import live_only_gate_blockers

    asset = tmp_path / "src/multi_agent_platform/web_admin/static/react/assets/main.js"
    asset.parent.mkdir(parents=True)
    asset.write_text('window.__asset = "qa058";\n', encoding="utf-8")

    blockers = live_only_gate_blockers(repository_root=tmp_path)

    assert len(blockers) == 1
    assert blockers[0].source_path.endswith("/assets/main.js")


def test_allowlist_rejects_unsafe_absolute_paths() -> None:
    from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
        LiveDataInventoryEvidence,
        LiveDataInventoryEvidenceType,
        MigrationEvidenceStatus,
    )

    with pytest.raises(ValueError, match="relative"):
        LiveDataInventoryEvidence(
            evidence_id="unsafe",
            evidence_type=LiveDataInventoryEvidenceType.SCANNER,
            reference="/tmp/unsafe",
            status=MigrationEvidenceStatus.PASS,
        )
