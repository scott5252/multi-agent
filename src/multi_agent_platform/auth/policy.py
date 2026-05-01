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
    "GET:/admin/skill-registry/ui/packages": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/packages",
        requested_action="render_skill_registry_packages",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/skill-registry/ui/packages/new": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/packages/new",
        requested_action="render_skill_package_create_form",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    "POST:/admin/skill-registry/ui/packages": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/ui/packages",
        requested_action="create_skill_package_from_browser",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    "GET:/admin/skill-registry/ui/packages/{slug}": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/packages/{slug}",
        requested_action="render_skill_registry_package_detail",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/skill-registry/ui/packages/{slug}/candidate": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/packages/{slug}/candidate",
        requested_action="render_skill_manifest_candidate_form",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    "POST:/admin/skill-registry/ui/packages/{slug}/candidate": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/ui/packages/{slug}/candidate",
        requested_action="save_skill_manifest_candidate",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "POST:/admin/skill-registry/ui/packages/{slug}/candidate/validate"
    ): ProtectedSurface(
        surface_key="POST:/admin/skill-registry/ui/packages/{slug}/candidate/validate",
        requested_action="validate_skill_manifest_candidate_from_browser",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "POST:/admin/skill-registry/ui/packages/{slug}/candidate/publish"
    ): ProtectedSurface(
        surface_key="POST:/admin/skill-registry/ui/packages/{slug}/candidate/publish",
        requested_action="publish_skill_manifest_candidate_from_browser",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "GET:/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}"
        ),
        requested_action="render_skill_registry_version_detail",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/skill-registry/ui/packages/{slug}/versions/"
        "{semantic_version}/grants"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/skill-registry/ui/packages/{slug}/versions/"
            "{semantic_version}/grants"
        ),
        requested_action="render_skill_tenant_grants_form",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "POST:/admin/skill-registry/ui/packages/{slug}/versions/"
        "{semantic_version}/grants"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/ui/packages/{slug}/versions/"
            "{semantic_version}/grants"
        ),
        requested_action="save_skill_tenant_grants_from_browser",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    "GET:/admin/skill-registry/ui/available-versions": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/available-versions",
        requested_action="render_available_skill_versions",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    "POST:/admin/skill-registry/ui/installations": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/ui/installations",
        requested_action="install_tenant_skill_from_browser",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    "GET:/admin/skill-registry/ui/installations": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/installations",
        requested_action="render_skill_registry_installations",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    "GET:/admin/skill-registry/ui/installations/{installation_id}": ProtectedSurface(
        surface_key="GET:/admin/skill-registry/ui/installations/{installation_id}",
        requested_action="render_skill_registry_installation_detail",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "GET:/admin/skill-registry/ui/installations/{installation_id}/credentials"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/skill-registry/ui/installations/{installation_id}/credentials"
        ),
        requested_action="render_skill_credential_reference_form",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "POST:/admin/skill-registry/ui/installations/{installation_id}/credentials"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/ui/installations/{installation_id}/credentials"
        ),
        requested_action="configure_skill_credentials_from_browser",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "POST:/admin/skill-registry/ui/installations/{installation_id}/smoke-tests"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/ui/installations/{installation_id}/smoke-tests"
        ),
        requested_action="refresh_skill_smoke_tests_from_browser",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "POST:/admin/skill-registry/ui/installations/{installation_id}/"
        "eligibility-preview"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/ui/installations/{installation_id}/"
            "eligibility-preview"
        ),
        requested_action="preview_skill_binding_from_browser",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:bind"),
    ),
    "POST:/admin/skill-registry/packages": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/packages",
        requested_action="create_skill_package",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    ("POST:/admin/skill-registry/packages/{slug}/versions/validate"): ProtectedSurface(
        surface_key="POST:/admin/skill-registry/packages/{slug}/versions/validate",
        requested_action="validate_skill_package_version",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    "POST:/admin/skill-registry/packages/{slug}/versions": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/packages/{slug}/versions",
        requested_action="publish_skill_package_version",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "POST:/admin/skill-registry/packages/{slug}/versions/{semantic_version}/availability"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/packages/{slug}/versions/"
            "{semantic_version}/availability"
        ),
        requested_action="grant_skill_package_version_availability",
        classification=SurfaceClassification.PLATFORM_ADMIN,
        required_roles=("platform_admin",),
        required_permissions=("skill-registry:publish",),
    ),
    (
        "GET:/admin/skill-registry/tenants/{tenant_id}/available-versions"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/skill-registry/tenants/{tenant_id}/available-versions"
        ),
        requested_action="list_available_skill_package_versions",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    "POST:/admin/skill-registry/installations": ProtectedSurface(
        surface_key="POST:/admin/skill-registry/installations",
        requested_action="install_tenant_skill",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "POST:/admin/skill-registry/installations/{installation_id}/credentials"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/skill-registry/installations/{installation_id}/credentials"
        ),
        requested_action="configure_skill_installation_credentials",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:install"),
    ),
    (
        "GET:/admin/skill-registry/installations/{installation_id}/eligibility"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/skill-registry/installations/{installation_id}/eligibility"
        ),
        requested_action="preview_skill_installation_eligibility",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin", "skill-registry:bind"),
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
    "GET:/admin/workflows/editor-lookups": ProtectedSurface(
        surface_key="GET:/admin/workflows/editor-lookups",
        requested_action="read_workflow_editor_lookups",
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
    "GET:/admin/workflows/drafts/{workflow_draft_id}/graph-preview": ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/graph-preview",
        requested_action="read_workflow_graph_preview",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/workflows/drafts/{workflow_draft_id}/revisions": ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/revisions",
        requested_action="list_workflow_draft_revisions",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/restore": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/restore",
        requested_action="restore_workflow_draft_revision",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/copy": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/copy",
        requested_action="copy_workflow_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/publish-gate": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/publish-gate",
        requested_action="evaluate_workflow_publish_gate",
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
    "GET:/admin/workflows/new": ProtectedSurface(
        surface_key="GET:/admin/workflows/new",
        requested_action="render_workflow_create_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/new": ProtectedSurface(
        surface_key="POST:/admin/workflows/new",
        requested_action="create_workflow_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    ("GET:/admin/workflows/drafts/{workflow_draft_id}/editor"): ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/editor",
        requested_action="render_workflow_draft_editor_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/save-ui": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/save-ui",
        requested_action="save_workflow_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/validate/ui": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/validate/ui",
        requested_action="validate_workflow_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    ("GET:/admin/workflows/drafts/{workflow_draft_id}/revisions/ui"): ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/revisions/ui",
        requested_action="render_workflow_revision_history_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/restore/ui": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/restore/ui",
        requested_action="restore_workflow_draft_revision_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/copy/ui": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/copy/ui",
        requested_action="copy_workflow_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui"
    ): ProtectedSurface(
        surface_key="GET:/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui",
        requested_action="render_workflow_publish_gate_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/workflows/drafts/{workflow_draft_id}/publish/ui": ProtectedSurface(
        surface_key="POST:/admin/workflows/drafts/{workflow_draft_id}/publish/ui",
        requested_action="publish_workflow_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/workflows/versions/{workflow_version_bundle_id}/detail"
    ): ProtectedSurface(
        surface_key="GET:/admin/workflows/versions/{workflow_version_bundle_id}/detail",
        requested_action="render_workflow_version_detail_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin": ProtectedSurface(
        surface_key="GET:/admin",
        requested_action="render_admin_console_shell",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/scope": ProtectedSurface(
        surface_key="GET:/admin/scope",
        requested_action="select_admin_console_scope",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/filters/{admin_area}": ProtectedSurface(
        surface_key="GET:/admin/filters/{admin_area}",
        requested_action="list_admin_saved_filters",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/filters/{admin_area}": ProtectedSurface(
        surface_key="POST:/admin/filters/{admin_area}",
        requested_action="save_admin_saved_filter",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/filters/{admin_area}/{filter_id}/restore": ProtectedSurface(
        surface_key="GET:/admin/filters/{admin_area}/{filter_id}/restore",
        requested_action="restore_admin_saved_filter",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/filters/{admin_area}/{filter_id}": ProtectedSurface(
        surface_key="POST:/admin/filters/{admin_area}/{filter_id}",
        requested_action="delete_admin_saved_filter",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "DELETE:/admin/filters/{admin_area}/{filter_id}": ProtectedSurface(
        surface_key="DELETE:/admin/filters/{admin_area}/{filter_id}",
        requested_action="delete_admin_saved_filter",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/config/ui": ProtectedSurface(
        surface_key="GET:/admin/config/ui",
        requested_action="render_model_skill_config_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/config/ui/history": ProtectedSurface(
        surface_key="GET:/admin/config/ui/history",
        requested_action="render_model_skill_config_history_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/config/ui/runs/{workflow_run_id}/provenance": ProtectedSurface(
        surface_key="GET:/admin/config/ui/runs/{workflow_run_id}/provenance",
        requested_action="render_model_skill_run_provenance_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/model-providers": ProtectedSurface(
        surface_key="GET:/admin/model-providers",
        requested_action="render_model_provider_connections_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/model-providers/new": ProtectedSurface(
        surface_key="GET:/admin/model-providers/new",
        requested_action="render_model_provider_create_ui",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "GET:/admin/model-providers/{connection_id}": ProtectedSurface(
        surface_key="GET:/admin/model-providers/{connection_id}",
        requested_action="render_model_provider_detail_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/model-providers/{connection_id}/edit": ProtectedSurface(
        surface_key="GET:/admin/model-providers/{connection_id}/edit",
        requested_action="render_model_provider_edit_ui",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "GET:/admin/model-providers/catalog": ProtectedSurface(
        surface_key="GET:/admin/model-providers/catalog",
        requested_action="render_model_provider_catalog_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/prompts": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts",
        requested_action="render_prompt_library_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/prompts/new": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts/new",
        requested_action="render_prompt_create_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit",
        requested_action="render_prompt_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/prompt-runtime/prompts/form": ProtectedSurface(
        surface_key="POST:/admin/prompt-runtime/prompts/form",
        requested_action="submit_prompt_library_form",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/prompt-runtime/prompts/versions/{prompt_version_id}"
    ): ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts/versions/{prompt_version_id}",
        requested_action="render_prompt_version_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/history": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/history",
        requested_action="render_prompt_history_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview",
        requested_action="render_prompt_preview_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/api/prompts": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/api/prompts",
        requested_action="list_prompt_lineages",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/prompt-runtime/api/prompts": ProtectedSurface(
        surface_key="POST:/admin/prompt-runtime/api/prompts",
        requested_action="create_prompt_lineage",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft",
        requested_action="read_prompt_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "PUT:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft": ProtectedSurface(
        surface_key="PUT:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft",
        requested_action="save_prompt_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate"
        ),
        requested_action="validate_prompt_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview"
        ),
        requested_action="preview_prompt_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish"
        ),
        requested_action="publish_prompt_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/retire"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/retire"
        ),
        requested_action="retire_prompt_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants"
        ),
        requested_action="grant_prompt_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/profiles": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/profiles",
        requested_action="render_agent_profiles_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/profiles/new": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/profiles/new",
        requested_action="render_agent_profile_create_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/edit"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/edit"
        ),
        requested_action="render_agent_profile_draft_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/prompt-runtime/profiles/versions/{agent_profile_version_id}"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/prompt-runtime/profiles/versions/{agent_profile_version_id}"
        ),
        requested_action="render_agent_profile_version_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "GET:/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/history"
    ): ProtectedSurface(
        surface_key=(
            "GET:/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/history"
        ),
        requested_action="render_agent_profile_history_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/profiles/resolve": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/profiles/resolve",
        requested_action="render_agent_profile_resolution_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/prompt-runtime/profiles/form": ProtectedSurface(
        surface_key="POST:/admin/prompt-runtime/profiles/form",
        requested_action="submit_agent_profile_form",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/api/profiles": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/api/profiles",
        requested_action="list_agent_profiles",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/prompt-runtime/api/profiles": ProtectedSurface(
        surface_key="POST:/admin/prompt-runtime/api/profiles",
        requested_action="create_agent_profile",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "PUT:/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft"
    ): ProtectedSurface(
        surface_key=(
            "PUT:/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft"
        ),
        requested_action="save_agent_profile_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/validate"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/profiles/"
            "{agent_runtime_profile_id}/validate"
        ),
        requested_action="validate_agent_profile_draft",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/activate"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/profiles/"
            "{agent_runtime_profile_id}/activate"
        ),
        requested_action="activate_agent_profile",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/profiles/versions/"
        "{agent_profile_version_id}/retire"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/profiles/versions/"
            "{agent_profile_version_id}/retire"
        ),
        requested_action="retire_agent_profile_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    (
        "POST:/admin/prompt-runtime/api/profiles/versions/"
        "{agent_profile_version_id}/grants"
    ): ProtectedSurface(
        surface_key=(
            "POST:/admin/prompt-runtime/api/profiles/versions/"
            "{agent_profile_version_id}/grants"
        ),
        requested_action="grant_agent_profile_version",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/prompt-runtime/api/resolve-profile": ProtectedSurface(
        surface_key="POST:/admin/prompt-runtime/api/resolve-profile",
        requested_action="resolve_agent_profile",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/prompt-runtime/api/history": ProtectedSurface(
        surface_key="GET:/admin/prompt-runtime/api/history",
        requested_action="list_prompt_runtime_history",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/model-providers": ProtectedSurface(
        surface_key="POST:/admin/model-providers",
        requested_action="create_model_provider_connection",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "GET:/admin/model-providers/api/connections": ProtectedSurface(
        surface_key="GET:/admin/model-providers/api/connections",
        requested_action="list_model_provider_connections",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "POST:/admin/model-providers/api/connections": ProtectedSurface(
        surface_key="POST:/admin/model-providers/api/connections",
        requested_action="create_model_provider_connection_api",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "PUT:/admin/model-providers/api/connections/{connection_id}": ProtectedSurface(
        surface_key="PUT:/admin/model-providers/api/connections/{connection_id}",
        requested_action="update_model_provider_connection_api",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "POST:/admin/model-providers/{connection_id}": ProtectedSurface(
        surface_key="POST:/admin/model-providers/{connection_id}",
        requested_action="update_model_provider_connection",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "POST:/admin/model-providers/{connection_id}/activate": ProtectedSurface(
        surface_key="POST:/admin/model-providers/{connection_id}/activate",
        requested_action="activate_model_provider_connection",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "POST:/admin/model-providers/{connection_id}/deactivate": ProtectedSurface(
        surface_key="POST:/admin/model-providers/{connection_id}/deactivate",
        requested_action="deactivate_model_provider_connection",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "POST:/admin/model-providers/{connection_id}/test": ProtectedSurface(
        surface_key="POST:/admin/model-providers/{connection_id}/test",
        requested_action="test_model_provider_connection",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "POST:/admin/model-providers/{connection_id}/sync-catalog": ProtectedSurface(
        surface_key="POST:/admin/model-providers/{connection_id}/sync-catalog",
        requested_action="sync_model_provider_catalog",
        classification=SurfaceClassification.PLATFORM_ADMIN,
    ),
    "GET:/admin/runs": ProtectedSurface(
        surface_key="GET:/admin/runs",
        requested_action="render_run_inspection_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/runs/{workflow_run_id}": ProtectedSurface(
        surface_key="GET:/admin/runs/{workflow_run_id}",
        requested_action="render_run_detail_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/runs/{workflow_run_id}/replay": ProtectedSurface(
        surface_key="GET:/admin/runs/{workflow_run_id}/replay",
        requested_action="render_run_replay_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/reliability/ui/": ProtectedSurface(
        surface_key="GET:/admin/reliability/ui/",
        requested_action="render_reliability_dashboard_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/reliability/ui/breakers": ProtectedSurface(
        surface_key="GET:/admin/reliability/ui/breakers",
        requested_action="render_reliability_breakers_ui",
        classification=SurfaceClassification.AUTHENTICATED,
    ),
    "GET:/admin/reliability/ui/dead-letters": ProtectedSurface(
        surface_key="GET:/admin/reliability/ui/dead-letters",
        requested_action="render_reliability_dead_letters_ui",
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
