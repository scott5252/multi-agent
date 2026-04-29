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


def test_resolve_surface_registers_workflow_builder_surfaces() -> None:
    expected = {
        ("GET", "/admin/workflows/editor-lookups"): "read_workflow_editor_lookups",
        (
            "GET",
            "/admin/workflows/drafts/{workflow_draft_id}/graph-preview",
        ): "read_workflow_graph_preview",
        (
            "GET",
            "/admin/workflows/drafts/{workflow_draft_id}/revisions",
        ): "list_workflow_draft_revisions",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/publish-gate",
        ): "evaluate_workflow_publish_gate",
        (
            "GET",
            "/admin/workflows/drafts/{workflow_draft_id}/revisions/ui",
        ): "render_workflow_revision_history_ui",
        ("POST", "/admin/workflows/new"): "create_workflow_draft_ui",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/save-ui",
        ): "save_workflow_draft_ui",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/validate/ui",
        ): "validate_workflow_draft_ui",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/restore/ui",
        ): "restore_workflow_draft_revision_ui",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/copy/ui",
        ): "copy_workflow_draft_ui",
        (
            "POST",
            "/admin/workflows/drafts/{workflow_draft_id}/publish/ui",
        ): "publish_workflow_draft_ui",
    }

    for (method, path), action in expected.items():
        surface = resolve_surface(method, path)
        assert surface.classification == "authenticated"
        assert surface.requested_action == action
