from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.provenance import ResolvedConfigurationSnapshot
from multi_agent_platform.runtime.versioning import RunVersionBundle


def test_prompt_profile_pins_are_part_of_run_resolution_digest() -> None:
    base = {
        "tenant_id": uuid4(),
        "workflow_run_id": uuid4(),
        "run_bundle_id": uuid4(),
        "bundle_digest": "a" * 64,
        "workflow_version_bundle_id": uuid4(),
        "prompt_reference_version_ids": (uuid4(),),
    }

    first = ResolvedConfigurationSnapshot(
        **base,
        prompt_library_version_ids=(uuid4(),),
        prompt_library_digests=("sha256:first",),
    )
    second = ResolvedConfigurationSnapshot(
        **base,
        prompt_library_version_ids=(uuid4(),),
        prompt_library_digests=("sha256:second",),
    )

    assert first.digest() != second.digest()


def test_run_version_bundle_keeps_published_prompt_profile_pin_metadata() -> None:
    bundle = RunVersionBundle(
        workflow_version_bundle_id="workflow-version",
        workflow_lineage_id="workflow-lineage",
        workflow_key="qa",
        compiled_bundle_digest="b" * 64,
        compiler_version="compiler",
        pinned_skill_versions={},
        subworkflow_version_refs={},
        prompt_profile_pins=[
            {
                "agent_key": "planner",
                "agent_profile_version_id": "profile-v1",
                "prompt_version_ids": ["prompt-v1"],
            }
        ],
    )

    assert bundle.prompt_profile_pins[0]["prompt_version_ids"] == ["prompt-v1"]
