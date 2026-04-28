from __future__ import annotations

from pathlib import Path


def test_admin_console_contract_lists_shell_routes_and_tenant_scope() -> None:
    contract = Path(
        "specs/010-admin-console-shell/contracts/admin-console-shell-ui.md"
    ).read_text()
    openapi = Path(
        "specs/010-admin-console-shell/contracts/admin-console-shell.openapi.yaml"
    ).read_text()

    assert "/admin" in contract
    assert "/admin/filters/{admin_area}" in openapi
    assert "tenant_id" in contract
    assert "AdminShellContext" in contract
