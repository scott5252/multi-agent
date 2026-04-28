from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from multi_agent_platform.config.model_skill import (
    ConfigKind,
    DecisionCategory,
    PolicyOutcome,
    stable_digest,
)


@dataclass(frozen=True, slots=True)
class ResolvedConfigurationSnapshot:
    tenant_id: UUID
    workflow_run_id: UUID
    run_bundle_id: UUID
    bundle_digest: str
    workflow_version_bundle_id: UUID
    model_routing_version_ids: tuple[UUID, ...] = ()
    prompt_reference_version_ids: tuple[UUID, ...] = ()
    prompt_library_version_ids: tuple[UUID, ...] = ()
    prompt_library_digests: tuple[str, ...] = ()
    skill_binding_version_ids: tuple[UUID, ...] = ()
    allowed_tool_policy_version_ids: tuple[UUID, ...] = ()
    outbound_domain_policy_version_ids: tuple[UUID, ...] = ()
    secret_reference_version_ids: tuple[UUID, ...] = ()
    credential_requirement_version_ids: tuple[UUID, ...] = ()
    warnings: tuple[str, ...] = ()

    def digest(self) -> str:
        return stable_digest(
            {
                "tenant_id": self.tenant_id,
                "workflow_run_id": self.workflow_run_id,
                "run_bundle_id": self.run_bundle_id,
                "bundle_digest": self.bundle_digest,
                "workflow_version_bundle_id": self.workflow_version_bundle_id,
                "model_routing_version_ids": sorted(
                    map(str, self.model_routing_version_ids)
                ),
                "prompt_reference_version_ids": sorted(
                    map(str, self.prompt_reference_version_ids)
                ),
                "prompt_library_version_ids": sorted(
                    map(str, self.prompt_library_version_ids)
                ),
                "prompt_library_digests": sorted(self.prompt_library_digests),
                "skill_binding_version_ids": sorted(
                    map(str, self.skill_binding_version_ids)
                ),
                "allowed_tool_policy_version_ids": sorted(
                    map(str, self.allowed_tool_policy_version_ids)
                ),
                "outbound_domain_policy_version_ids": sorted(
                    map(str, self.outbound_domain_policy_version_ids)
                ),
                "secret_reference_version_ids": sorted(
                    map(str, self.secret_reference_version_ids)
                ),
                "credential_requirement_version_ids": sorted(
                    map(str, self.credential_requirement_version_ids)
                ),
            }
        )


@dataclass(frozen=True, slots=True)
class SafeRuntimeDecision:
    tenant_id: UUID
    workflow_run_id: UUID
    decision_category: DecisionCategory
    outcome: PolicyOutcome
    requested_resource: str
    requested_action: str | None = None
    idempotency_key: str | None = None
    evaluated_version_ids: tuple[UUID, ...] = ()
    winning_version_ids: tuple[UUID, ...] = ()
    source_scopes: tuple[str, ...] = ()
    denial_category: str | None = None
    safe_reason: str = ""
    redacted_metadata: dict[str, object] = field(default_factory=dict)

    def to_record_payload(self) -> dict[str, object]:
        return {
            "tenant_id": str(self.tenant_id),
            "workflow_run_id": str(self.workflow_run_id),
            "decision_category": self.decision_category.value,
            "outcome": self.outcome.value,
            "requested_resource": self.requested_resource,
            "requested_action": self.requested_action,
            "idempotency_key": self.idempotency_key,
            "evaluated_version_ids": [
                str(value) for value in self.evaluated_version_ids
            ],
            "winning_version_ids": [str(value) for value in self.winning_version_ids],
            "source_scopes": list(self.source_scopes),
            "denial_category": self.denial_category,
            "safe_reason": self.safe_reason,
            "redacted_metadata": self.redacted_metadata,
        }


def audit_diff_summary(
    *,
    action: str,
    config_kind: ConfigKind,
    prior_version_id: UUID | None,
    new_version_id: UUID | None,
    summary: dict[str, object],
) -> dict[str, object]:
    forbidden = {"secret", "password", "token", "api_key", "credential_value"}
    safe_summary = {
        key: ("***REDACTED***" if key.lower() in forbidden else value)
        for key, value in summary.items()
    }
    return {
        "action": action,
        "config_kind": config_kind.value,
        "prior_version_id": str(prior_version_id) if prior_version_id else None,
        "new_version_id": str(new_version_id) if new_version_id else None,
        "summary": safe_summary,
    }
