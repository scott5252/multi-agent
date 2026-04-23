from __future__ import annotations

from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.config.settings import LocalPrincipalCatalogEntry


def test_local_principal_catalog_resolves_enabled_entries() -> None:
    catalog = LocalPrincipalCatalog(
        {
            "tenant-admin": LocalPrincipalCatalogEntry(
                catalog_key="tenant-admin",
                display_name="Tenant Admin",
                role_codes=("tenant_admin",),
            ),
            "disabled-user": LocalPrincipalCatalogEntry(
                catalog_key="disabled-user",
                display_name="Disabled",
                enabled=False,
            ),
        }
    )

    assert catalog.resolve("tenant-admin") is not None
    assert catalog.resolve("disabled-user") is None
