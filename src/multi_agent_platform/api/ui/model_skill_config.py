from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.api.schemas.model_skill_config import (
    HistoryResponse,
    RunProvenanceResponse,
)


@dataclass(frozen=True, slots=True)
class ModelRoutingPageModel:
    title: str
    missing_default: bool
    preview_action: str = "/admin/config/preview/model"
    history_href: str = "/admin/config/model-routing/history"


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
    )


def build_history_page_model(history: HistoryResponse) -> ModelSkillHistoryPageModel:
    return ModelSkillHistoryPageModel(title="Configuration History", history=history)


def build_run_provenance_page_model(
    provenance: RunProvenanceResponse,
) -> RunProvenancePageModel:
    return RunProvenancePageModel(title="Run Provenance", provenance=provenance)
