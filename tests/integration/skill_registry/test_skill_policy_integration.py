from __future__ import annotations

from multi_agent_platform.config.model_skill import installed_skill_binding_constraints


def test_model_skill_binding_constraints_pin_installation_evidence() -> None:
    constraints = installed_skill_binding_constraints(
        installation_id="install-1",
        installation_version=2,
        package_slug="calendar-assistant",
        semantic_version="1.2.3",
        manifest_digest="sha256:manifest",
        artifact_digest="sha256:artifact",
    )

    assert constraints["source"] == "skill_registry"
    assert constraints["installation_version"] == 2
