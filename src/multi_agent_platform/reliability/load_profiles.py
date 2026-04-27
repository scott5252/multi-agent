from __future__ import annotations

from dataclasses import dataclass
from random import Random
from uuid import NAMESPACE_URL, UUID, uuid5


@dataclass(slots=True, frozen=True)
class LoadProfile:
    seed: int
    tenant_count: int
    active_users: int
    workload_mix: dict[str, float]
    policy_version: int


def build_mixed_lifecycle_profile(
    *, seed: int = 9009, tenant_count: int = 50, active_users: int = 5_000
) -> LoadProfile:
    return LoadProfile(
        seed=seed,
        tenant_count=tenant_count,
        active_users=active_users,
        workload_mix={"submit": 0.35, "monitor": 0.55, "artifact": 0.1},
        policy_version=1,
    )


def deterministic_tenant_ids(profile: LoadProfile) -> list[UUID]:
    rnd = Random(profile.seed)
    return [
        uuid5(NAMESPACE_URL, f"tenant-{profile.seed}-{rnd.randrange(10_000_000)}")
        for _ in range(profile.tenant_count)
    ]
