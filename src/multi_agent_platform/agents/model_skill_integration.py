from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ModelSkillPromptReference:
    prompt_version_id: str
    prompt_digest: str
    purpose: str


def model_skill_prompt_references_from_profile(
    prompt_references: list[dict[str, object]],
) -> tuple[ModelSkillPromptReference, ...]:
    references: list[ModelSkillPromptReference] = []
    for reference in prompt_references:
        version_id = str(reference.get("prompt_version_id", "")).strip()
        digest = str(reference.get("prompt_digest", "")).strip()
        if not version_id or not digest:
            continue
        references.append(
            ModelSkillPromptReference(
                prompt_version_id=version_id,
                prompt_digest=digest,
                purpose=str(reference.get("purpose", "")),
            )
        )
    return tuple(references)


def prompt_reference_digest_findings(
    *,
    profile_prompt_references: list[dict[str, object]],
    model_skill_digests_by_prompt_version: dict[str, str],
) -> tuple[dict[str, str], ...]:
    findings: list[dict[str, str]] = []
    for index, reference in enumerate(
        model_skill_prompt_references_from_profile(profile_prompt_references)
    ):
        expected = model_skill_digests_by_prompt_version.get(
            reference.prompt_version_id
        )
        if expected is None:
            findings.append(
                {
                    "code": "missing_model_skill_prompt_reference",
                    "severity": "blocking",
                    "field_path": f"prompt_references[{index}]",
                    "message": (
                        "Profile prompt version is missing a model-skill reference."
                    ),
                }
            )
        elif expected != reference.prompt_digest:
            findings.append(
                {
                    "code": "prompt_digest_mismatch",
                    "severity": "blocking",
                    "field_path": f"prompt_references[{index}].prompt_digest",
                    "message": (
                        "Profile prompt digest does not match model-skill config."
                    ),
                }
            )
    return tuple(findings)


def build_profile_gateway_routing_context(
    *,
    agent_profile_version_id: UUID,
    model_routing_hints: dict[str, object],
    memory_policy: dict[str, object],
    tool_policy_expectations: dict[str, object],
    output_contract: dict[str, object],
    source_scope: str,
) -> dict[str, object]:
    return {
        "agent_profile_version_id": str(agent_profile_version_id),
        "model_routing_hints": dict(model_routing_hints),
        "memory_policy_context": dict(memory_policy),
        "tool_policy_expectations": dict(tool_policy_expectations),
        "output_contract_metadata": dict(output_contract),
        "profile_provenance": {
            "source_scope": source_scope,
            "tenant_profile_precedence_applied": source_scope == "tenant",
        },
    }
