from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from multi_agent_platform.skill_execution.schemas import (
    CredentialResolutionSummary,
    ExecutionMode,
    SkillToolExecutionRequest,
    ToolPolicyDecision,
)


class PolicyEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    decisions: tuple[ToolPolicyDecision, ...]
    credential_summary: CredentialResolutionSummary | None = None
    error_code: str | None = None
    error_message: str | None = None


class SkillExecutionPolicyBundle(BaseModel):
    model_config = ConfigDict(frozen=True)

    installed_skill_versions: Mapping[str, frozenset[str]] = Field(default_factory=dict)
    allowed_tools: frozenset[str] = Field(default_factory=frozenset)
    allowed_outbound_domains: frozenset[str] = Field(default_factory=frozenset)
    credential_summaries: Mapping[str, CredentialResolutionSummary] = Field(
        default_factory=dict
    )
    environment: str = "local"
    live_probe_enabled: bool = False
    side_effects_allowed: bool = False
    policy_refs: Mapping[str, str] = Field(default_factory=dict)

    @classmethod
    def local_qa_default(cls, *, tenant_id: str | UUID) -> SkillExecutionPolicyBundle:
        from multi_agent_platform.skill_execution.adapters import (
            default_adapter_registry,
        )

        adapters = default_adapter_registry()
        tenant_uuid = UUID(str(tenant_id))
        return cls(
            installed_skill_versions={
                adapter.skill_package: frozenset({"1.0.0"})
                for adapter in adapters.values()
            },
            allowed_tools=frozenset(adapters),
            allowed_outbound_domains=frozenset(
                domain
                for adapter in adapters.values()
                for domain in adapter.allowed_domains
            ),
            credential_summaries={
                adapter.required_credential_kind: CredentialResolutionSummary(
                    required=True,
                    credential_kind=adapter.required_credential_kind,
                    tenant_id=tenant_uuid,
                    reference=f"delegated:{adapter.required_credential_kind}:qa",
                    available=True,
                    safe_label=f"QA {adapter.display_name}",
                )
                for adapter in adapters.values()
            },
            policy_refs={
                "tool_policy": "qa021-tool-policy",
                "outbound_policy": "qa021-outbound-policy",
                "credential_policy": "qa021-credential-policy",
            },
        )

    def without_credentials(self) -> SkillExecutionPolicyBundle:
        return self.model_copy(update={"credential_summaries": {}})


def evaluate_skill_execution_policy(
    *,
    request: SkillToolExecutionRequest,
    adapter: object | None,
    adapter_skill_package: str | None,
    adapter_domains: tuple[str, ...],
    adapter_read_only: bool,
    adapter_credential_kind: str | None,
    policy_bundle: SkillExecutionPolicyBundle,
) -> PolicyEvaluation:
    decisions: list[ToolPolicyDecision] = []

    def add(
        check: str,
        allowed: bool,
        reason: str,
        *,
        policy_ref: str | None = None,
        error_code: str | None = None,
    ) -> PolicyEvaluation | None:
        decisions.append(
            ToolPolicyDecision(
                check=check,
                allowed=allowed,
                reason=reason,
                policy_ref=policy_ref,
            )
        )
        if allowed:
            return None
        return PolicyEvaluation(
            allowed=False,
            decisions=tuple(decisions),
            error_code=error_code or check,
            error_message=reason,
        )

    denied = add(
        "tool_registered",
        adapter is not None,
        "tool adapter is registered"
        if adapter is not None
        else "tool is not registered",
        error_code="tool_not_registered",
    )
    if denied is not None:
        return denied

    versions = policy_bundle.installed_skill_versions.get(request.skill_package)
    installed = bool(versions and request.skill_version in versions)
    if request.skill_package != adapter_skill_package:
        installed = False
    denied = add(
        "skill_installed",
        installed,
        "installed skill version matched"
        if installed
        else "installed skill version did not match the requested tool",
        policy_ref=policy_bundle.policy_refs.get("skill_binding"),
        error_code="skill_not_installed",
    )
    if denied is not None:
        return denied

    tool_allowed = (
        "*" in policy_bundle.allowed_tools
        or request.tool_name in policy_bundle.allowed_tools
    )
    denied = add(
        "tool_policy",
        tool_allowed,
        "tool policy allowed read operation"
        if tool_allowed
        else "no active tool allow policy matched",
        policy_ref=policy_bundle.policy_refs.get("tool_policy"),
        error_code="tool_denied",
    )
    if denied is not None:
        return denied

    side_effect_allowed = (
        not request.side_effect_requested
        and adapter_read_only
        or policy_bundle.side_effects_allowed
    )
    denied = add(
        "side_effect_policy",
        side_effect_allowed,
        "read-only operation has no unsafe side effect"
        if side_effect_allowed
        else "unsafe side effects are blocked by default",
        error_code="side_effect_denied",
    )
    if denied is not None:
        return denied

    outbound_domains = tuple(
        dict.fromkeys((*adapter_domains, *request.outbound_domains))
    )
    outbound_allowed = all(
        _domain_allowed(domain, policy_bundle.allowed_outbound_domains)
        for domain in outbound_domains
    )
    denied = add(
        "outbound_policy",
        outbound_allowed,
        "outbound domains are allowlisted"
        if outbound_allowed
        else "one or more outbound domains are blocked",
        policy_ref=policy_bundle.policy_refs.get("outbound_policy"),
        error_code="domain_denied",
    )
    if denied is not None:
        return denied

    live_allowed = request.execution_mode is ExecutionMode.MOCK or (
        policy_bundle.live_probe_enabled
        and policy_bundle.environment not in {"local", "test", "ci"}
    )
    denied = add(
        "execution_mode",
        live_allowed,
        "execution mode allowed"
        if live_allowed
        else "live probes are disabled for this environment",
        error_code="live_probe_denied",
    )
    if denied is not None:
        return denied

    credential_kind = request.required_credential_kind or adapter_credential_kind
    credential_summary = None
    if credential_kind:
        credential_summary = policy_bundle.credential_summaries.get(credential_kind)
        available = bool(credential_summary and credential_summary.available)
        denied = add(
            "credential_policy",
            available,
            "credential metadata is available"
            if available
            else "required credential metadata is unavailable",
            policy_ref=policy_bundle.policy_refs.get("credential_policy"),
            error_code="credential_unsatisfied",
        )
        if denied is not None:
            return denied
        assert credential_summary is not None
        same_tenant = credential_summary.tenant_id == request.tenant_id
        denied = add(
            "credential_tenant",
            same_tenant,
            "credential metadata belongs to the request tenant"
            if same_tenant
            else "credential metadata belongs to a different tenant",
            policy_ref=policy_bundle.policy_refs.get("credential_policy"),
            error_code="credential_tenant_mismatch",
        )
        if denied is not None:
            return denied

    return PolicyEvaluation(
        allowed=True,
        decisions=tuple(decisions),
        credential_summary=credential_summary,
    )


def _domain_allowed(domain: str, allowed_domains: frozenset[str]) -> bool:
    normalized = domain.lower().strip()
    if "*" in allowed_domains or normalized in allowed_domains:
        return True
    return any(
        pattern.startswith("*.") and normalized.endswith(pattern[1:])
        for pattern in allowed_domains
    )
