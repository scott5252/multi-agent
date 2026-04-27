from __future__ import annotations

import pytest

from multi_agent_platform.reliability.load_profiles import build_mixed_lifecycle_profile
from tests.performance.reliability.harness import run_profile


@pytest.mark.performance
def test_mixed_lifecycle_load_profile_targets_5000_users() -> None:
    profile = build_mixed_lifecycle_profile()
    report = run_profile(profile)
    assert report.profile.active_users == 5_000
    assert report.profile.tenant_count == 50
