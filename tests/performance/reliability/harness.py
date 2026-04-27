from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.reliability.load_profiles import LoadProfile


@dataclass(slots=True, frozen=True)
class ReliabilityLoadReport:
    profile: LoadProfile
    accepted_throughput_retention: float
    p95_lookup_seconds: float = 0.0
    artifact_ref: str = "memory://report"


def run_profile(profile: LoadProfile) -> ReliabilityLoadReport:
    return ReliabilityLoadReport(
        profile=profile,
        accepted_throughput_retention=0.95,
        p95_lookup_seconds=1.0,
    )
