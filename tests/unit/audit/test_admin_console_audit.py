from __future__ import annotations

from tests.fixtures.admin_console import platform_principal

from multi_agent_platform.api.ui.admin_console import (
    AdminScope,
    NavigationOutcome,
)
from multi_agent_platform.audit.service import AuditService


class _Repo:
    def __init__(self) -> None:
        self.events: list[object] = []

    async def create(self, audit_event: object) -> object:
        self.events.append(audit_event)
        return audit_event


async def test_navigation_visibility_audit_event_is_itemized_and_safe() -> None:
    repo = _Repo()
    service = AuditService(repo)  # type: ignore[arg-type]

    await service.record_admin_navigation_visibility(
        principal=platform_principal(),
        active_scope=AdminScope.platform(),
        request_path="/admin",
        outcomes=[
            NavigationOutcome(
                item_id="home",
                route_surface_key="GET:/admin",
                outcome="allowed",
                reason_category="allowed",
            )
        ],
    )

    assert len(repo.events) == 1
    event = repo.events[0]
    assert event.action == "admin_shell.navigation_visibility"
    assert event.payload_redacted["item_outcomes"].startswith("[")


async def test_scope_selection_and_filter_restore_audits_are_separate() -> None:
    repo = _Repo()
    service = AuditService(repo)  # type: ignore[arg-type]
    principal = platform_principal()

    await service.record_admin_scope_selection(
        principal=principal,
        active_scope=AdminScope.platform(),
        selected_scope=AdminScope.platform(),
        outcome="allowed",
        reason_category="platform_scope",
    )
    await service.record_admin_filter_restore(
        principal=principal,
        active_scope=AdminScope.platform(),
        admin_area="workflows",
        filter_id="filter-1",
        outcome="allowed",
        reason_category="validated",
    )

    assert [event.action for event in repo.events] == [
        "admin_shell.scope_selection",
        "admin_shell.saved_filter_restore",
    ]
