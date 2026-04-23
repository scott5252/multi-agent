from __future__ import annotations

from typing import Any

import jwt
from jwt import PyJWKClient

from multi_agent_platform.auth.claims import (
    NormalizedTokenClaims,
    normalize_token_claims,
)
from multi_agent_platform.config.settings import Settings


class JwtValidationError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class Auth0JwtValidator:
    def __init__(
        self,
        settings: Settings,
        jwk_client: PyJWKClient | None = None,
    ) -> None:
        self.settings = settings
        self._jwk_client = jwk_client

    def _client(self) -> PyJWKClient:
        if self._jwk_client is None:
            if self.settings.auth0_jwks_url is None:
                raise JwtValidationError("auth0 jwks url is not configured")
            self._jwk_client = PyJWKClient(self.settings.auth0_jwks_url)
        return self._jwk_client

    async def validate(self, token: str) -> NormalizedTokenClaims:
        try:
            signing_key = self._client().get_signing_key_from_jwt(token)
            payload: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=list(self.settings.auth0_algorithms),
                audience=self.settings.auth0_audience,
                issuer=self.settings.auth0_issuer,
            )
        except Exception as exc:  # pragma: no cover - library-specific subclasses
            raise JwtValidationError(str(exc)) from exc

        try:
            return normalize_token_claims(
                payload,
                required_org_claim=self.settings.auth0_required_org_claim,
            )
        except ValueError as exc:
            raise JwtValidationError(str(exc)) from exc
