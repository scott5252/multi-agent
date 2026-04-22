from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status


@dataclass(frozen=True)
class Settings:
    auth_enabled: bool = True


@dataclass(frozen=True)
class Principal:
    user_id: str
    roles: frozenset[str]


settings = Settings(auth_enabled=False)
app = FastAPI()


def get_settings() -> Settings:
    return settings


def get_dev_principal() -> Principal:
    return Principal(user_id="dev-user", roles=frozenset({"admin"}))


def validate_auth0_token(authorization: str | None) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid bearer token",
        )

    token = authorization.removeprefix("Bearer ").strip()
    if token != "example-auth0-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token validation failed",
        )

    return Principal(user_id="auth0-user", roles=frozenset({"user", "admin"}))


def get_principal(
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    if not settings.auth_enabled:
        return get_dev_principal()
    return validate_auth0_token(authorization)


def require_role(required_role: str):
    def dependency(
        principal: Annotated[Principal, Depends(get_principal)],
    ) -> Principal:
        if required_role not in principal.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"missing required role: {required_role}",
            )
        return principal

    return dependency


@app.get("/admin/workflows")
def list_workflows(
    principal: Annotated[Principal, Depends(require_role("admin"))],
) -> dict[str, object]:
    return {"user_id": principal.user_id, "workflows": []}
