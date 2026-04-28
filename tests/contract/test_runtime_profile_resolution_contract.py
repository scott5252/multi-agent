from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.agents.resolution import (
    AgentProfileCandidate,
    resolve_agent_profile,
)


def test_resolution_prefers_tenant_over_granted_platform() -> None:
    tenant_id = uuid4()
    tenant_profile = uuid4()
    platform_profile = uuid4()

    resolution = resolve_agent_profile(
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
        candidates=(
            AgentProfileCandidate(
                agent_profile_version_id=platform_profile,
                scope_type="platform",
                tenant_id=None,
                agent_key="planner",
                agent_kind="agent",
                status="active",
                granted_tenant_ids=(tenant_id,),
            ),
            AgentProfileCandidate(
                agent_profile_version_id=tenant_profile,
                scope_type="tenant",
                tenant_id=tenant_id,
                agent_key="planner",
                agent_kind="agent",
                status="active",
                granted_tenant_ids=(),
            ),
        ),
    )

    assert resolution.selected_profile_version_id == tenant_profile
    assert resolution.source_scope == "tenant"
