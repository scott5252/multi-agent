from __future__ import annotations

from types import SimpleNamespace

import jwt
import pytest

from multi_agent_platform.auth.jwt_validator import (
    Auth0JwtValidator,
    JwtValidationError,
)
from multi_agent_platform.config.settings import Settings


def build_auth0_settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env="test",
        auth_mode="auth0",
        auth0_domain="tenant.example.com",
        auth0_issuer="https://tenant.example.com/",
        auth0_audience="multi-agent-platform",
        auth0_algorithms=("HS256",),
    )


class FakeJwkClient:
    def __init__(self, key: str) -> None:
        self.key = key

    def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
        return SimpleNamespace(key=self.key)


async def test_jwt_validator_normalizes_valid_claims() -> None:
    key = "test-secret-key-with-32-plus-bytes"
    token = jwt.encode(
        {
            "sub": "auth0|user-1",
            "iss": "https://tenant.example.com/",
            "aud": "multi-agent-platform",
            "org_id": "org-acme",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "permissions": ["tenant:read"],
        },
        key,
        algorithm="HS256",
    )

    validator = Auth0JwtValidator(build_auth0_settings(), FakeJwkClient(key))
    claims = await validator.validate(token)

    assert claims.subject == "auth0|user-1"
    assert claims.org_id == "org-acme"
    assert claims.permissions == ("tenant:read",)


async def test_jwt_validator_rejects_missing_required_org_claim() -> None:
    key = "test-secret-key-with-32-plus-bytes"
    token = jwt.encode(
        {
            "sub": "auth0|user-1",
            "iss": "https://tenant.example.com/",
            "aud": "multi-agent-platform",
        },
        key,
        algorithm="HS256",
    )

    validator = Auth0JwtValidator(build_auth0_settings(), FakeJwkClient(key))
    with pytest.raises(JwtValidationError):
        await validator.validate(token)
