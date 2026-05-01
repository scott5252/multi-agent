from __future__ import annotations

from multi_agent_platform.auth.local_principals import skill_registry_permission_codes
from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_skill_registry_surface_policies_are_registered() -> None:
    expected_surfaces = {
        "GET:/admin/skill-registry/ui/packages",
        "GET:/admin/skill-registry/ui/packages/new",
        "POST:/admin/skill-registry/ui/packages",
        "GET:/admin/skill-registry/ui/packages/{slug}",
        "GET:/admin/skill-registry/ui/packages/{slug}/candidate",
        "POST:/admin/skill-registry/ui/packages/{slug}/candidate",
        "POST:/admin/skill-registry/ui/packages/{slug}/candidate/validate",
        "POST:/admin/skill-registry/ui/packages/{slug}/candidate/publish",
        "GET:/admin/skill-registry/ui/packages/{slug}/versions/{semantic_version}",
        (
            "GET:/admin/skill-registry/ui/packages/{slug}/versions/"
            "{semantic_version}/grants"
        ),
        (
            "POST:/admin/skill-registry/ui/packages/{slug}/versions/"
            "{semantic_version}/grants"
        ),
        "GET:/admin/skill-registry/ui/available-versions",
        "GET:/admin/skill-registry/ui/installations",
        "POST:/admin/skill-registry/ui/installations",
        "GET:/admin/skill-registry/ui/installations/{installation_id}",
        "GET:/admin/skill-registry/ui/installations/{installation_id}/credentials",
        "POST:/admin/skill-registry/ui/installations/{installation_id}/credentials",
        "POST:/admin/skill-registry/ui/installations/{installation_id}/smoke-tests",
        (
            "POST:/admin/skill-registry/ui/installations/{installation_id}/"
            "eligibility-preview"
        ),
        "POST:/admin/skill-registry/packages",
        "POST:/admin/skill-registry/packages/{slug}/versions/validate",
        "POST:/admin/skill-registry/packages/{slug}/versions",
        (
            "POST:/admin/skill-registry/packages/{slug}/versions/"
            "{semantic_version}/availability"
        ),
        "GET:/admin/skill-registry/tenants/{tenant_id}/available-versions",
        "POST:/admin/skill-registry/installations",
        "POST:/admin/skill-registry/installations/{installation_id}/credentials",
        "GET:/admin/skill-registry/installations/{installation_id}/eligibility",
    }

    assert expected_surfaces.issubset(SURFACE_POLICIES)


def test_local_principal_skill_registry_grants_include_install_permission() -> None:
    assert "skill-registry:install" in skill_registry_permission_codes(platform=False)
