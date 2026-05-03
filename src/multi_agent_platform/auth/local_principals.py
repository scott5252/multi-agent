from __future__ import annotations

from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.config.settings import LocalPrincipalCatalogEntry
from multi_agent_platform.tenancy.context import ScopeType


class LocalPrincipalCatalog:
    def __init__(
        self, entries: dict[str, LocalPrincipalCatalogEntry] | None = None
    ) -> None:
        self.entries = entries or {}

    def resolve(self, catalog_key: str) -> LocalPrincipalCatalogEntry | None:
        entry = self.entries.get(catalog_key)
        if entry is None or not entry.enabled:
            return None
        return entry

    def as_principal_context(
        self,
        catalog_key: str,
        *,
        trace_id: str,
        request_id: str | None,
    ) -> PrincipalContext | None:
        entry = self.resolve(catalog_key)
        if entry is None:
            return None
        return PrincipalContext(
            principal_id=entry.catalog_key,
            auth_provider=AuthProvider.LOCAL_PRINCIPAL,
            auth_mode=AuthMode.LOCAL_PRINCIPAL,
            tenant_id=entry.tenant_id,
            org_id=entry.org_id,
            role_codes=entry.role_codes,
            permission_codes=entry.permission_codes,
            scope_type=(
                ScopeType.TENANT if entry.tenant_id is not None else ScopeType.PLATFORM
            ),
            trace_id=trace_id,
            request_id=request_id,
            token_subject=entry.catalog_key,
        )


SKILL_REGISTRY_PLATFORM_PERMISSIONS = (
    "platform:admin",
    "skill-registry:publish",
    "skill-registry:quarantine",
    "skill-registry:audit",
)
SKILL_REGISTRY_TENANT_PERMISSIONS = (
    "tenant:read",
    "tenant:admin",
    "skill-registry:install",
    "skill-registry:bind",
    "skill-registry:audit",
)
AGENT_TEST_PLATFORM_PERMISSIONS = (
    "platform:admin",
    "agent-tests:manage",
    "agent-tests:run",
    "agent-tests:read",
    "agent-tests:gate",
)
AGENT_TEST_TENANT_PERMISSIONS = (
    "tenant:read",
    "tenant:admin",
    "agent-tests:manage",
    "agent-tests:run",
    "agent-tests:read",
    "agent-tests:gate",
)
USAGE_ANALYTICS_PLATFORM_PERMISSIONS = (
    "platform:admin",
    "usage:read",
    "usage:export",
)
USAGE_ANALYTICS_TENANT_PERMISSIONS = (
    "tenant:read",
    "tenant:admin",
    "usage:read",
    "usage:export",
)
TELEGRAM_CONFIG_PLATFORM_PERMISSIONS = (
    "platform:admin",
    "telegram-config:read",
    "telegram-config:write",
    "telegram-config:tokens",
    "telegram-config:diagnostics",
)
TELEGRAM_CONFIG_TENANT_PERMISSIONS = (
    "tenant:read",
    "tenant:admin",
    "telegram-config:read",
    "telegram-config:write",
    "telegram-config:tokens",
    "telegram-config:diagnostics",
)
MEMBERSHIP_ADMIN_PLATFORM_PERMISSIONS = (
    "platform:admin",
    "membership-admin:read",
    "membership-admin:invite",
    "membership-admin:write",
    "membership-admin:grants",
    "membership-admin:audit",
)
MEMBERSHIP_ADMIN_TENANT_PERMISSIONS = (
    "tenant:read",
    "tenant:admin",
    "membership-admin:read",
    "membership-admin:invite",
    "membership-admin:write",
    "membership-admin:grants",
    "membership-admin:audit",
)


def skill_registry_permission_codes(*, platform: bool) -> tuple[str, ...]:
    if platform:
        return SKILL_REGISTRY_PLATFORM_PERMISSIONS
    return SKILL_REGISTRY_TENANT_PERMISSIONS


def agent_test_permission_codes(*, platform: bool) -> tuple[str, ...]:
    if platform:
        return AGENT_TEST_PLATFORM_PERMISSIONS
    return AGENT_TEST_TENANT_PERMISSIONS


def usage_analytics_permission_codes(*, platform: bool) -> tuple[str, ...]:
    if platform:
        return USAGE_ANALYTICS_PLATFORM_PERMISSIONS
    return USAGE_ANALYTICS_TENANT_PERMISSIONS


def telegram_config_permission_codes(*, platform: bool) -> tuple[str, ...]:
    if platform:
        return TELEGRAM_CONFIG_PLATFORM_PERMISSIONS
    return TELEGRAM_CONFIG_TENANT_PERMISSIONS


def membership_admin_permission_codes(*, platform: bool) -> tuple[str, ...]:
    if platform:
        return MEMBERSHIP_ADMIN_PLATFORM_PERMISSIONS
    return MEMBERSHIP_ADMIN_TENANT_PERMISSIONS
