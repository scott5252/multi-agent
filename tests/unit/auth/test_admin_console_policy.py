from __future__ import annotations

from multi_agent_platform.auth.policy import SURFACE_POLICIES, SurfaceClassification
from tests.fixtures.admin_console import ADMIN_CONSOLE_ROUTE_SURFACES


def test_admin_console_surfaces_are_registered_and_protected() -> None:
    missing = [
        surface
        for surface in ADMIN_CONSOLE_ROUTE_SURFACES
        if surface not in SURFACE_POLICIES
    ]

    assert missing == []
    assert all(
        SURFACE_POLICIES[surface].classification is not SurfaceClassification.PUBLIC
        for surface in ADMIN_CONSOLE_ROUTE_SURFACES
    )
