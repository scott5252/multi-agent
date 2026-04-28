from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.agents.resolution import (
    AgentProfileCandidate,
    AgentProfileResolutionError,
    resolve_agent_profile,
)


def test_profile_resolution_prefers_tenant_profile_over_platform_fallback() -> None:
    tenant_id = uuid4()
    platform = AgentProfileCandidate(
        agent_profile_version_id=uuid4(),
        scope_type="platform",
        tenant_id=None,
        agent_key="planner",
        agent_kind="agent",
        status="active",
        granted_tenant_ids=(tenant_id,),
    )
    tenant = AgentProfileCandidate(
        agent_profile_version_id=uuid4(),
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
        status="active",
        granted_tenant_ids=(),
    )

    result = resolve_agent_profile(
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
        candidates=(platform, tenant),
    )

    assert result.selected_profile_version_id == tenant.agent_profile_version_id
    assert result.source_scope == "tenant"


def test_profile_resolution_blocks_missing_profile() -> None:
    with pytest.raises(AgentProfileResolutionError, match="no active profile"):
        resolve_agent_profile(
            tenant_id=uuid4(),
            agent_key="planner",
            agent_kind="agent",
            candidates=(),
        )


def test_profile_resolution_blocks_conflicting_tenant_profiles() -> None:
    tenant_id = uuid4()

    with pytest.raises(AgentProfileResolutionError, match="multiple active tenant"):
        resolve_agent_profile(
            tenant_id=tenant_id,
            agent_key="planner",
            agent_kind="agent",
            candidates=(
                AgentProfileCandidate(
                    agent_profile_version_id=uuid4(),
                    scope_type="tenant",
                    tenant_id=tenant_id,
                    agent_key="planner",
                    agent_kind="agent",
                    status="active",
                    granted_tenant_ids=(),
                ),
                AgentProfileCandidate(
                    agent_profile_version_id=uuid4(),
                    scope_type="tenant",
                    tenant_id=tenant_id,
                    agent_key="planner",
                    agent_kind="agent",
                    status="active",
                    granted_tenant_ids=(),
                ),
            ),
        )
