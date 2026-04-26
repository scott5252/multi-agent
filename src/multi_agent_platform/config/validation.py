from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from uuid import UUID

from multi_agent_platform.config.model_skill import (
    ConfigKind,
    ModelProviderSummary,
    ModelSkillErrorCategory,
    PromptReferenceCandidate,
    ScopeSelector,
    ScopeType,
)

SECRET_LIKE_PATTERN = re.compile(
    r"(-----BEGIN|sk-[A-Za-z0-9]|AKIA[0-9A-Z]{16}|password\s*=|api[_-]?key\s*=)",
    re.IGNORECASE,
)


class ModelSkillValidationError(ValueError):
    def __init__(
        self,
        category: ModelSkillErrorCategory,
        message: str,
        *,
        safe_identifiers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.safe_identifiers = dict(safe_identifiers or {})


def require_reason(reason: str | None) -> str:
    normalized = (reason or "").strip()
    if not normalized:
        raise ModelSkillValidationError(
            ModelSkillErrorCategory.VALIDATION_FAILED,
            "a non-empty reason is required",
        )
    return normalized


def validate_scope_for_kind(kind: ConfigKind, scope: ScopeSelector) -> None:
    if (
        kind is ConfigKind.PROMPT_REFERENCE
        and scope.scope_type is ScopeType.TENANT_DEFAULT
    ):
        raise ModelSkillValidationError(
            ModelSkillErrorCategory.MISSING_PROMPT_VERSION,
            "prompt references must be scoped to workflow, agent, or step",
        )
    if scope.step_key and not (scope.agent_key or scope.workflow_lineage_id):
        raise ModelSkillValidationError(
            ModelSkillErrorCategory.VALIDATION_FAILED,
            "step scoped configuration must include an agent or workflow selector",
        )


def assert_no_raw_secret(value: object, *, path: str = "payload") -> None:
    if isinstance(value, str):
        if SECRET_LIKE_PATTERN.search(value):
            raise ModelSkillValidationError(
                ModelSkillErrorCategory.SECRET_REFERENCE_INVALID,
                f"raw secret-like value is not allowed at {path}",
            )
        return
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            lowered = str(key).lower()
            if lowered in {"secret", "password", "token", "api_key", "apikey"}:
                raise ModelSkillValidationError(
                    ModelSkillErrorCategory.SECRET_REFERENCE_INVALID,
                    f"raw credential field is not allowed at {path}.{key}",
                )
            assert_no_raw_secret(nested_value, path=f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for index, nested_value in enumerate(value):
            assert_no_raw_secret(nested_value, path=f"{path}[{index}]")


def validate_model_reference(
    *,
    provider_key: str,
    model_id: str,
    tenant_id: UUID,
    providers: Sequence[ModelProviderSummary],
) -> ModelProviderSummary:
    for provider in providers:
        if (
            provider.provider_key == provider_key
            and provider.model_id == model_id
            and provider.tenant_id in (None, tenant_id)
            and provider.status.value == "active"
        ):
            return provider
    raise ModelSkillValidationError(
        ModelSkillErrorCategory.INVALID_MODEL_REFERENCE,
        "model provider entry is inactive, unavailable, or unknown",
        safe_identifiers={"provider_key": provider_key, "model_id": model_id},
    )


def validate_publish_time_model_skill_config(
    *,
    has_model_backed_steps: bool,
    has_global_default: bool,
    prompt_references: Sequence[PromptReferenceCandidate],
    required_skills: Sequence[str] = (),
    bound_skills: Sequence[str] = (),
    required_tools: Sequence[str] = (),
    allowed_tools: Sequence[str] = (),
) -> list[ModelSkillValidationError]:
    errors: list[ModelSkillValidationError] = []
    if has_model_backed_steps and not has_global_default:
        errors.append(
            ModelSkillValidationError(
                ModelSkillErrorCategory.MISSING_GLOBAL_DEFAULT,
                "tenant global default model is required",
            )
        )
    if has_model_backed_steps and not prompt_references:
        errors.append(
            ModelSkillValidationError(
                ModelSkillErrorCategory.MISSING_PROMPT_VERSION,
                "at least one workflow, agent, or step prompt reference is required",
            )
        )
    missing_skills = sorted(set(required_skills) - set(bound_skills))
    if missing_skills:
        errors.append(
            ModelSkillValidationError(
                ModelSkillErrorCategory.SKILL_NOT_BOUND,
                "workflow references unbound skills",
                safe_identifiers={"skills": ",".join(missing_skills)},
            )
        )
    missing_tools = sorted(set(required_tools) - set(allowed_tools))
    if missing_tools:
        errors.append(
            ModelSkillValidationError(
                ModelSkillErrorCategory.TOOL_DENIED,
                "workflow references tools without allow policies",
                safe_identifiers={"tools": ",".join(missing_tools)},
            )
        )
    return errors
