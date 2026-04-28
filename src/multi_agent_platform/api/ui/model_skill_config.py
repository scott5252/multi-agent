from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.api.schemas.model_skill_config import (
    HistoryResponse,
    RunProvenanceResponse,
)
from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles


@dataclass(frozen=True, slots=True)
class ModelRoutingPageModel:
    title: str
    missing_default: bool
    preview_action: str = "/admin/config/preview/model"
    tool_preview_action: str = "/admin/config/preview/tool"
    history_href: str = "/admin/config/ui/history"
    skills_tools_filters: tuple[str, ...] = (
        "tenant",
        "workflow",
        "agent",
        "step",
        "skill",
        "tool",
        "action",
        "status",
    )
    policy_create_actions: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class ModelSkillHistoryPageModel:
    title: str
    history: HistoryResponse


@dataclass(frozen=True, slots=True)
class RunProvenancePageModel:
    title: str
    provenance: RunProvenanceResponse


def build_model_routing_page_model(*, missing_default: bool) -> ModelRoutingPageModel:
    return ModelRoutingPageModel(
        title="Model Routing",
        missing_default=missing_default,
        policy_create_actions={
            "skill_binding": "/admin/config/skill-bindings",
            "tool_policy": "/admin/config/tool-policies",
            "outbound_policy": "/admin/config/outbound-domain-policies",
            "secret_reference": "/admin/config/secret-references",
            "credential_requirement": "/admin/config/credential-requirements",
        },
    )


def build_history_page_model(history: HistoryResponse) -> ModelSkillHistoryPageModel:
    return ModelSkillHistoryPageModel(title="Configuration History", history=history)


def build_run_provenance_page_model(
    provenance: RunProvenanceResponse,
) -> RunProvenancePageModel:
    return RunProvenancePageModel(title="Run Provenance", provenance=provenance)


def model_skill_history_filter_profile() -> FilterProfile:
    return filter_profiles()["model_skill_history"]
