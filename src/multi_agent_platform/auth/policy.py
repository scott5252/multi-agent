from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import AccessReasonCode

AUTH_POLICY_VERSION = "2026-04-22"
SURFACE_POLICY_VERSION = "2026-04-22"


class SurfaceClassification(StrEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    TENANT_USER = "tenant_user"
    TENANT_ADMIN = "tenant_admin"
    PLATFORM_ADMIN = "platform_admin"


class ProtectedSurface(BaseModel):
    surface_key: str
    requested_action: str
    classification: SurfaceClassification
    required_roles: tuple[str, ...] = Field(default_factory=tuple)
    required_permissions: tuple[str, ...] = Field(default_factory=tuple)
    support_override_required: bool = False


class AuthorizationDecision(BaseModel):
    surface_key: str
    requested_action: str
    classification: SurfaceClassification
    allowed: bool
    reason_code: AccessReasonCode
    required_roles: tuple[str, ...] = Field(default_factory=tuple)
    required_permissions: tuple[str, ...] = Field(default_factory=tuple)
    target_tenant_id: UUID | None = None
    support_override_request_id: UUID | None = None


SURFACE_POLICIES: dict[str, ProtectedSurface] = {
    "GET:/auth/me": ProtectedSurface(
        surface_key="GET:/auth/me",
        requested_action="read_principal_context",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/auth/tenant-context/{tenant_id}": ProtectedSurface(
        surface_key="GET:/auth/tenant-context/{tenant_id}",
        requested_action="read_tenant_context",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "GET:/admin/tenants/{tenant_id}/role-grants": ProtectedSurface(
        surface_key="GET:/admin/tenants/{tenant_id}/role-grants",
        requested_action="list_tenant_role_grants",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin",),
    ),
    "POST:/admin/role-grants": ProtectedSurface(
        surface_key="POST:/admin/role-grants",
        requested_action="upsert_role_grant",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("admin:role-grants:write",),
    ),
    "POST:/admin/support-overrides": ProtectedSurface(
        surface_key="POST:/admin/support-overrides",
        requested_action="create_support_override",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("admin:support-overrides:write",),
    ),
    (
        "POST:/admin/support-overrides/{support_override_request_id}/approve"
    ): ProtectedSurface(
        surface_key="POST:/admin/support-overrides/{support_override_request_id}/approve",
        requested_action="approve_support_override",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("admin:support-overrides:approve",),
    ),
    "GET:/admin/workflows": ProtectedSurface(
        surface_key="GET:/admin/workflows",
        requested_action="read_workflow_registry",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows": ProtectedSurface(
        surface_key="POST:/admin/workflows",
        requested_action="create_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/workflows/editor-metadata": ProtectedSurface(
        surface_key="GET:/admin/workflows/editor-metadata",
        requested_action="read_workflow_editor_metadata",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/workflows/drafts/{workflow_draft_id}": ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}",
        requested_action="read_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "PUT:/admin/workflows/drafts/{workflow_draft_id}": ProtectedSurface(
        surface_key="PUT:/admin/workflows/drafts/{workflow_draft_id}",
        requested_action="save_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/validate": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/validate",
        requested_action="validate_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/publish": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/publish",
        requested_action="publish_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/workflows/versions/{workflow_version_bundle_id}": ProtectedSurface(
        surface_key="GET:/admin/workflows/versions/{workflow_version_bundle_id}",
        requested_action="read_workflow_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/workflows/versions/{workflow_version_bundle_id}/sharing-grants"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/workflows/versions/{workflow_version_bundle_id}/sharing-grants"
        ),
        requested_action="create_workflow_sharing_grant",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "GET:/admin/workflows/ui": ProtectedSurface(
        surface_key="GET:/admin/workflows/ui",
        requested_action="render_workflow_registry_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    ("GET:/admin/workflows/drafts/{workflow_draft_id}/editor"): ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/editor",
        requested_action="render_workflow_draft_editor_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/workflows/versions/{workflow_version_bundle_id}/detail"
    ): ProtectedSurface(
        surface_key="GET:/admin/workflows/versions/{workflow_version_bundle_id}/detail",
        requested_action="render_workflow_version_detail_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/config/model-routing": ProtectedSurface(
        surface_key="POST:/admin/config/model-routing",
        requested_action="create_model_routing_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/model-routing/{version_id}/activate": ProtectedSurface(
        surface_key="POST:/admin/config/model-routing/{version_id}/activate",
        requested_action="activate_model_routing_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/prompt-references": ProtectedSurface(
        surface_key="POST:/admin/config/prompt-references",
        requested_action="create_prompt_reference_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/skill-bindings": ProtectedSurface(
        surface_key="POST:/admin/config/skill-bindings",
        requested_action="create_skill_binding_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/tool-policies": ProtectedSurface(
        surface_key="POST:/admin/config/tool-policies",
        requested_action="create_tool_policy_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/outbound-domain-policies": ProtectedSurface(
        surface_key="POST:/admin/config/outbound-domain-policies",
        requested_action="create_outbound_domain_policy_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/secret-references": ProtectedSurface(
        surface_key="POST:/admin/config/secret-references",
        requested_action="create_secret_reference_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/credential-requirements": ProtectedSurface(
        surface_key="POST:/admin/config/credential-requirements",
        requested_action="create_credential_requirement_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/preview/model": ProtectedSurface(
        surface_key="POST:/admin/config/preview/model",
        requested_action="preview_model_routing_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/admin/config/preview/tool": ProtectedSurface(
        surface_key="POST:/admin/config/preview/tool",
        requested_action="preview_tool_policy_config",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "GET:/admin/config/history": ProtectedSurface(
        surface_key="GET:/admin/config/history",
        requested_action="read_model_skill_config_history",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "GET:/admin/config/runs/{workflow_run_id}/provenance": ProtectedSurface(
        surface_key="GET:/admin/config/runs/{workflow_run_id}/provenance",
        requested_action="read_model_skill_run_provenance",
        classification=SurfaceClassification.TENANT_USER,
        required_roles=("tenant_user",),
        required_permissions=("tenant:read",),
    ),
    "POST:/runtime/runs": ProtectedSurface(
        surface_key="POST:/runtime/runs",
        requested_action="start_runtime_run",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}",
        requested_action="inspect_runtime_run",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/runtime/runs/{workflow_run_id}/cancel": ProtectedSurface(
        surface_key="POST:/runtime/runs/{workflow_run_id}/cancel",
        requested_action="cancel_runtime_run",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}/timeline": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}/timeline",
        requested_action="read_runtime_timeline",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}/lineage": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}/lineage",
        requested_action="read_runtime_lineage",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}/approval-gates": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}/approval-gates",
        requested_action="list_runtime_approval_gates",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/runtime/runs/{workflow_run_id}/approval-gates/"
        "{approval_gate_id}/decisions"
    ): ProtectedSurface(
        surface_key=(
            "POST:/runtime/runs/{workflow_run_id}/approval-gates/"
            "{approval_gate_id}/decisions"
        ),
        requested_action="decide_runtime_approval_gate",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}/handoffs": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}/handoffs",
        requested_action="list_runtime_handoffs",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/runtime/runs/{workflow_run_id}/side-effects": ProtectedSurface(
        surface_key="GET:/runtime/runs/{workflow_run_id}/side-effects",
        requested_action="list_runtime_side_effects",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/memory/head": ProtectedSurface(
        surface_key="GET:/memory/head",
        requested_action="read_memory_head",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/memory/versions": ProtectedSurface(
        surface_key="POST:/memory/versions",
        requested_action="create_memory_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/memory/versions/{memory_version_id}": ProtectedSurface(
        surface_key="GET:/memory/versions/{memory_version_id}",
        requested_action="read_memory_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/memory/scopes/{memory_scope_id}/versions": ProtectedSurface(
        surface_key="GET:/memory/scopes/{memory_scope_id}/versions",
        requested_action="list_memory_history",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/memory/versions/{memory_version_id}/replay": ProtectedSurface(
        surface_key="GET:/memory/versions/{memory_version_id}/replay",
        requested_action="replay_memory_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/memory/diffs": ProtectedSurface(
        surface_key="POST:/memory/diffs",
        requested_action="diff_memory_versions",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/memory/audit": ProtectedSurface(
        surface_key="GET:/memory/audit",
        requested_action="list_memory_audit",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
}


def route_surface_key(method: str, route_path: str) -> str:
    return f"{method.upper()}:{route_path}"


def resolve_surface(method: str, route_path: str) -> ProtectedSurface:
    surface = SURFACE_POLICIES.get(route_surface_key(method, route_path))
    if surface is None:
        return ProtectedSurface(
            surface_key=route_surface_key(method, route_path),
            requested_action="unclassified_surface",
            classification=SurfaceClassification.PUBLIC,
        )
    return surface


def principal_has_role(principal: PrincipalContext, *roles: str) -> bool:
    return any(role in principal.role_codes for role in roles)
