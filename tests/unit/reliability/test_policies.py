from __future__ import annotations

import pytest

from multi_agent_platform.reliability.models import ReliabilityPolicySettings
from multi_agent_platform.reliability.policies import (
    ReliabilityPolicyValidationError,
    ensure_valid_policy,
    next_policy_version,
    validate_policy_settings,
)


def test_policy_validation_requires_override_for_disabled_safety(
    reliability_policy,
) -> None:
    settings = ReliabilityPolicySettings(quotas_enabled=False)
    result = validate_policy_settings(settings)
    assert result.override_required
    unsafe_policy = reliability_policy.__class__(
        tenant_id=reliability_policy.tenant_id,
        scope_type=reliability_policy.scope_type,
        scope_key=reliability_policy.scope_key,
        settings=settings,
        policy_id=reliability_policy.policy_id,
    )
    with pytest.raises(ReliabilityPolicyValidationError):
        ensure_valid_policy(unsafe_policy)
    assert ensure_valid_policy(unsafe_policy, unsafe_override=True) is unsafe_policy


def test_next_policy_version_is_prospective(reliability_policy) -> None:
    assert next_policy_version(None) == 1
    assert next_policy_version(reliability_policy) == 2
