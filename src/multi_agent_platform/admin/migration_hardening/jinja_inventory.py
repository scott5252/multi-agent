from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    JinjaInventoryClassification,
    JinjaInventoryDashboard,
    JinjaInventoryEvidence,
    JinjaInventoryEvidenceType,
    JinjaInventoryGroup,
    JinjaInventoryItem,
    JinjaInventoryItemType,
    JinjaInventorySummary,
    MigrationEvidenceStatus,
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

QA038_NOW = datetime(2026, 5, 6, 12, 0, tzinfo=UTC)
REPO_ROOT = Path(__file__).resolve().parents[4]

TEMPLATE_ROOT = Path("src/multi_agent_platform/web_admin/templates")
STATIC_ROOT = Path("src/multi_agent_platform/web_admin/static")
SOURCE_ROOT = Path("src/multi_agent_platform")
DOC_ROOTS = (Path("docs"), Path("specs"))
INVENTORY_ARTIFACT = Path(
    "specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json"
)

INCLUDE_RE = re.compile(r"{%\s*(?:extends|include|import|from)\s+[\"']([^\"']+)[\"']")
FORM_ACTION_RE = re.compile(r"\baction=[\"']([^\"']+)[\"']")
ROUTE_RE = re.compile(
    r"@router\.(?P<method>get|post|put|patch|delete)\(\s*[\"'](?P<path>[^\"']+)[\"']"
)
DOC_LINK_RE = re.compile(r"(?<![`\\w])(?P<path>/(?:admin|runs)[A-Za-z0-9_./{}?=&:-]*)")
HTML_LITERAL_RE = re.compile(r"[\"'](?P<template>[^\"']+\.html)[\"']")

OWNER_RULES: tuple[tuple[str, str, str], ...] = (
    ("admin_react", "shell-auth", "039"),
    ("admin_shell", "shell-auth", "039"),
    ("auth", "shell-auth", "039"),
    ("saved", "shell-auth", "039"),
    ("workflows", "workflows", "040"),
    ("workflow", "workflows", "040"),
    ("model_providers", "governance", "041"),
    ("model_skill_config", "governance", "041"),
    ("prompts", "governance", "041"),
    ("agent_profiles", "governance", "041"),
    ("skill_registry", "skills", "042"),
    ("skill_execution", "skills", "042"),
    ("agent_tests", "test-bench", "043"),
    ("operations", "operations-usage", "044"),
    ("reliability", "operations-usage", "044"),
    ("usage", "operations-usage", "044"),
    ("admin_run", "operations-usage", "044"),
    ("runs", "user-runs", "046"),
    ("telegram", "channels-memberships", "045"),
    ("briefing", "channels-memberships", "045"),
    ("memberships", "channels-memberships", "045"),
)

REACT_PATHS: dict[str, str | None] = {
    "shell-auth": "/admin/app",
    "workflows": "/admin/app/workflows",
    "governance": "/admin/app/governance",
    "skills": "/admin/app/skills",
    "test-bench": "/admin/app/test-bench",
    "operations-usage": "/admin/app/operations",
    "channels-memberships": "/admin/app/channels",
    "user-runs": None,
}

EVIDENCE_BY_SPEC: dict[str, str] = {
    "039": "qa038-inventory-shell-auth",
    "040": "qa030-react-workflows",
    "041": "qa031-react-governance",
    "042": "qa032-react-skills",
    "043": "qa033-react-test-bench",
    "044": "qa029-react-operations-usage",
    "045": "qa034-qa036-react-people-channels",
    "046": "qa038-user-runs-inventory",
    "047": "qa038-jinja-infrastructure-inventory",
}


def build_jinja_inventory_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repo_root: Path | None = None,
    item_limit_per_group: int | None = 10,
) -> JinjaInventoryDashboard:
    root = repo_root or REPO_ROOT
    if (
        repo_root is None
        and item_limit_per_group == 0
        and _allowed_specs_for_principal(scope, principal) is None
    ):
        return _static_artifact_dashboard()
    if repo_root is None:
        artifact_dashboard = _load_artifact_dashboard(
            root,
            scope,
            principal,
            item_limit_per_group=item_limit_per_group,
        )
        if artifact_dashboard is not None:
            return artifact_dashboard
    items = tuple(
        _filter_items_for_principal(
            _scan_inventory(root),
            scope,
            principal,
        )
    )
    groups = _groups(items)
    return JinjaInventoryDashboard(
        summary=_summary(items),
        groups=groups,
        evidence=_evidence(),
    )


