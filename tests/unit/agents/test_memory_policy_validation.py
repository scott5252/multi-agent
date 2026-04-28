from __future__ import annotations

from multi_agent_platform.memory.policy import validate_profile_memory_policy


def test_profile_memory_policy_requires_known_modes_and_write_compatibility() -> None:
    findings = validate_profile_memory_policy(
        {
            "scope_mode": "read_only",
            "retention_mode": "forever",
            "allow_writes": True,
        }
    )

    assert {finding.code for finding in findings} == {
        "invalid_memory_retention_mode",
        "memory_write_requires_read_write_scope",
    }


def test_profile_memory_policy_accepts_read_write_workflow_policy() -> None:
    assert (
        validate_profile_memory_policy(
            {
                "scope_mode": "read_write",
                "retention_mode": "workflow",
                "allow_writes": True,
            }
        )
        == ()
    )
