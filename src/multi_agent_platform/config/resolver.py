from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.config.model_skill import (
    ModelRoutingCandidate,
    ModelSkillErrorCategory,
    PromptReferenceCandidate,
    ScopeSelector,
    ScopeType,
    VersionStatus,
)


class ResolutionError(RuntimeError):
    def __init__(self, category: ModelSkillErrorCategory, message: str) -> None:
        super().__init__(message)
        self.category = category


@dataclass(frozen=True, slots=True)
class ModelResolution:
    model_routing_version_id: UUID
    provider_key: str
    model_id: str
    model_provider_entry_id: UUID
    source_scope: ScopeType
    routing_parameters: dict[str, object]
    considered_version_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class PromptResolution:
    prompt_reference_version_id: UUID
    prompt_id: UUID
    prompt_version_id: UUID
    prompt_digest: str
    source_scope: ScopeType
    considered_version_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class ModelPromptResolution:
    model: ModelResolution
    prompt: PromptResolution


def _active_applicable_model_candidates(
    candidates: list[ModelRoutingCandidate], request_scope: ScopeSelector
) -> list[ModelRoutingCandidate]:
    applicable = [
        candidate
        for candidate in candidates
        if candidate.status is VersionStatus.ACTIVE
        and candidate.scope.contains(request_scope)
    ]
    return sorted(
        applicable,
        key=lambda candidate: (
            candidate.scope.specificity(),
            candidate.version_sequence,
            str(candidate.version_id),
        ),
        reverse=True,
    )


def resolve_model(
    candidates: list[ModelRoutingCandidate], request_scope: ScopeSelector
) -> ModelResolution:
    ordered = _active_applicable_model_candidates(candidates, request_scope)
    if not ordered:
        raise ResolutionError(
            ModelSkillErrorCategory.MISSING_GLOBAL_DEFAULT,
            "no active model routing candidate matched and no tenant default exists",
        )
    winner = ordered[0]
    tied = [
        candidate
        for candidate in ordered
        if candidate.scope.specificity() == winner.scope.specificity()
        and candidate.scope.scope_hash() == winner.scope.scope_hash()
        and candidate.version_id != winner.version_id
    ]
    if tied:
        raise ResolutionError(
            ModelSkillErrorCategory.RESOLUTION_CONFLICT,
            "more than one active model candidate matched the same specificity",
        )
    return ModelResolution(
        model_routing_version_id=winner.version_id,
        provider_key=winner.provider_key,
        model_id=winner.model_id,
        model_provider_entry_id=winner.model_provider_entry_id,
        source_scope=winner.scope.scope_type,
        routing_parameters=dict(winner.routing_parameters),
        considered_version_ids=tuple(candidate.version_id for candidate in ordered),
    )


def resolve_prompt(
    candidates: list[PromptReferenceCandidate], request_scope: ScopeSelector
) -> PromptResolution:
    applicable = [
        candidate
        for candidate in candidates
        if candidate.status is VersionStatus.ACTIVE
        and candidate.scope.scope_type is not ScopeType.TENANT_DEFAULT
        and candidate.scope.contains(request_scope)
    ]
    ordered = sorted(
        applicable,
        key=lambda candidate: (
            candidate.scope.specificity(),
            candidate.version_sequence,
            str(candidate.version_id),
        ),
        reverse=True,
    )
    if not ordered:
        raise ResolutionError(
            ModelSkillErrorCategory.MISSING_PROMPT_VERSION,
            "no workflow, agent, or step prompt reference matched",
        )
    winner = ordered[0]
    tied = [
        candidate
        for candidate in ordered
        if candidate.scope.specificity() == winner.scope.specificity()
        and candidate.scope.scope_hash() == winner.scope.scope_hash()
        and candidate.version_id != winner.version_id
    ]
    if tied:
        raise ResolutionError(
            ModelSkillErrorCategory.RESOLUTION_CONFLICT,
            "more than one active prompt candidate matched the same specificity",
        )
    return PromptResolution(
        prompt_reference_version_id=winner.version_id,
        prompt_id=winner.prompt_id,
        prompt_version_id=winner.prompt_version_id,
        prompt_digest=winner.prompt_digest,
        source_scope=winner.scope.scope_type,
        considered_version_ids=tuple(candidate.version_id for candidate in ordered),
    )


def resolve_model_prompt(
    *,
    model_candidates: list[ModelRoutingCandidate],
    prompt_candidates: list[PromptReferenceCandidate],
    request_scope: ScopeSelector,
) -> ModelPromptResolution:
    return ModelPromptResolution(
        model=resolve_model(model_candidates, request_scope),
        prompt=resolve_prompt(prompt_candidates, request_scope),
    )
