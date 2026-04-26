from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import UUID

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
from multi_agent_platform.secrets.base import SecretProvider, SecretValue


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


@dataclass(frozen=True, slots=True)
class SecretReferenceAuthorization:
    secret_reference_version_id: UUID
    secret_reference_id: str
    provider_key: str
    external_reference: str
    safe_summary: dict[str, object]


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
    credential_context: Mapping[str, object] | None = None,
    authorized_delegated_credential_link_ids: set[UUID] | None = None,
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
    active_secrets = {
        secret.version_id: secret
        for secret in secret_references
        if secret.is_usable and secret.scope.contains(scope)
    }
    delegated_ids = authorized_delegated_credential_link_ids or set()
    for requirement in applicable:
        if requirement.credential_kind == "secret_reference":
            secret = (
                None
                if requirement.secret_reference_version_id is None
                else active_secrets.get(requirement.secret_reference_version_id)
            )
            if secret is None:
                return PolicyDecision(
                    outcome=PolicyOutcome.DENY,
                    denial_category=ModelSkillErrorCategory.SECRET_REFERENCE_INVALID,
                    safe_reason=(
                        "required secret reference is missing, inactive, revoked, "
                        "expired, or cross-tenant"
                    ),
                    evaluated_version_ids=tuple(item.version_id for item in applicable),
                )
            if not _scope_metadata_allows(
                requirement.allowed_credential_scope, credential_context
            ) or not _scope_metadata_allows(secret.allowed_scopes, credential_context):
                return PolicyDecision(
                    outcome=PolicyOutcome.DENY,
                    denial_category=ModelSkillErrorCategory.CREDENTIAL_UNSATISFIED,
                    safe_reason="credential context is outside the allowed scope",
                    evaluated_version_ids=tuple(item.version_id for item in applicable),
                )
        elif (
            requirement.credential_kind == "delegated_credential"
            and requirement.delegated_credential_link_id not in delegated_ids
        ):
            return PolicyDecision(
                outcome=PolicyOutcome.DENY,
                denial_category=ModelSkillErrorCategory.CREDENTIAL_UNSATISFIED,
                safe_reason="delegated credential is not authorized for this tool",
                evaluated_version_ids=tuple(item.version_id for item in applicable),
            )
        else:
            if requirement.credential_kind not in {
                "secret_reference",
                "delegated_credential",
            }:
                return PolicyDecision(
                    outcome=PolicyOutcome.DENY,
                    denial_category=ModelSkillErrorCategory.CREDENTIAL_UNSATISFIED,
                    safe_reason="unsupported credential requirement kind",
                    evaluated_version_ids=tuple(item.version_id for item in applicable),
                )
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="credential requirements satisfied",
        evaluated_version_ids=tuple(item.version_id for item in applicable),
        winning_version_ids=tuple(item.version_id for item in applicable),
    )


def _scope_metadata_allows(
    allowed_scope: Mapping[str, object],
    credential_context: Mapping[str, object] | None,
) -> bool:
    if not allowed_scope:
        return True
    context = credential_context or {}
    for key, expected in allowed_scope.items():
        if context.get(key) != expected:
            return False
    return True


async def authorize_secret_reference_resolution(
    *,
    secret_provider: SecretProvider,
    secret_reference: SecretReferenceCandidate,
    scope: ScopeSelector,
    credential_context: Mapping[str, object] | None = None,
) -> SecretReferenceAuthorization:
    if not secret_reference.scope.contains(scope) or not secret_reference.is_usable:
        raise ValueError("secret reference is not active for this tenant scope")
    if not _scope_metadata_allows(secret_reference.allowed_scopes, credential_context):
        raise ValueError("secret reference is outside the allowed credential scope")
    value = await secret_provider.resolve(secret_reference.external_reference)
    if not isinstance(value, SecretValue):
        raise TypeError("secret provider returned an invalid secret value")
    return SecretReferenceAuthorization(
        secret_reference_version_id=secret_reference.version_id,
        secret_reference_id=secret_reference.secret_reference_id,
        provider_key=secret_reference.provider_key,
        external_reference=secret_reference.external_reference,
        safe_summary={
            "secret_reference_id": secret_reference.secret_reference_id,
            "provider_key": secret_reference.provider_key,
            "resolved": True,
        },
    )
