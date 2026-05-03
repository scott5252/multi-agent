from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, Literal, Self
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from multi_agent_platform.auth.policy import (
    SURFACE_POLICIES,
    SurfaceClassification,
)
from multi_agent_platform.auth.principal import PrincipalContext

AdminScopeValue = Literal["platform", "tenant"]
RequiredScopeValue = Literal["platform", "tenant", "either"]

ADMIN_ROLE_CODES = frozenset({"tenant_admin", "platform_admin", "auditor"})
SENSITIVE_TEXT_MARKERS = (
    "secret",
    "token",
    "password",
    "api_key",
    "authorization",
    "credential",
    "prompt",
    "memory",
    "payload",
    "traceback",
    "stack trace",
    "stacktrace",
)


class AdminConsoleAccessError(PermissionError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 403,
        reason_category: str = "denied",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.reason_category = reason_category


class CommonStateType(StrEnum):
    EMPTY = "empty"
    FILTERED_EMPTY = "filtered_empty"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"
    VALIDATION_ERROR = "validation_error"
    UNEXPECTED_ERROR = "unexpected_error"


class AdminScope(BaseModel):
    scope_type: AdminScopeValue
    tenant_id: UUID | None = None
    label: str | None = None

    @classmethod
    def platform(cls, *, label: str | None = None) -> AdminScope:
        return cls(scope_type="platform", label=label or "Platform")

    @classmethod
    def tenant(cls, tenant_id: UUID | None, *, label: str | None = None) -> AdminScope:
        if tenant_id is None:
            raise ValueError("tenant scope requires tenant_id")
        return cls(
            scope_type="tenant",
            tenant_id=tenant_id,
            label=label or f"Tenant {str(tenant_id)[:8]}",
        )

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if self.scope_type == "platform" and self.tenant_id is not None:
            raise ValueError("platform scope must omit tenant_id")
        if self.scope_type == "tenant" and self.tenant_id is None:
            raise ValueError("tenant scope requires tenant_id")
        if self.label is None:
            self.label = "Platform" if self.scope_type == "platform" else "Tenant"
        return self

    def query_params(self) -> dict[str, str]:
        if self.scope_type == "tenant" and self.tenant_id is not None:
            return {"tenant_id": str(self.tenant_id)}
        return {}


class AdminScopeOption(BaseModel):
    scope: AdminScope
    label: str
    href: str
    selected: bool = False


class BreadcrumbItem(BaseModel):
    label: str
    href: str | None = None
    active: bool = False


class PageAction(BaseModel):
    label: str
    href: str
    method: str = "GET"
    allowed: bool = True


class FlashMessage(BaseModel):
    level: Literal["success", "info", "warning", "error"] = "info"
    summary: str
    principal_id: str
    scope_type: AdminScopeValue
    tenant_id: UUID | None = None


class CommonState(BaseModel):
    state_type: CommonStateType
    title: str
    summary: str
    next_actions: tuple[PageAction, ...] = Field(default_factory=tuple)
    trace_id: str | None = None

    @property
    def is_blocking(self) -> bool:
        return self.state_type in {
            CommonStateType.DENIED,
            CommonStateType.NOT_FOUND,
            CommonStateType.UNAVAILABLE,
            CommonStateType.UNEXPECTED_ERROR,
            CommonStateType.VALIDATION_ERROR,
        }


class NavigationItem(BaseModel):
    item_id: str
    label: str
    group: str
    href: str
    route_surface_key: str
    required_scope: RequiredScopeValue = "either"
    admin_area: str | None = None
    preserve_tenant_scope: bool = True
    active_matchers: tuple[str, ...]
    order: int = 100
    filter_profile: str | None = None
    active: bool = False


class NavigationGroup(BaseModel):
    label: str
    items: tuple[NavigationItem, ...]


class NavigationOutcome(BaseModel):
    item_id: str
    route_surface_key: str
    outcome: Literal["allowed", "denied", "unavailable"]
    reason_category: str


class SavedFilterSummary(BaseModel):
    filter_id: UUID | str
    display_name: str
    admin_area: str
    filter_key: str
    safe_summary: dict[str, str]
    restore_href: str
    delete_href: str
    last_restored_at: str | None = None


class AdminShellContext(BaseModel):
    title: str
    active_scope: AdminScope
    available_scopes: tuple[AdminScopeOption, ...] = Field(default_factory=tuple)
    navigation_groups: tuple[NavigationGroup, ...] = Field(default_factory=tuple)
    breadcrumbs: tuple[BreadcrumbItem, ...] = Field(default_factory=tuple)
    page_actions: tuple[PageAction, ...] = Field(default_factory=tuple)
    messages: tuple[FlashMessage, ...] = Field(default_factory=tuple)
    common_state: CommonState | None = None
    saved_filters: tuple[SavedFilterSummary, ...] = Field(default_factory=tuple)
    filter_restore_outcome: str | None = None
    trace_id: str
    navigation_outcomes: tuple[NavigationOutcome, ...] = Field(default_factory=tuple)


class FilterProfile(BaseModel):
    admin_area: str
    filter_key: str
    destination_href: str
    allowed_criteria: tuple[str, ...]
    labels: dict[str, str]


class NormalizedFilterCriteria(BaseModel):
    admin_area: str
    filter_key: str
    criteria: dict[str, str | int | float | bool | list[str]]
    safe_summary: dict[str, str]


def is_admin_principal(principal: PrincipalContext) -> bool:
    return bool(set(principal.role_codes) & ADMIN_ROLE_CODES)


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def is_auditor(principal: PrincipalContext) -> bool:
    return "auditor" in principal.role_codes


def sanitize_text(
    value: object,
    *,
    fallback: str = "Protected detail",
    max_length: int = 180,
) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    lowered = text.lower()
    if any(marker in lowered for marker in SENSITIVE_TEXT_MARKERS):
        return fallback
    if len(text) > max_length:
        return f"{text[: max_length - 1].rstrip()}..."
    return text


def sanitize_breadcrumbs(
    breadcrumbs: Sequence[BreadcrumbItem],
) -> tuple[BreadcrumbItem, ...]:
    sanitized: list[BreadcrumbItem] = []
    for item in breadcrumbs:
        sanitized.append(
            item.model_copy(
                update={
                    "label": sanitize_text(item.label),
                    "href": item.href
                    if item.href and item.href.startswith("/")
                    else None,
                }
            )
        )
    if sanitized:
        sanitized[-1] = sanitized[-1].model_copy(update={"active": True})
    return tuple(sanitized)


def sanitize_flash_message(
    summary: object,
    *,
    scope: AdminScope,
    principal_id: str,
    level: Literal["success", "info", "warning", "error"] = "info",
) -> FlashMessage:
    return FlashMessage(
        level=level,
        summary=sanitize_text(
            summary,
            fallback="Action completed. Details were redacted.",
            max_length=220,
        ),
        principal_id=principal_id,
        scope_type=scope.scope_type,
        tenant_id=scope.tenant_id,
    )


def build_common_state(
    state_type: CommonStateType,
    *,
    title: object,
    summary: object,
    trace_id: str | None = None,
    next_actions: Sequence[PageAction] = (),
) -> CommonState:
    return CommonState(
        state_type=state_type,
        title=sanitize_text(title, max_length=90),
        summary=sanitize_text(summary, max_length=260),
        trace_id=trace_id,
        next_actions=tuple(action for action in next_actions if action.allowed),
    )


def safe_redirect_target(value: str | None, *, fallback: str = "/admin") -> str:
    if not value:
        return fallback
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return fallback
    if not parsed.path.startswith("/admin"):
        return fallback
    if parsed.path.startswith("//"):
        return fallback
    return urlunsplit(("", "", parsed.path, parsed.query, ""))


def with_scope_query(href: str, scope: AdminScope) -> str:
    parsed = urlsplit(href)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if scope.scope_type == "tenant" and scope.tenant_id is not None:
        query["tenant_id"] = str(scope.tenant_id)
    else:
        query.pop("tenant_id", None)
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


def resolve_admin_scope(
    principal: PrincipalContext,
    tenant_id: UUID | str | None,
) -> AdminScope:
    if not is_admin_principal(principal):
        raise AdminConsoleAccessError(
            "admin console requires tenant or platform administrator role",
            reason_category="insufficient_role",
        )

    if tenant_id in (None, ""):
        if principal.tenant_id is not None and "tenant_admin" in principal.role_codes:
            return AdminScope.tenant(principal.tenant_id)
        if is_platform_admin(principal) or is_auditor(principal):
            return AdminScope.platform()
        raise AdminConsoleAccessError(
            "no authorized admin scope is available",
            reason_category="missing_scope",
        )

    try:
        selected_tenant_id = (
            tenant_id if isinstance(tenant_id, UUID) else UUID(str(tenant_id))
        )
    except ValueError as exc:
        raise AdminConsoleAccessError(
            "tenant scope is invalid",
            reason_category="invalid_scope",
        ) from exc

    if is_platform_admin(principal):
        return AdminScope.tenant(selected_tenant_id)
    if (
        principal.tenant_id == selected_tenant_id
        and "tenant_admin" in principal.role_codes
    ):
        return AdminScope.tenant(selected_tenant_id)
    raise AdminConsoleAccessError(
        "tenant scope is not authorized",
        reason_category="cross_tenant_scope",
    )


def principal_can_use_scope(principal: PrincipalContext, scope: AdminScope) -> bool:
    if not is_admin_principal(principal):
        return False
    if scope.scope_type == "platform":
        return is_platform_admin(principal) or is_auditor(principal)
    if is_platform_admin(principal):
        return True
    return (
        principal.tenant_id == scope.tenant_id
        and "tenant_admin" in principal.role_codes
    )


def available_scope_options(
    *,
    principal: PrincipalContext,
    active_scope: AdminScope,
    current_path: str,
) -> tuple[AdminScopeOption, ...]:
    options: list[AdminScopeOption] = []
    if is_platform_admin(principal) or is_auditor(principal):
        platform = AdminScope.platform()
        options.append(
            AdminScopeOption(
                scope=platform,
                label="Platform scope",
                href=f"/admin/scope?{urlencode({'next': current_path})}",
                selected=active_scope.scope_type == "platform",
            )
        )
    if principal.tenant_id is not None:
        tenant_scope = AdminScope.tenant(principal.tenant_id)
        query = urlencode({"next": current_path, "tenant_id": str(principal.tenant_id)})
        href = f"/admin/scope?{query}"
        options.append(
            AdminScopeOption(
                scope=tenant_scope,
                label=f"Tenant scope {tenant_scope.label}",
                href=href,
                selected=active_scope.tenant_id == principal.tenant_id,
            )
        )
    if (
        active_scope.scope_type == "tenant"
        and active_scope.tenant_id is not None
        and all(option.scope.tenant_id != active_scope.tenant_id for option in options)
    ):
        query = urlencode(
            {"next": current_path, "tenant_id": str(active_scope.tenant_id)}
        )
        href = f"/admin/scope?{query}"
        options.append(
            AdminScopeOption(
                scope=active_scope,
                label=f"Tenant scope {active_scope.label}",
                href=href,
                selected=True,
            )
        )
    return tuple(options)


def navigation_registry() -> tuple[NavigationItem, ...]:
    return (
        NavigationItem(
            item_id="home",
            label="Console Home",
            group="Access",
            href="/admin",
            route_surface_key="GET:/admin",
            required_scope="either",
            admin_area="home",
            preserve_tenant_scope=True,
            active_matchers=("/admin",),
            order=0,
        ),
        NavigationItem(
            item_id="workflow_registry",
            label="Workflow Registry",
            group="Workflows",
            href="/admin/workflows/ui",
            route_surface_key="GET:/admin/workflows/ui",
            required_scope="either",
            admin_area="workflows",
            preserve_tenant_scope=True,
            active_matchers=("/admin/workflows",),
            order=10,
            filter_profile="workflows",
        ),
        NavigationItem(
            item_id="model_skill_config",
            label="Configuration",
            group="Model And Skill Config",
            href="/admin/config/ui",
            route_surface_key="GET:/admin/config/ui",
            required_scope="tenant",
            admin_area="model_skill_config",
            preserve_tenant_scope=True,
            active_matchers=("/admin/config/ui",),
            order=20,
        ),
        NavigationItem(
            item_id="model_skill_history",
            label="Configuration History",
            group="Model And Skill Config",
            href="/admin/config/ui/history",
            route_surface_key="GET:/admin/config/ui/history",
            required_scope="tenant",
            admin_area="model_skill_history",
            preserve_tenant_scope=True,
            active_matchers=("/admin/config/ui/history",),
            order=21,
            filter_profile="model_skill_history",
        ),
        NavigationItem(
            item_id="skill_registry_packages",
            label="Skill Registry",
            group="Model And Skill Config",
            href="/admin/skill-registry/ui/packages",
            route_surface_key="GET:/admin/skill-registry/ui/packages",
            required_scope="either",
            admin_area="skill_registry",
            preserve_tenant_scope=True,
            active_matchers=("/admin/skill-registry",),
            order=22,
            filter_profile="skill_registry",
        ),
        NavigationItem(
            item_id="skill_registry_installations",
            label="Installed Skills",
            group="Model And Skill Config",
            href="/admin/skill-registry/ui/installations",
            route_surface_key="GET:/admin/skill-registry/ui/installations",
            required_scope="tenant",
            admin_area="skill_registry_installations",
            preserve_tenant_scope=True,
            active_matchers=("/admin/skill-registry/ui/installations",),
            order=23,
            filter_profile="skill_registry_installations",
        ),
        NavigationItem(
            item_id="agent_tests",
            label="Agent Tests",
            group="Model And Skill Config",
            href="/admin/agent-tests/ui",
            route_surface_key="GET:/admin/agent-tests/ui",
            required_scope="either",
            admin_area="agent_tests",
            preserve_tenant_scope=True,
            active_matchers=("/admin/agent-tests",),
            order=24,
            filter_profile="agent_tests",
        ),
        NavigationItem(
            item_id="usage_analytics",
            label="Usage Analytics",
            group="Model And Skill Config",
            href="/admin/usage",
            route_surface_key="GET:/admin/usage",
            required_scope="either",
            admin_area="usage_analytics",
            preserve_tenant_scope=True,
            active_matchers=("/admin/usage",),
            order=24,
            filter_profile="usage_analytics",
        ),
        NavigationItem(
            item_id="telegram_configuration",
            label="Telegram Configuration",
            group="Model And Skill Config",
            href="/admin/telegram",
            route_surface_key="GET:/admin/telegram",
            required_scope="either",
            admin_area="telegram_configuration",
            preserve_tenant_scope=True,
            active_matchers=("/admin/telegram",),
            order=25,
            filter_profile="telegram_configuration",
        ),
        NavigationItem(
            item_id="model_providers",
            label="Model Providers",
            group="Model And Skill Config",
            href="/admin/model-providers",
            route_surface_key="GET:/admin/model-providers",
            required_scope="either",
            admin_area="model_providers",
            preserve_tenant_scope=True,
            active_matchers=("/admin/model-providers",),
            order=26,
            filter_profile="model_providers",
        ),
        NavigationItem(
            item_id="prompt_library",
            label="Prompt Library",
            group="Prompt Runtime",
            href="/admin/prompt-runtime/prompts",
            route_surface_key="GET:/admin/prompt-runtime/prompts",
            required_scope="either",
            admin_area="prompt_library",
            preserve_tenant_scope=True,
            active_matchers=("/admin/prompt-runtime/prompts",),
            order=23,
            filter_profile="prompt_library",
        ),
        NavigationItem(
            item_id="agent_profiles",
            label="Agent Profiles",
            group="Prompt Runtime",
            href="/admin/prompt-runtime/profiles",
            route_surface_key="GET:/admin/prompt-runtime/profiles",
            required_scope="either",
            admin_area="agent_profiles",
            preserve_tenant_scope=True,
            active_matchers=("/admin/prompt-runtime/profiles",),
            order=24,
            filter_profile="agent_profiles",
        ),
        NavigationItem(
            item_id="run_search",
            label="Run Search",
            group="Run Inspection",
            href="/admin/runs",
            route_surface_key="GET:/admin/runs",
            required_scope="either",
            admin_area="run_inspection",
            preserve_tenant_scope=True,
            active_matchers=("/admin/runs",),
            order=30,
            filter_profile="run_inspection",
        ),
        NavigationItem(
            item_id="operations_console",
            label="Operations Console",
            group="Operations",
            href="/admin/operations",
            route_surface_key="GET:/admin/operations",
            required_scope="platform",
            admin_area="operations",
            preserve_tenant_scope=False,
            active_matchers=("/admin/operations",),
            order=35,
            filter_profile="operations",
        ),
        NavigationItem(
            item_id="reliability_dashboard",
            label="Reliability Dashboard",
            group="Reliability",
            href="/admin/reliability/ui/",
            route_surface_key="GET:/admin/reliability/ui/",
            required_scope="either",
            admin_area="reliability",
            preserve_tenant_scope=True,
            active_matchers=("/admin/reliability/ui/",),
            order=40,
        ),
        NavigationItem(
            item_id="reliability_breakers",
            label="Circuit Breakers",
            group="Reliability",
            href="/admin/reliability/ui/breakers",
            route_surface_key="GET:/admin/reliability/ui/breakers",
            required_scope="either",
            admin_area="reliability_breakers",
            preserve_tenant_scope=True,
            active_matchers=("/admin/reliability/ui/breakers",),
            order=41,
            filter_profile="reliability_breakers",
        ),
        NavigationItem(
            item_id="reliability_dead_letters",
            label="Dead Letters",
            group="Reliability",
            href="/admin/reliability/ui/dead-letters",
            route_surface_key="GET:/admin/reliability/ui/dead-letters",
            required_scope="either",
            admin_area="reliability_dead_letters",
            preserve_tenant_scope=True,
            active_matchers=("/admin/reliability/ui/dead-letters",),
            order=42,
            filter_profile="reliability_dead_letters",
        ),
    )


def _item_scope_allowed(
    item: NavigationItem,
    active_scope: AdminScope,
) -> tuple[bool, str]:
    if item.required_scope == "platform" and active_scope.scope_type != "platform":
        return False, "requires_platform_scope"
    if item.required_scope == "tenant" and active_scope.scope_type != "tenant":
        return False, "requires_tenant_scope"
    return True, "scope_allowed"


def _policy_allows(
    *,
    principal: PrincipalContext,
    active_scope: AdminScope,
    surface_key: str,
) -> tuple[bool, str]:
    surface = SURFACE_POLICIES.get(surface_key)
    if surface is None:
        return False, "missing_surface_policy"
    if surface.classification is SurfaceClassification.PUBLIC:
        return False, "public_surface_policy"
    if surface.required_permissions and not set(surface.required_permissions).issubset(
        set(principal.permission_codes)
    ):
        return False, "insufficient_permission"
    if surface.classification is SurfaceClassification.AUTHENTICATED:
        return True, "authenticated_admin"
    if surface.classification is SurfaceClassification.PLATFORM_ADMIN:
        return is_platform_admin(principal), "platform_admin_required"
    if surface.classification in {
        SurfaceClassification.TENANT_USER,
        SurfaceClassification.TENANT_ADMIN,
    }:
        if active_scope.scope_type != "tenant":
            return False, "tenant_scope_required"
        if is_platform_admin(principal):
            return True, "platform_admin_tenant_scope"
        if principal.tenant_id != active_scope.tenant_id:
            return False, "cross_tenant_scope"
        required_roles = set(surface.required_roles)
        if surface.classification is SurfaceClassification.TENANT_USER:
            required_roles = required_roles or {"tenant_user"}
            return bool(set(principal.role_codes) & required_roles), "tenant_role"
        required_roles = required_roles or {"tenant_admin"}
        return bool(set(principal.role_codes) & required_roles), "tenant_admin_role"
    return False, "unsupported_surface_policy"


def filter_navigation_items(
    *,
    principal: PrincipalContext,
    active_scope: AdminScope,
    current_path: str,
) -> tuple[tuple[NavigationGroup, ...], tuple[NavigationOutcome, ...]]:
    visible_by_group: dict[str, list[NavigationItem]] = {}
    outcomes: list[NavigationOutcome] = []
    for item in sorted(navigation_registry(), key=lambda candidate: candidate.order):
        scope_allowed, scope_reason = _item_scope_allowed(item, active_scope)
        policy_allowed, policy_reason = _policy_allows(
            principal=principal,
            active_scope=active_scope,
            surface_key=item.route_surface_key,
        )
        allowed = scope_allowed and policy_allowed
        reason = policy_reason if scope_allowed else scope_reason
        outcomes.append(
            NavigationOutcome(
                item_id=item.item_id,
                route_surface_key=item.route_surface_key,
                outcome="allowed" if allowed else "denied",
                reason_category=reason,
            )
        )
        if not allowed:
            continue
        href = (
            with_scope_query(item.href, active_scope)
            if item.preserve_tenant_scope
            else item.href
        )
        visible_by_group.setdefault(item.group, []).append(
            item.model_copy(
                update={
                    "href": href,
                    "active": any(
                        current_path == matcher or current_path.startswith(matcher)
                        for matcher in item.active_matchers
                    ),
                }
            )
        )
    groups = tuple(
        NavigationGroup(label=label, items=tuple(items))
        for label, items in visible_by_group.items()
        if items
    )
    return groups, tuple(outcomes)


def default_breadcrumbs(title: str, current_path: str) -> tuple[BreadcrumbItem, ...]:
    if current_path == "/admin":
        return (BreadcrumbItem(label="Admin", href="/admin", active=True),)
    return (
        BreadcrumbItem(label="Admin", href="/admin"),
        BreadcrumbItem(label=title, href=current_path, active=True),
    )


def build_admin_shell_context(
    *,
    principal: PrincipalContext,
    active_scope: AdminScope,
    current_path: str,
    title: str,
    breadcrumbs: Sequence[BreadcrumbItem] = (),
    page_actions: Sequence[PageAction] = (),
    messages: Sequence[FlashMessage] = (),
    common_state: CommonState | None = None,
    saved_filters: Sequence[SavedFilterSummary] = (),
    filter_restore_outcome: str | None = None,
    available_scopes: Sequence[AdminScopeOption] | None = None,
) -> AdminShellContext:
    if not principal_can_use_scope(principal, active_scope):
        raise AdminConsoleAccessError(
            "admin scope is not authorized",
            reason_category="cross_tenant_scope"
            if active_scope.scope_type == "tenant"
            else "insufficient_role",
        )
    navigation_groups, navigation_outcomes = filter_navigation_items(
        principal=principal,
        active_scope=active_scope,
        current_path=current_path,
    )
    resolved_breadcrumbs = breadcrumbs or default_breadcrumbs(title, current_path)
    return AdminShellContext(
        title=sanitize_text(title, fallback="Admin Console", max_length=90),
        active_scope=active_scope,
        available_scopes=tuple(available_scopes)
        if available_scopes is not None
        else available_scope_options(
            principal=principal,
            active_scope=active_scope,
            current_path=current_path,
        ),
        navigation_groups=navigation_groups,
        breadcrumbs=sanitize_breadcrumbs(resolved_breadcrumbs),
        page_actions=tuple(action for action in page_actions if action.allowed),
        messages=tuple(messages),
        common_state=common_state,
        saved_filters=tuple(saved_filters),
        filter_restore_outcome=filter_restore_outcome,
        trace_id=principal.trace_id,
        navigation_outcomes=navigation_outcomes,
    )


def filter_profiles() -> dict[str, FilterProfile]:
    return {
        "workflows": FilterProfile(
            admin_area="workflows",
            filter_key="workflow-list",
            destination_href="/admin/workflows/ui",
            allowed_criteria=("status", "scope_type", "workflow_kind", "slug"),
            labels={
                "status": "Status",
                "scope_type": "Scope",
                "workflow_kind": "Workflow kind",
                "slug": "Slug",
            },
        ),
        "model_skill_history": FilterProfile(
            admin_area="model_skill_history",
            filter_key="model-skill-history",
            destination_href="/admin/config/ui/history",
            allowed_criteria=("tenant_id", "config_kind", "actor", "limit"),
            labels={
                "tenant_id": "Tenant",
                "config_kind": "Config kind",
                "actor": "Actor",
                "limit": "Limit",
            },
        ),
        "model_providers": FilterProfile(
            admin_area="model_providers",
            filter_key="model-providers",
            destination_href="/admin/model-providers",
            allowed_criteria=(
                "provider_type",
                "health_state",
                "active",
                "visibility",
                "model_id",
            ),
            labels={
                "provider_type": "Provider",
                "health_state": "Health",
                "active": "Active",
                "visibility": "Visibility",
                "model_id": "Model",
            },
        ),
        "telegram_configuration": FilterProfile(
            admin_area="telegram_configuration",
            filter_key="telegram-configuration",
            destination_href="/admin/telegram",
            allowed_criteria=("tenant_id", "enabled", "status", "category"),
            labels={
                "tenant_id": "Tenant",
                "enabled": "Enabled",
                "status": "Status",
                "category": "Diagnostic category",
            },
        ),
        "run_inspection": FilterProfile(
            admin_area="run_inspection",
            filter_key="run-search",
            destination_href="/admin/runs",
            allowed_criteria=(
                "tenant_id",
                "workflow_run_id",
                "workflow_id",
                "status",
                "failure_category",
                "agent",
                "tool",
            ),
            labels={
                "tenant_id": "Tenant",
                "workflow_run_id": "Run",
                "workflow_id": "Workflow",
                "status": "Status",
                "failure_category": "Failure",
                "agent": "Agent",
                "tool": "Tool",
            },
        ),
        "operations": FilterProfile(
            admin_area="operations",
            filter_key="operations-console",
            destination_href="/admin/operations",
            allowed_criteria=(
                "trace_id",
                "tenant_id",
                "run_id",
                "component",
                "severity",
                "status",
                "dependency",
            ),
            labels={
                "trace_id": "Trace",
                "tenant_id": "Tenant",
                "run_id": "Run",
                "component": "Component",
                "severity": "Severity",
                "status": "Status",
                "dependency": "Dependency",
            },
        ),
        "reliability_breakers": FilterProfile(
            admin_area="reliability_breakers",
            filter_key="reliability-breakers",
            destination_href="/admin/reliability/ui/breakers",
            allowed_criteria=("tenant_id", "state", "scope_type", "scope_key"),
            labels={
                "tenant_id": "Tenant",
                "state": "State",
                "scope_type": "Scope type",
                "scope_key": "Scope key",
            },
        ),
        "reliability_dead_letters": FilterProfile(
            admin_area="reliability_dead_letters",
            filter_key="reliability-dead-letters",
            destination_href="/admin/reliability/ui/dead-letters",
            allowed_criteria=("tenant_id", "status", "failure_category", "source_kind"),
            labels={
                "tenant_id": "Tenant",
                "status": "Status",
                "failure_category": "Failure",
                "source_kind": "Source",
            },
        ),
    }


def _criteria_from_input(criteria: Mapping[str, object] | str) -> dict[str, object]:
    if isinstance(criteria, str):
        parsed = json.loads(criteria or "{}")
        if not isinstance(parsed, dict):
            raise ValueError("criteria must be a JSON object")
        return dict(parsed)
    return dict(criteria)


def _normalize_value(value: object) -> str | int | float | bool | list[str] | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool | int | float):
        return value
    if isinstance(value, str):
        safe = sanitize_text(value, fallback="")
        if not safe:
            raise ValueError("criterion value contains protected detail")
        return safe
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        normalized: list[str] = []
        for item in value:
            safe = sanitize_text(item, fallback="")
            if not safe:
                raise ValueError("criterion value contains protected detail")
            normalized.append(safe)
        return normalized
    raise ValueError("criterion value is unsupported")


