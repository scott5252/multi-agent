from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.auth.principal import PrincipalContext


class ReactAdminScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class ReactAdminRequiredScope(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"
    EITHER = "either"


class ReactAdminFallbackKind(StrEnum):
    JINJA = "jinja"
    REACT = "react"
    DISABLED = "disabled"


class ReactAdminPageActionMethod(StrEnum):
    GET = "get"


class ReactAdminPageActionVariant(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    GHOST = "ghost"


class ReactAdminShellStateKind(StrEnum):
    LOADING = "loading"
    EMPTY = "empty"
    FILTERED_EMPTY = "filtered_empty"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    PARTIAL_DATA = "partial_data"
    UNEXPECTED_ERROR = "unexpected_error"


class ReactAdminNotificationTone(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"


def _safe_summary(value: str, *, max_length: int = 160) -> str:
    value = " ".join(value.strip().split())
    if not value:
        raise ValueError("safe text is required")
    return value[:max_length]


class ReactAdminPrincipal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_id: str
    display_name: str | None = None
    role_codes: tuple[str, ...] = Field(default_factory=tuple)
    auth_mode: Literal["auth0", "local_principal"]
    trace_id: str

    @classmethod
    def from_context(cls, principal: PrincipalContext) -> ReactAdminPrincipal:
        return cls(
            principal_id=principal.principal_id,
            display_name=principal.principal_id,
            role_codes=tuple(sorted(principal.role_codes)),
            auth_mode=principal.auth_mode.value,
            trace_id=principal.trace_id,
        )


class ReactAdminScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_type: ReactAdminScopeType
    tenant_id: UUID | None = None
    label: str

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("scope label is required")
        return value[:80]


class ReactAdminScopeOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    label: str
    href: str
    selected: bool


class ReactAdminNavigationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    label: str
    group: str
    href: str
    route_surface_key: str
    required_scope: ReactAdminRequiredScope
    admin_area: str | None = None
    preserve_tenant_scope: bool
    active: bool
    fallback_kind: ReactAdminFallbackKind


class ReactAdminNavigationGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    items: tuple[ReactAdminNavigationItem, ...] = Field(default_factory=tuple)


class ReactAdminBreadcrumb(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    href: str | None = None
    active: bool = False

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=80)


class ReactAdminPageAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    label: str
    href: str | None = None
    method: ReactAdminPageActionMethod = ReactAdminPageActionMethod.GET
    variant: ReactAdminPageActionVariant = ReactAdminPageActionVariant.SECONDARY
    disabled_reason: str | None = None

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=80)

    @field_validator("disabled_reason")
    @classmethod
    def disabled_reason_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _safe_summary(value, max_length=120)


class ReactAdminShellState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ReactAdminShellStateKind
    title: str
    summary: str
    action: ReactAdminPageAction | None = None
    trace_id: str | None = None

    @field_validator("title")
    @classmethod
    def title_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=90)

    @field_validator("summary")
    @classmethod
    def summary_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=220)


class ReactAdminSavedFilterChip(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filter_id: str
    label: str
    admin_area: str
    href: str
    scope_type: ReactAdminScopeType
    tenant_id: UUID | None = None

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=90)


class ReactAdminShellNotification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    notification_id: str
    tone: ReactAdminNotificationTone
    title: str
    summary: str
    href: str | None = None

    @field_validator("title")
    @classmethod
    def title_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=90)

    @field_validator("summary")
    @classmethod
    def summary_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=180)


class ReactAdminCommandSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result_id: str
    label: str
    description: str | None = None
    group: str
    href: str
    required_scope: ReactAdminRequiredScope
    fallback_kind: ReactAdminFallbackKind

    @field_validator("label", "group")
    @classmethod
    def label_fields_are_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=90)

    @field_validator("description")
    @classmethod
    def description_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _safe_summary(value, max_length=160)


class ReactAdminCommandSearch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = ""
    results: tuple[ReactAdminCommandSearchResult, ...] = Field(default_factory=tuple)


class ReactAdminShellChrome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_name: str
    active_area: str
    breadcrumbs: tuple[ReactAdminBreadcrumb, ...] = Field(default_factory=tuple)
    page_actions: tuple[ReactAdminPageAction, ...] = Field(default_factory=tuple)
    saved_filters: tuple[ReactAdminSavedFilterChip, ...] = Field(default_factory=tuple)
    notifications: tuple[ReactAdminShellNotification, ...] = Field(
        default_factory=tuple
    )
    states: tuple[ReactAdminShellState, ...] = Field(default_factory=tuple)
    command_results: tuple[ReactAdminCommandSearchResult, ...] = Field(
        default_factory=tuple
    )
    design_token_version: str
    search_url: str

    @field_validator("product_name")
    @classmethod
    def product_name_is_safe(cls, value: str) -> str:
        return _safe_summary(value, max_length=80)


class ReactAdminFeatureFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")

    react_admin_enabled: bool
    react_domain_routes: dict[str, bool] = Field(default_factory=dict)
    source: str = "settings"


class ReactAdminVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    app_version: str
    api_version: str
    commit_sha: str
    build_time: str


class ReactAdminAssetManifestSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool
    base_path: str
    entrypoints: tuple[str, ...] = Field(default_factory=tuple)
    stylesheets: tuple[str, ...] = Field(default_factory=tuple)
    version: str | None = None
    unavailable_reason: str | None = None


class ReactAdminActionTokens(BaseModel):
    model_config = ConfigDict(extra="forbid")

    csrf_token: str | None = None
    issued_at: datetime | None = None


class ReactAdminBootstrap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal: ReactAdminPrincipal
    active_scope: ReactAdminScope
    available_scopes: tuple[ReactAdminScopeOption, ...] = Field(default_factory=tuple)
    navigation: tuple[ReactAdminNavigationGroup, ...] = Field(default_factory=tuple)
    feature_flags: ReactAdminFeatureFlags
    version: ReactAdminVersion
    asset_manifest: ReactAdminAssetManifestSummary
    action_tokens: ReactAdminActionTokens
    shell: ReactAdminShellChrome


class ReactAdminConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mount_path: str
    asset_base_path: str
    bootstrap_url: str
    config_url: str
    manifest_url: str


class SafeProblem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str
    reason: str
    trace_id: str | None = None
