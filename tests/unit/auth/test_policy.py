from __future__ import annotations

from multi_agent_platform.auth.policy import resolve_surface


def test_resolve_surface_returns_registered_definition() -> None:
    surface = resolve_surface("GET", "/auth/me")
    assert surface.surface_key == "GET:/auth/me"
    assert surface.classification == "authenticated"


def test_resolve_surface_defaults_unclassified_routes_to_public() -> None:
    surface = resolve_surface("GET", "/unknown")
    assert surface.classification == "public"


def test_resolve_surface_registers_model_skill_config_history() -> None:
    surface = resolve_surface("GET", "/admin/config/history")
    assert surface.surface_key == "GET:/admin/config/history"
    assert surface.classification == "tenant_user"
    assert surface.requested_action == "read_model_skill_config_history"
    assert surface.required_permissions == ("tenant:read",)


def test_resolve_surface_registers_model_skill_config_provenance() -> None:
    surface = resolve_surface("GET", "/admin/config/runs/{workflow_run_id}/provenance")
    assert surface.surface_key == "GET:/admin/config/runs/{workflow_run_id}/provenance"
    assert surface.classification == "tenant_user"
    assert surface.requested_action == "read_model_skill_run_provenance"
    assert surface.required_permissions == ("tenant:read",)


def test_resolve_surface_registers_model_skill_config_mutation() -> None:
    surface = resolve_surface("POST", "/admin/config/model-routing")
    assert surface.surface_key == "POST:/admin/config/model-routing"
    assert surface.classification == "tenant_user"
    assert surface.requested_action == "create_model_routing_config"
    assert surface.required_permissions == ("tenant:read",)
