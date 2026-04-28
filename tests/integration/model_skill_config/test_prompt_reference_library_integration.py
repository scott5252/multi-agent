from __future__ import annotations

from multi_agent_platform.agents.model_skill_integration import (
    model_skill_prompt_references_from_profile,
    prompt_reference_digest_findings,
)


def test_profile_prompt_reference_digest_matches_model_skill_reference() -> None:
    references = [
        {
            "prompt_version_id": "prompt-v1",
            "prompt_digest": "sha256:abc",
            "purpose": "planner",
        }
    ]

    parsed_references = model_skill_prompt_references_from_profile(references)
    assert parsed_references[0].purpose == "planner"
    assert (
        prompt_reference_digest_findings(
            profile_prompt_references=references,
            model_skill_digests_by_prompt_version={"prompt-v1": "sha256:abc"},
        )
        == ()
    )
    assert (
        prompt_reference_digest_findings(
            profile_prompt_references=references,
            model_skill_digests_by_prompt_version={"prompt-v1": "sha256:wrong"},
        )[0]["code"]
        == "prompt_digest_mismatch"
    )


def test_digest_findings_report_missing_model_skill_reference() -> None:
    references = [
        {
            "prompt_version_id": "prompt-v2",
            "prompt_digest": "sha256:def",
            "purpose": "planner",
        },
        {
            "prompt_version_id": "",
            "prompt_digest": "",
            "purpose": "ignored",
        },
    ]

    parsed_references = model_skill_prompt_references_from_profile(references)
    findings = prompt_reference_digest_findings(
        profile_prompt_references=references,
        model_skill_digests_by_prompt_version={},
    )

    assert len(parsed_references) == 1
    assert findings[0]["code"] == "missing_model_skill_prompt_reference"
