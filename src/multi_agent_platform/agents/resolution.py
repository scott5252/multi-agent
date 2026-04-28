from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


class AgentProfileResolutionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AgentProfileCandidate:
    agent_profile_version_id: UUID
    scope_type: str
    tenant_id: UUID | None
    agent_key: str
    agent_kind: str
    status: str
    granted_tenant_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class AgentProfileResolution:
    selected_profile_version_id: UUID
    source_scope: str
    considered_profile_version_ids: tuple[UUID, ...]


def resolve_agent_profile(
    *,
    tenant_id: UUID,
    agent_key: str,
    agent_kind: str,
    candidates: tuple[AgentProfileCandidate, ...],
) -> AgentProfileResolution:
    active = [
        candidate
        for candidate in candidates
        if candidate.status == "active"
        and candidate.agent_key == agent_key
        and candidate.agent_kind == agent_kind
    ]
    tenant_matches = [
        candidate
        for candidate in active
        if candidate.scope_type == "tenant" and candidate.tenant_id == tenant_id
    ]
    if len(tenant_matches) > 1:
        raise AgentProfileResolutionError("multiple active tenant profiles matched")
    if tenant_matches:
        selected = tenant_matches[0]
    else:
        platform_matches = [
            candidate
            for candidate in active
            if candidate.scope_type == "platform"
            and tenant_id in candidate.granted_tenant_ids
        ]
        if len(platform_matches) > 1:
            raise AgentProfileResolutionError(
                "multiple platform fallback profiles matched"
            )
        if not platform_matches:
            raise AgentProfileResolutionError("no active profile matched")
        selected = platform_matches[0]
    return AgentProfileResolution(
        selected_profile_version_id=selected.agent_profile_version_id,
        source_scope=selected.scope_type,
        considered_profile_version_ids=tuple(
            candidate.agent_profile_version_id for candidate in active
        ),
    )
