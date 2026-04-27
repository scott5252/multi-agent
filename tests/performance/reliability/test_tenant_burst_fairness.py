from __future__ import annotations

import pytest

from multi_agent_platform.reliability.load_profiles import build_mixed_lifecycle_profile
from tests.performance.reliability.harness import run_profile


@pytest.mark.performance
def test_tenant_burst_fairness_retains_compliant_throughput() -> None:
    report = run_profile(build_mixed_lifecycle_profile())
    assert report.accepted_throughput_retention >= 0.95
