from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.agents.resolution import (
    AgentProfileCandidate,
    AgentProfileResolutionError,
    resolve_agent_profile,
)
from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument


@dataclass(frozen=True, slots=True)
class WorkflowPromptProfilePin:
    agent_key: str
    agent_kind: str
    agent_profile_version_id: UUID
    source_scope: str
    prompt_version_ids: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "agent_key": self.agent_key,
            "agent_kind": self.agent_kind,
            "agent_profile_version_id": str(self.agent_profile_version_id),
            "source_scope": self.source_scope,
            "prompt_version_ids": list(self.prompt_version_ids),
        }


@dataclass(frozen=True, slots=True)
class WorkflowPromptProfileValidation:
    findings: tuple[dict[str, str], ...]
    pins: tuple[WorkflowPromptProfilePin, ...]

    @property
    def blocking_issue_count(self) -> int:
        return sum(1 for finding in self.findings if finding["severity"] == "blocking")


def validate_workflow_prompt_profiles(
    *,
    document: WorkflowDraftDocument,
    tenant_id: UUID,
    profile_candidates: tuple[AgentProfileCandidate, ...],
    prompt_versions_by_profile: dict[UUID, tuple[str, ...]] | None = None,
) -> WorkflowPromptProfileValidation:
    prompt_versions_by_profile = prompt_versions_by_profile or {}
    findings: list[dict[str, str]] = []
    pins: list[WorkflowPromptProfilePin] = []
    for index, role in enumerate(document.roles):
        agent_kind = "sub_agent" if role.role_kind.value == "subagent" else "agent"
        try:
            resolution = resolve_agent_profile(
                tenant_id=tenant_id,
                agent_key=role.role_key,
                agent_kind=agent_kind,
                candidates=profile_candidates,
            )
        except AgentProfileResolutionError as exc:
            findings.append(
                {
                    "category": "prompt_runtime_profile",
                    "severity": "blocking",
                    "message": str(exc),
                    "field_path": f"roles[{index}].role_key",
                }
            )
            continue
        pins.append(
            WorkflowPromptProfilePin(
                agent_key=role.role_key,
                agent_kind=agent_kind,
                agent_profile_version_id=resolution.selected_profile_version_id,
                source_scope=resolution.source_scope,
                prompt_version_ids=prompt_versions_by_profile.get(
                    resolution.selected_profile_version_id, ()
                ),
            )
        )
    return WorkflowPromptProfileValidation(findings=tuple(findings), pins=tuple(pins))