def normalize_filter_criteria(
    admin_area: str,
    criteria: Mapping[str, object] | str,
    *,
    active_scope: AdminScope,
    filter_key: str | None = None,
) -> NormalizedFilterCriteria:
    profiles = filter_profiles()
    profile = profiles.get(admin_area)
    if profile is None:
        raise ValueError("unsupported admin area")
    requested = _criteria_from_input(criteria)
    allowed = set(profile.allowed_criteria)
    normalized: dict[str, str | int | float | bool | list[str]] = {}
    for key, value in requested.items():
        if key not in allowed:
            raise ValueError(f"unsupported criterion: {key}")
        normalized_value = _normalize_value(value)
        if normalized_value is None:
            continue
        if key == "tenant_id" and active_scope.scope_type == "tenant":
            if str(normalized_value) != str(active_scope.tenant_id):
                raise ValueError("tenant criterion does not match active scope")
        normalized[key] = normalized_value
    safe_summary = {
        key: ", ".join(value) if isinstance(value, list) else str(value)
        for key, value in sorted(normalized.items())
    }
    return NormalizedFilterCriteria(
        admin_area=admin_area,
        filter_key=filter_key or profile.filter_key,
        criteria=normalized,
        safe_summary=safe_summary,
    )


def build_saved_filter_summary(
    record: Any,
    *,
    active_scope: AdminScope,
) -> SavedFilterSummary:
    filter_id = record.admin_saved_filter_id
    restore_href = with_scope_query(
        f"/admin/filters/{record.admin_area}/{filter_id}/restore",
        active_scope,
    )
    delete_href = with_scope_query(
        f"/admin/filters/{record.admin_area}/{filter_id}",
        active_scope,
    )
    last_restored_at = getattr(record, "last_restored_at", None)
    return SavedFilterSummary(
        filter_id=filter_id,
        display_name=sanitize_text(record.display_name, max_length=120),
        admin_area=record.admin_area,
        filter_key=record.filter_key,
        safe_summary={
            str(key): sanitize_text(value, max_length=120)
            for key, value in dict(record.safe_summary or {}).items()
        },
        restore_href=restore_href,
        delete_href=delete_href,
        last_restored_at=last_restored_at.isoformat()
        if last_restored_at is not None
        else None,
    )
