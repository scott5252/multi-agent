from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.reliability.models import (
    PolicyStatus,
    ReliabilityPolicy,
    ReliabilityPolicySettings,
    ReliabilityScopeType,
)


class ReliabilityPolicyValidationError(ValueError):
    pass


@dataclass(slots=True, frozen=True)
class PolicyValidationResult:
    accepted: bool
    override_required: bool
    reasons: tuple[str, ...] = ()


def validate_policy_settings(
    settings: ReliabilityPolicySettings, *, unsafe_override: bool = False
) -> PolicyValidationResult:
    reasons: list[str] = []
    if settings.max_submitted_work < 1:
        reasons.append("max_submitted_work must be positive")
    if settings.max_active_work < 1:
        reasons.append("max_active_work must be positive")
    if settings.max_retry_attempts < 0:
        reasons.append("max_retry_attempts cannot be negative")
    if settings.retry_budget_per_window < settings.max_retry_attempts:
        reasons.append("retry_budget_per_window must cover max_retry_attempts")
    if settings.fairness_weight <= 0:
        reasons.append("fairness_weight must be positive")
    if settings.lease_renewal_seconds >= settings.lease_expiry_seconds:
        reasons.append("lease renewal must be before expiry")
    if settings.artifact_tenant_concurrency > settings.artifact_global_concurrency:
        reasons.append("tenant artifact concurrency cannot exceed global concurrency")

    unsafe_disabled = not all(
        (
            settings.quotas_enabled,
            settings.fairness_enabled,
            settings.recovery_safety_enabled,
            settings.containment_enabled,
        )
    )
    override_required = (
        unsafe_disabled
        and settings.require_override_for_unsafe_changes
        and not unsafe_override
    )
    if override_required:
        reasons.append("unsafe reliability control changes require override")
    return PolicyValidationResult(
        accepted=not reasons,
        override_required=override_required,
        reasons=tuple(reasons),
    )


def ensure_valid_policy(
    policy: ReliabilityPolicy, *, unsafe_override: bool = False
) -> ReliabilityPolicy:
    if policy.policy_version < 1:
        raise ReliabilityPolicyValidationError("policy version must be prospective")
    if policy.status not in set(PolicyStatus):
        raise ReliabilityPolicyValidationError("invalid policy status")
    if policy.scope_type is ReliabilityScopeType.TENANT and policy.tenant_id is None:
        raise ReliabilityPolicyValidationError("tenant scoped policies need tenant_id")
    result = validate_policy_settings(policy.settings, unsafe_override=unsafe_override)
    if not result.accepted:
        raise ReliabilityPolicyValidationError("; ".join(result.reasons))
    return policy


def next_policy_version(current: ReliabilityPolicy | None) -> int:
    return 1 if current is None else current.policy_version + 1
