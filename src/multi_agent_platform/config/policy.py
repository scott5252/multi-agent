from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from urllib.parse import urlparse

from multi_agent_platform.config.model_skill import (
    CredentialRequirementCandidate,
    ModelSkillErrorCategory,
    OutboundPolicyCandidate,
    PolicyOutcome,
    ScopeSelector,
    SecretReferenceCandidate,
    SkillBindingCandidate,
    ToolPolicyCandidate,
    VersionedRecord,
    VersionStatus,
)


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    outcome: PolicyOutcome
    denial_category: ModelSkillErrorCategory | None
    safe_reason: str
    evaluated_version_ids: tuple[object, ...]
    winning_version_ids: tuple[object, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.outcome is PolicyOutcome.ALLOW


def _applicable[VersionedT: VersionedRecord](
    candidates: Sequence[VersionedT], scope: ScopeSelector
) -> list[VersionedT]:
    return [
        candidate
        for candidate in candidates
        if candidate.status is VersionStatus.ACTIVE and candidate.scope.contains(scope)
    ]


def evaluate_skill_access(
    *,
    candidates: list[SkillBindingCandidate],
    scope: ScopeSelector,
    skill_slug: str,
    skill_version: str,
    use_context: str,
) -> PolicyDecision:
    applicable = [
        candidate
        for candidate in _applicable(candidates, scope)
        if candidate.skill_slug == skill_slug
        and candidate.skill_version == skill_version
    ]
    if not applicable:
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.SKILL_NOT_BOUND,
            safe_reason="no active exact skill binding matched",
            evaluated_version_ids=(),
        )
    denied = [
        candidate
        for candidate in applicable
        if candidate.allowed_contexts and use_context not in candidate.allowed_contexts
    ]
    if denied:
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.SKILL_NOT_BOUND,
            safe_reason="skill binding does not allow this use context",
            evaluated_version_ids=tuple(
                candidate.version_id for candidate in applicable
            ),
        )
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="skill binding allowed",
        evaluated_version_ids=tuple(candidate.version_id for candidate in applicable),
        winning_version_ids=tuple(candidate.version_id for candidate in applicable),
    )


def evaluate_tool_policy(
    *,
    candidates: list[ToolPolicyCandidate],
    scope: ScopeSelector,
    skill_slug: str | None,
    tool_id: str,
    action_category: str,
) -> PolicyDecision:
    applicable = [
        candidate
        for candidate in _applicable(candidates, scope)
        if candidate.tool_id == tool_id
        and (candidate.skill_slug is None or candidate.skill_slug == skill_slug)
    ]
    if not applicable:
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.TOOL_DENIED,
            safe_reason="no active tool allow policy matched",
            evaluated_version_ids=(),
        )
    denied = [
        candidate
        for candidate in applicable
        if action_category not in candidate.allowed_action_categories
    ]
    if denied:
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.TOOL_DENIED,
            safe_reason="an applicable tool policy does not allow the action",
            evaluated_version_ids=tuple(
                candidate.version_id for candidate in applicable
            ),
        )
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="all applicable tool policies allowed",
        evaluated_version_ids=tuple(candidate.version_id for candidate in applicable),
        winning_version_ids=tuple(candidate.version_id for candidate in applicable),
    )


def _normalize_destination(destination_url: str) -> tuple[str, str, int | None] | str:
    parsed = urlparse(destination_url)
    if parsed.username or parsed.password:
        return "embedded credentials are not allowed"
    if not parsed.scheme or not parsed.hostname:
        return "destination must include scheme and host"
    try:
        host = parsed.hostname.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return "destination host is malformed"
    return parsed.scheme.lower(), host, parsed.port


def _domain_matches(pattern: str, host: str) -> bool:
    normalized = pattern.encode("idna").decode("ascii").lower()
    if normalized.startswith("*."):
        suffix = normalized[2:]
        return host.endswith(f".{suffix}") and host != suffix
    return host == normalized


def evaluate_outbound_policy(
    *,
    candidates: list[OutboundPolicyCandidate],
    scope: ScopeSelector,
    tool_id: str,
    action_category: str,
    destination_url: str,
) -> PolicyDecision:
    normalized = _normalize_destination(destination_url)
    if isinstance(normalized, str):
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.DOMAIN_DENIED,
            safe_reason=normalized,
            evaluated_version_ids=(),
        )
    scheme, host, port = normalized
    applicable = [
        candidate
        for candidate in _applicable(candidates, scope)
        if candidate.tool_id == tool_id
        and (
            candidate.action_category is None
            or candidate.action_category == action_category
        )
    ]
    if not applicable:
        return PolicyDecision(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.DOMAIN_DENIED,
            safe_reason="no active outbound domain policy matched",
            evaluated_version_ids=(),
        )
    for candidate in applicable:
        if candidate.allowed_schemes and scheme not in candidate.allowed_schemes:
            return PolicyDecision(
                outcome=PolicyOutcome.DENY,
                denial_category=ModelSkillErrorCategory.DOMAIN_DENIED,
                safe_reason="scheme denied by outbound policy",
                evaluated_version_ids=tuple(policy.version_id for policy in applicable),
            )
        if candidate.allowed_ports and port not in candidate.allowed_ports:
            return PolicyDecision(
                outcome=PolicyOutcome.DENY,
                denial_category=ModelSkillErrorCategory.DOMAIN_DENIED,
                safe_reason="port denied by outbound policy",
                evaluated_version_ids=tuple(policy.version_id for policy in applicable),
            )
        if not any(
            _domain_matches(pattern, host)
            for pattern in candidate.allowed_domain_patterns
        ):
            return PolicyDecision(
                outcome=PolicyOutcome.DENY,
                denial_category=ModelSkillErrorCategory.DOMAIN_DENIED,
                safe_reason="host denied by outbound policy",
                evaluated_version_ids=tuple(policy.version_id for policy in applicable),
            )
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="all applicable outbound policies allowed",
        evaluated_version_ids=tuple(candidate.version_id for candidate in applicable),
        winning_version_ids=tuple(candidate.version_id for candidate in applicable),
    )


def evaluate_credential_requirements(
    *,
    requirements: list[CredentialRequirementCandidate],
    secret_references: list[SecretReferenceCandidate],
    scope: ScopeSelector,
    tool_id: str,
    action_category: str,
) -> PolicyDecision:
    applicable = [
        candidate
        for candidate in _applicable(requirements, scope)
        if candidate.tool_id == tool_id
        and (
            candidate.action_category is None
            or candidate.action_category == action_category
        )
    ]
    if not applicable:
        return PolicyDecision(
            outcome=PolicyOutcome.ALLOW,
            denial_category=None,
            safe_reason="no credential requirement applies",
            evaluated_version_ids=(),
        )
    active_secret_ids = {
        secret.version_id
        for secret in secret_references
        if secret.status is VersionStatus.ACTIVE and secret.scope.contains(scope)
    }
    for requirement in applicable:
        if (
            requirement.credential_kind == "secret_reference"
            and requirement.secret_reference_version_id not in active_secret_ids
        ):
            return PolicyDecision(
                outcome=PolicyOutcome.DENY,
                denial_category=ModelSkillErrorCategory.CREDENTIAL_UNSATISFIED,
                safe_reason="required secret reference is missing or inactive",
                evaluated_version_ids=tuple(item.version_id for item in applicable),
            )
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="credential requirements satisfied",
        evaluated_version_ids=tuple(item.version_id for item in applicable),
        winning_version_ids=tuple(item.version_id for item in applicable),
    )
