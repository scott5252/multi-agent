from __future__ import annotations

from multi_agent_platform.auth.policy import resolve_surface


def test_resolve_surface_returns_registered_definition() -> None:
    surface = resolve_surface("GET", "/auth/me")
    assert surface.surface_key == "GET:/auth/me"
    assert surface.classification == "authenticated"


def test_resolve_surface_defaults_unclassified_routes_to_public() -> None:
    surface = resolve_surface("GET", "/unknown")
    assert surface.classification == "public"
