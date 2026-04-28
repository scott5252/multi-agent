from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AgentProfileUiSection:
    key: str
    label: str
    blocking_count: int = 0


@dataclass(frozen=True, slots=True)
class AgentProfileUiModel:
    title: str
    scope_type: str
    tenant_id: UUID | None = None
    agent_runtime_profile_id: UUID | None = None
    agent_profile_version_id: UUID | None = None
    agent_key: str = ""
    agent_kind: str = "agent"
    can_activate: bool = False
    can_retire: bool = False
    sections: tuple[AgentProfileUiSection, ...] = field(default_factory=tuple)
    submitted_fields: dict[str, object] = field(default_factory=dict)


def build_agent_profile_ui_model(
    *,
    title: str,
    scope_type: str,
    tenant_id: UUID | None = None,
    agent_runtime_profile_id: UUID | None = None,
    agent_profile_version_id: UUID | None = None,
    agent_key: str = "",
    agent_kind: str = "agent",
    validation_status: str | None = None,
    status: str = "draft",
    findings: list[dict[str, object]] | None = None,
    submitted_fields: dict[str, object] | None = None,
) -> AgentProfileUiModel:
    blocking_by_section: dict[str, int] = {}
    for finding in findings or []:
        if finding.get("severity") != "blocking":
            continue
        section = str(finding.get("section", "profile"))
        blocking_by_section[section] = blocking_by_section.get(section, 0) + 1
    section_labels = {
        "prompt_references": "Prompt References",
        "model_routing_hints": "Model Routing",
        "memory_scope_policy": "Memory Policy",
        "skill_requirements": "Skills",
        "tool_policy_expectations": "Tools",
        "output_contract_expectations": "Output Contract",
        "test_suite_requirements": "Tests",
    }
    sections = tuple(
        AgentProfileUiSection(
            key=key,
            label=label,
            blocking_count=blocking_by_section.get(key, 0),
        )
        for key, label in section_labels.items()
    )
    return AgentProfileUiModel(
        title=title,
        scope_type=scope_type,
        tenant_id=tenant_id,
        agent_runtime_profile_id=agent_runtime_profile_id,
        agent_profile_version_id=agent_profile_version_id,
        agent_key=agent_key,
        agent_kind=agent_kind,
        can_activate=validation_status == "passed" and status == "draft",
        can_retire=status == "active",
        sections=sections,
        submitted_fields=submitted_fields or {},
    )
