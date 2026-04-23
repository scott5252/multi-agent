from __future__ import annotations

import pytest

from multi_agent_platform.auth.claims import normalize_token_claims


def test_normalize_token_claims_supports_audience_lists_and_scope_fallback() -> None:
    claims = normalize_token_claims(
        {
            "sub": "auth0|user-1",
            "iss": "https://tenant.example.com/",
            "aud": ["multi-agent-platform", "secondary"],
            "scope": "tenant:read tenant:admin",
            "org_id": "org-acme",
        },
        required_org_claim=True,
    )

    assert claims.audience == ("multi-agent-platform", "secondary")
    assert claims.permissions == ("tenant:read", "tenant:admin")


def test_normalize_token_claims_rejects_missing_subject() -> None:
    with pytest.raises(ValueError):
        normalize_token_claims(
            {
                "iss": "https://tenant.example.com/",
                "aud": "multi-agent-platform",
                "org_id": "org-acme",
            },
            required_org_claim=True,
        )