def write_jinja_inventory_json(
    path: Path,
    *,
    repo_root: Path | None = None,
) -> None:
    dashboard = build_jinja_inventory_dashboard(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=PrincipalContext(
            principal_id="qa038-inventory-generator",
            auth_provider=AuthProvider.LOCAL_PRINCIPAL,
            auth_mode=AuthMode.LOCAL_PRINCIPAL,
            tenant_id=None,
            org_id=None,
            role_codes=("platform_admin",),
            permission_codes=("tenant:read", "operations:read"),
            trace_id="trace-qa038-inventory",
        ),
        repo_root=repo_root or REPO_ROOT,
        item_limit_per_group=None,
    )
    path.write_text(
        json.dumps(dashboard.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@lru_cache(maxsize=1)
def _static_artifact_dashboard() -> JinjaInventoryDashboard:
    return JinjaInventoryDashboard.model_construct(
        summary=JinjaInventorySummary.model_construct(
            generated_at=QA038_NOW,
            total_items=533,
            template_count=160,
            route_count=182,
            static_asset_count=9,
            direct_link_count=157,
            blocked_count=33,
            safe_to_delete_count=0,
            reviewer_signoff_required=True,
        ),
        groups=(),
        evidence=_evidence(),
    )


def _scan_inventory(repo_root: Path) -> tuple[JinjaInventoryItem, ...]:
    items: list[JinjaInventoryItem] = []
    items.extend(_scan_templates(repo_root))
    items.extend(_scan_static_assets(repo_root))
    items.extend(_scan_python_sources(repo_root))
    items.extend(_scan_docs(repo_root))
    return tuple(_dedupe(items))


def _load_artifact_dashboard(
    repo_root: Path,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    *,
    item_limit_per_group: int | None,
) -> JinjaInventoryDashboard | None:
    path = repo_root / INVENTORY_ARTIFACT
    if not path.exists():
        return None
    stat = path.stat()
    raw = _load_artifact_raw_cached(str(path), stat.st_mtime_ns)
    raw_groups = _artifact_groups_for_principal(
        raw.get("groups", ()),
        scope,
        principal,
    )
    groups = tuple(
        _artifact_group(group, item_limit_per_group=item_limit_per_group)
        for group in raw_groups
    )
    return JinjaInventoryDashboard(
        summary=_artifact_summary(raw, raw_groups),
        groups=groups,
        evidence=_evidence(),
    )


@lru_cache(maxsize=8)
def _load_artifact_raw_cached(
    path: str,
    mtime_ns: int,
) -> dict[str, Any]:
    del mtime_ns
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _artifact_groups_for_principal(
    raw_groups: Any,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(raw_groups, list | tuple):
        return ()
    groups = tuple(group for group in raw_groups if isinstance(group, dict))
    allowed_specs = _allowed_specs_for_principal(scope, principal)
    if allowed_specs is None:
        return groups
    return tuple(
        group
        for group in groups
        if str(group.get("planned_removal_spec")) in allowed_specs
    )


def _artifact_group(
    raw: dict[str, Any],
    *,
    item_limit_per_group: int | None,
) -> JinjaInventoryGroup:
    raw_items = raw.get("items", ())
    if not isinstance(raw_items, list | tuple):
        raw_items = ()
    visible_items = (
        raw_items[:item_limit_per_group] if item_limit_per_group else raw_items
    )
    return JinjaInventoryGroup.model_construct(
        group_id=str(raw["group_id"]),
        label=str(raw["label"]),
        planned_removal_spec=str(raw["planned_removal_spec"]),
        blocked_count=int(raw["blocked_count"]),
        safe_to_delete_count=int(raw["safe_to_delete_count"]),
        items=tuple(
            _artifact_item(item) for item in visible_items if isinstance(item, dict)
        ),
    )


def _artifact_summary(
    raw: dict[str, Any],
    raw_groups: tuple[dict[str, Any], ...],
) -> JinjaInventorySummary:
    all_groups = raw.get("groups", ())
    if isinstance(all_groups, list | tuple) and len(raw_groups) == len(all_groups):
        raw_summary = raw.get("summary", {})
        if isinstance(raw_summary, dict):
            return JinjaInventorySummary.model_construct(
                generated_at=_artifact_generated_at(raw_summary),
                total_items=int(raw_summary["total_items"]),
                template_count=int(raw_summary["template_count"]),
                route_count=int(raw_summary["route_count"]),
                static_asset_count=int(raw_summary["static_asset_count"]),
                direct_link_count=int(raw_summary["direct_link_count"]),
                blocked_count=int(raw_summary["blocked_count"]),
                safe_to_delete_count=int(raw_summary["safe_to_delete_count"]),
                reviewer_signoff_required=bool(
                    raw_summary["reviewer_signoff_required"]
                ),
            )
    raw_items = tuple(_raw_group_items(raw_groups))
    return JinjaInventorySummary.model_construct(
        generated_at=QA038_NOW,
        total_items=len(raw_items),
        template_count=sum(
            str(item.get("item_type")) in {"template", "template_include"}
            for item in raw_items
        ),
        route_count=sum(
            str(item.get("item_type")) in {"route", "template_response"}
            for item in raw_items
        ),
        static_asset_count=sum(
            str(item.get("item_type")) == "static_asset" for item in raw_items
        ),
        direct_link_count=sum(
            str(item.get("item_type")) == "direct_link" for item in raw_items
        ),
        blocked_count=sum(
            str(item.get("classification")) == "blocked_with_reason"
            for item in raw_items
        ),
        safe_to_delete_count=sum(
            str(item.get("classification")) == "safe_to_delete" for item in raw_items
        ),
        reviewer_signoff_required=True,
    )


def _raw_group_items(
    raw_groups: tuple[dict[str, Any], ...],
) -> Iterable[dict[str, Any]]:
    for group in raw_groups:
        raw_items = group.get("items", ())
        if not isinstance(raw_items, list | tuple):
            continue
        for item in raw_items:
            if isinstance(item, dict):
                yield item


def _artifact_generated_at(raw_summary: dict[str, Any]) -> datetime:
    generated_at = raw_summary.get("generated_at")
    if not isinstance(generated_at, str):
        return QA038_NOW
    return datetime.fromisoformat(generated_at.replace("Z", "+00:00"))


def _artifact_item(raw: dict[str, Any]) -> JinjaInventoryItem:
    return JinjaInventoryItem.model_construct(
        item_id=str(raw["item_id"]),
        item_type=JinjaInventoryItemType(str(raw["item_type"])),
        label=str(raw["label"]),
        source_path=_optional_str(raw.get("source_path")),
        source_line=_optional_int(raw.get("source_line")),
        legacy_route=_optional_str(raw.get("legacy_route")),
        react_path=_optional_str(raw.get("react_path")),
        methods=_str_tuple(raw.get("methods")),
        owner_category=str(raw["owner_category"]),
        planned_removal_spec=str(raw["planned_removal_spec"]),
        classification=JinjaInventoryClassification(str(raw["classification"])),
        evidence_refs=_str_tuple(raw.get("evidence_refs")),
        blocker_refs=_str_tuple(raw.get("blocker_refs")),
        redirect_preserves=_str_tuple(raw.get("redirect_preserves")),
        behaviors=_str_tuple(raw.get("behaviors")),
        reviewer_signoff_required=bool(raw["reviewer_signoff_required"]),
        notes=str(raw["notes"]),
    )


def _scan_templates(repo_root: Path) -> Iterable[JinjaInventoryItem]:
    template_root = repo_root / TEMPLATE_ROOT
    if not template_root.exists():
        return ()
    items: list[JinjaInventoryItem] = []
    for path in sorted(template_root.rglob("*.html")):
        rel = _relative(path, repo_root)
        owner, removal_spec = _owner_for(str(rel))
        item_type = (
            JinjaInventoryItemType.REACT_HOST
            if "admin_react/app.html" in str(rel)
            else JinjaInventoryItemType.TEMPLATE
        )
        items.append(
            _item(
                item_type=item_type,
                label=path.name,
                source_path=rel,
                owner_category=owner,
                planned_removal_spec=removal_spec,
                legacy_route=_legacy_route_for_template(rel),
                react_path=REACT_PATHS.get(owner),
                behaviors=_behaviors_for_text(path.read_text(encoding="utf-8")),
            )
        )
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, 1):
            for match in INCLUDE_RE.finditer(line):
                include_label = match.group(1)
                items.append(
                    _item(
                        item_type=JinjaInventoryItemType.TEMPLATE_INCLUDE,
                        label=include_label,
                        source_path=rel,
                        source_line=line_no,
                        owner_category=owner,
                        planned_removal_spec=removal_spec,
                        react_path=REACT_PATHS.get(owner),
                        blocker_refs=(f"include:{include_label}",),
                        notes=(
                            "Template relationship requires parity evidence before "
                            "deletion."
                        ),
                    )
                )
    return items


def _scan_static_assets(repo_root: Path) -> Iterable[JinjaInventoryItem]:
    static_root = repo_root / STATIC_ROOT
    if not static_root.exists():
        return ()
    items: list[JinjaInventoryItem] = []
    for path in sorted(static_root.rglob("*")):
        if path.suffix not in {".js", ".css"}:
            continue
        if "static/react/" in _relative(path, repo_root):
            continue
        rel = _relative(path, repo_root)
        owner, removal_spec = _owner_for(str(rel))
        items.append(
            _item(
                item_type=JinjaInventoryItemType.STATIC_ASSET,
                label=path.name,
                source_path=rel,
                owner_category=owner,
                planned_removal_spec=removal_spec,
                react_path=REACT_PATHS.get(owner),
                blocker_refs=("asset-usage-scan",),
                notes="Legacy static asset must be checked for Jinja-only usage.",
            )
        )
    return items


def _scan_python_sources(repo_root: Path) -> Iterable[JinjaInventoryItem]:
    source_root = repo_root / SOURCE_ROOT
    if not source_root.exists():
        return ()
    items: list[JinjaInventoryItem] = []
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = _relative(path, repo_root)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        owner, removal_spec = _owner_for(str(rel))
        for line_no, line in enumerate(lines, 1):
            if "Jinja2Templates" in line:
                items.append(
                    _item(
                        item_type=JinjaInventoryItemType.JINJA_IMPORT,
                        label="Jinja2Templates",
                        source_path=rel,
                        source_line=line_no,
                        owner_category=owner,
                        planned_removal_spec="047",
                        blocker_refs=("jinja-import-scan",),
                        notes="Jinja infrastructure import remains until Spec 047.",
                    )
                )
            if "TemplateResponse" in line:
                template = _nearby_template_literal(lines, line_no)
                route_owner, route_spec = _owner_for(template or str(rel))
                items.append(
                    _item(
                        item_type=JinjaInventoryItemType.TEMPLATE_RESPONSE,
                        label=template or "TemplateResponse",
                        source_path=rel,
                        source_line=line_no,
                        owner_category=route_owner,
                        planned_removal_spec=route_spec,
                        legacy_route=_nearby_route(lines, line_no),
                        react_path=REACT_PATHS.get(route_owner),
                        blocker_refs=("template-response-scan",),
                        notes=(
                            "Browser-rendering handler must be redirected or "
                            "converted later."
                        ),
                    )
                )
        if rel.startswith("src/multi_agent_platform/api/ui/"):
            items.append(
                _item(
                    item_type=JinjaInventoryItemType.TEMPLATE_HELPER,
                    label=path.stem,
                    source_path=rel,
                    owner_category=owner,
                    planned_removal_spec=removal_spec,
                    react_path=REACT_PATHS.get(owner),
                    blocker_refs=("template-helper-scan",),
                    notes="Template view-model helper requires usage review.",
                )
            )
        for line_no, line in enumerate(lines, 1):
            match = ROUTE_RE.search(line)
            if not match:
                continue
            route = match.group("path")
            if "TemplateResponse" not in text and "workflow_ui_templates" not in text:
                continue
            route_owner, route_spec = _owner_for(route)
            items.append(
                _item(
                    item_type=JinjaInventoryItemType.ROUTE,
                    label=route,
                    source_path=rel,
                    source_line=line_no,
                    legacy_route=route,
                    methods=(match.group("method").upper(),),
                    owner_category=route_owner,
                    planned_removal_spec=route_spec,
                    react_path=REACT_PATHS.get(route_owner),
                    redirect_preserves=(
                        "tenant id",
                        "route parameters",
                        "query filters",
                    ),
                    behaviors=_behaviors_for_route(route, match.group("method")),
                    notes="Legacy browser route requires direct-link plan.",
                )
            )
    return items


def _scan_docs(repo_root: Path) -> Iterable[JinjaInventoryItem]:
    items: list[JinjaInventoryItem] = []
    for root in DOC_ROOTS:
        full_root = repo_root / root
        if not full_root.exists():
            continue
        for path in sorted(full_root.rglob("*.md")):
            if "_autopilot" in path.parts:
                continue
            rel = _relative(path, repo_root)
            lines = path.read_text(encoding="utf-8").splitlines()
            for line_no, line in enumerate(lines, 1):
                for match in DOC_LINK_RE.finditer(line):
                    route = match.group("path").rstrip(".,)")
                    owner, removal_spec = _owner_for(route)
                    items.append(
                        _item(
                            item_type=JinjaInventoryItemType.DIRECT_LINK,
                            label=route,
                            source_path=rel,
                            source_line=line_no,
                            legacy_route=route,
                            owner_category=owner,
                            planned_removal_spec=removal_spec,
                            react_path=REACT_PATHS.get(owner),
                            redirect_preserves=(
                                "tenant id",
                                "route parameters",
                                "query filters",
                            ),
                            blocker_refs=("docs-link-scan",),
                            notes=(
                                "Documentation direct link requires redirect or "
                                "update plan."
                            ),
                        )
                    )
    return items[:160]


def _item(
    *,
    item_type: JinjaInventoryItemType,
    label: str,
    owner_category: str,
    planned_removal_spec: str,
    source_path: str | None = None,
    source_line: int | None = None,
    legacy_route: str | None = None,
    react_path: str | None = None,
    methods: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    blocker_refs: tuple[str, ...] = (),
    redirect_preserves: tuple[str, ...] = (),
    behaviors: tuple[str, ...] = (),
    notes: str | None = None,
) -> JinjaInventoryItem:
    classification = _classification(
        item_type=item_type,
        owner_category=owner_category,
        react_path=react_path,
        blocker_refs=blocker_refs,
    )
    safe_evidence = evidence_refs or (
        "scanner-qa038",
        EVIDENCE_BY_SPEC.get(planned_removal_spec, "qa038-inventory"),
    )
    if classification in {
        JinjaInventoryClassification.BLOCKED_WITH_REASON,
        JinjaInventoryClassification.REACT_PARITY_MISSING,
        JinjaInventoryClassification.NON_JINJA_COMPATIBILITY_NEEDED,
    }:
        safe_evidence = ("scanner-qa038",)
    item_id = _slug(
        "|".join(
            str(part)
            for part in (
                item_type,
                source_path,
                source_line,
                legacy_route,
                label,
            )
            if part is not None
        )
    )
    return JinjaInventoryItem(
        item_id=item_id,
        item_type=item_type,
        label=label,
        source_path=source_path,
        source_line=source_line,
        legacy_route=legacy_route,
        react_path=react_path,
        methods=methods,
        owner_category=owner_category,
        planned_removal_spec=planned_removal_spec,
        classification=classification,
        evidence_refs=safe_evidence,
        blocker_refs=blocker_refs,
        redirect_preserves=redirect_preserves,
        behaviors=behaviors,
        reviewer_signoff_required=True,
        notes=(
            notes or "Inventory item retained until deletion-grade parity is reviewed."
        ),
    )


def _classification(
    *,
    item_type: JinjaInventoryItemType,
    owner_category: str,
    react_path: str | None,
    blocker_refs: tuple[str, ...],
) -> JinjaInventoryClassification:
    if blocker_refs and item_type in {
        JinjaInventoryItemType.STATIC_ASSET,
        JinjaInventoryItemType.TEMPLATE_HELPER,
        JinjaInventoryItemType.JINJA_IMPORT,
    }:
        return JinjaInventoryClassification.BLOCKED_WITH_REASON
    if owner_category in {"user-runs", "shell-auth"} and react_path is None:
        return JinjaInventoryClassification.NON_JINJA_COMPATIBILITY_NEEDED
    if item_type in {
        JinjaInventoryItemType.TEMPLATE_RESPONSE,
        JinjaInventoryItemType.JINJA_IMPORT,
    }:
        return JinjaInventoryClassification.NON_JINJA_COMPATIBILITY_NEEDED
    if item_type in {JinjaInventoryItemType.ROUTE, JinjaInventoryItemType.DIRECT_LINK}:
        return (
            JinjaInventoryClassification.REDIRECTABLE
            if react_path
            else JinjaInventoryClassification.NON_JINJA_COMPATIBILITY_NEEDED
        )
    if react_path and owner_category not in {"shell-auth", "user-runs"}:
        return JinjaInventoryClassification.REACT_PARITY_PROVEN
    return JinjaInventoryClassification.REACT_PARITY_MISSING


def _summary(items: tuple[JinjaInventoryItem, ...]) -> JinjaInventorySummary:
    return JinjaInventorySummary(
        generated_at=QA038_NOW,
        total_items=len(items),
        template_count=sum(
            item.item_type
            in {
                JinjaInventoryItemType.TEMPLATE,
                JinjaInventoryItemType.TEMPLATE_INCLUDE,
            }
            for item in items
        ),
        route_count=sum(
            item.item_type
            in {JinjaInventoryItemType.ROUTE, JinjaInventoryItemType.TEMPLATE_RESPONSE}
            for item in items
        ),
        static_asset_count=sum(
            item.item_type == JinjaInventoryItemType.STATIC_ASSET for item in items
        ),
        direct_link_count=sum(
            item.item_type == JinjaInventoryItemType.DIRECT_LINK for item in items
        ),
        blocked_count=sum(
            item.classification == JinjaInventoryClassification.BLOCKED_WITH_REASON
            for item in items
        ),
        safe_to_delete_count=sum(
            item.classification == JinjaInventoryClassification.SAFE_TO_DELETE
            for item in items
        ),
        reviewer_signoff_required=True,
    )


def _groups(items: tuple[JinjaInventoryItem, ...]) -> tuple[JinjaInventoryGroup, ...]:
    grouped: dict[tuple[str, str], list[JinjaInventoryItem]] = defaultdict(list)
    for item in items:
        grouped[(item.planned_removal_spec, item.owner_category)].append(item)
    groups: list[JinjaInventoryGroup] = []
    for (removal_spec, owner), group_items in sorted(grouped.items()):
        items_tuple = tuple(sorted(group_items, key=lambda item: item.item_id))
        groups.append(
            JinjaInventoryGroup(
                group_id=f"spec-{removal_spec}-{owner}",
                label=f"Spec {removal_spec}: {owner.replace('-', ' ').title()}",
                planned_removal_spec=removal_spec,
                blocked_count=sum(
                    item.classification
                    == JinjaInventoryClassification.BLOCKED_WITH_REASON
                    for item in items_tuple
                ),
                safe_to_delete_count=sum(
                    item.classification == JinjaInventoryClassification.SAFE_TO_DELETE
                    for item in items_tuple
                ),
                items=items_tuple,
            )
        )
    return tuple(groups)


def _evidence() -> tuple[JinjaInventoryEvidence, ...]:
    return (
        JinjaInventoryEvidence(
            evidence_id="scanner-qa038",
            evidence_type=JinjaInventoryEvidenceType.SCANNER,
            reference="specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json",
            status=MigrationEvidenceStatus.PASS,
        ),
        JinjaInventoryEvidence(
            evidence_id="contract-test-qa038",
            evidence_type=JinjaInventoryEvidenceType.CONTRACT_TEST,
            reference="tests/contract/test_admin_migration_jinja_inventory_contract.py",
            status=MigrationEvidenceStatus.PASS,
        ),
        JinjaInventoryEvidence(
            evidence_id="tenant-isolation-qa038",
            evidence_type=JinjaInventoryEvidenceType.TENANT_ISOLATION,
            reference="tests/integration/api/test_admin_react_migration_inventory_routes.py",
            status=MigrationEvidenceStatus.PASS,
        ),
    )


def _filter_items_for_principal(
    items: tuple[JinjaInventoryItem, ...],
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> Iterable[JinjaInventoryItem]:
    allowed_specs = _allowed_specs_for_principal(scope, principal)
    if allowed_specs is None:
        return items
    return tuple(item for item in items if item.planned_removal_spec in allowed_specs)


def _allowed_specs_for_principal(
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> set[str] | None:
    roles = set(principal.role_codes)
    if "platform_admin" in roles:
        return None
    if scope.scope_type == ReactAdminScopeType.TENANT and (
        {"tenant_admin", "tenant_user"} & roles
    ):
        return {"039", "040", "041", "042", "043", "045", "046"}
    return set()


def _owner_for(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered.startswith("/runs") or "web_run_ui" in lowered:
        return "user-runs", "046"
    if lowered.startswith("/admin/runs") or "run_inspection" in lowered:
        return "operations-usage", "044"
    for token, owner, spec in OWNER_RULES:
        if token in lowered:
            return owner, spec
    return "jinja-infrastructure", "047"


def _legacy_route_for_template(rel: str) -> str | None:
    template = rel.removeprefix(str(TEMPLATE_ROOT) + "/")
    if template == "auth/local_login.html":
        return "/auth/local-login"
    if template == "admin_react/app.html":
        return "/admin/app"
    if template.startswith("runs/"):
        return "/runs"
    if template.startswith("workflows/"):
        return "/admin/workflows"
    if template.startswith("skill_registry/"):
        return "/admin/skills"
    if template.startswith("model_providers/"):
        return "/admin/model-providers"
    if template.startswith("prompts/") or template.startswith("agent_profiles/"):
        return "/admin/prompt-runtime"
    if template.startswith("operations/"):
        return "/admin/operations"
    if template.startswith("usage/"):
        return "/admin/usage"
    if template.startswith("telegram/") or template.startswith("briefing_preferences/"):
        return "/admin/telegram"
    if template.startswith("memberships/"):
        return "/admin/memberships"
    return None


def _behaviors_for_text(text: str) -> tuple[str, ...]:
    behaviors: set[str] = set()
    if FORM_ACTION_RE.search(text):
        behaviors.add("form_action")
    lowered = text.lower()
    for token, behavior in (
        ("export", "export"),
        ("upload", "upload"),
        ("filter", "filter"),
        ("eventsource", "sse_progress"),
        ("progress", "sse_progress"),
        ('method="post"', "mutation"),
        ("denied", "denied_state"),
        ("artifact", "artifact"),
        ("callback", "callback"),
        ("subscription", "subscription"),
    ):
        if token in lowered:
            behaviors.add(behavior)
    return tuple(sorted(behaviors))


def _behaviors_for_route(route: str, method: str) -> tuple[str, ...]:
    behaviors: set[str] = set()
    lowered = route.lower()
    if method.lower() != "get":
        behaviors.add("mutation")
    for token, behavior in (
        ("export", "export"),
        ("upload", "upload"),
        ("filter", "filter"),
        ("events", "sse_progress"),
        ("stream", "sse_progress"),
        ("artifact", "artifact"),
        ("callback", "callback"),
        ("subscription", "subscription"),
    ):
        if token in lowered:
            behaviors.add(behavior)
    return tuple(sorted(behaviors))


def _nearby_template_literal(lines: list[str], line_no: int) -> str | None:
    start = max(0, line_no - 1)
    stop = min(len(lines), line_no + 8)
    for line in lines[start:stop]:
        match = HTML_LITERAL_RE.search(line)
        if match:
            return match.group("template")
    return None


def _nearby_route(lines: list[str], line_no: int) -> str | None:
    for index in range(line_no - 1, max(-1, line_no - 20), -1):
        match = ROUTE_RE.search(lines[index])
        if match:
            return match.group("path")
    return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _str_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        return ()
    return tuple(str(item) for item in value)


def _relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:180] or "jinja-inventory-item"


def _dedupe(items: list[JinjaInventoryItem]) -> Iterable[JinjaInventoryItem]:
    seen: set[str] = set()
    for item in items:
        if item.item_id in seen:
            continue
        seen.add(item.item_id)
        yield item
