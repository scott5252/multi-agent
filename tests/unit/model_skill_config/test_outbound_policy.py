from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import (
    OutboundPolicyCandidate,
    ScopeSelector,
)
from multi_agent_platform.config.policy import evaluate_outbound_policy


def test_outbound_policy_normalizes_case_and_allows_wildcard_subdomain() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    policy = OutboundPolicyCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        action_category="read",
        allowed_domain_patterns=("*.example.com",),
        allowed_schemes=("https",),
        allowed_ports=(443,),
    )

    decision = evaluate_outbound_policy(
        candidates=[policy],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
        destination_url="https://Docs.Example.com:443/reference",
    )

    assert decision.allowed


def test_outbound_policy_rejects_embedded_credentials() -> None:
    decision = evaluate_outbound_policy(
        candidates=[],
        scope=ScopeSelector(tenant_id=uuid4()),
        tool_id="http.fetch",
        action_category="read",
        destination_url="https://user:pass@example.com",
    )

    assert not decision.allowed
    assert "embedded credentials" in decision.safe_reason


def test_outbound_policy_denies_wrong_scheme_port_and_host() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    policy = OutboundPolicyCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        action_category="read",
        allowed_domain_patterns=("docs.example.com",),
        allowed_schemes=("https",),
        allowed_ports=(443,),
    )

    wrong_scheme = evaluate_outbound_policy(
        candidates=[policy],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
        destination_url="http://docs.example.com:443",
    )
    wrong_port = evaluate_outbound_policy(
        candidates=[policy],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
        destination_url="https://docs.example.com:8443",
    )
    wrong_host = evaluate_outbound_policy(
        candidates=[policy],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
        destination_url="https://example.net:443",
    )

    assert {
        wrong_scheme.safe_reason,
        wrong_port.safe_reason,
        wrong_host.safe_reason,
    } == {
        "scheme denied by outbound policy",
        "port denied by outbound policy",
        "host denied by outbound policy",
    }
