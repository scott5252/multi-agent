from __future__ import annotations

from multi_agent_platform.config.settings import AppEnvironment, Settings


def auth_configuration_error(settings: Settings) -> str | None:
    if settings.auth_mode.value == "auth0":
        required = {
            "AUTH0_DOMAIN": settings.auth0_domain,
            "AUTH0_ISSUER": settings.auth0_issuer,
            "AUTH0_AUDIENCE": settings.auth0_audience,
        }
        missing = sorted(name for name, value in required.items() if not value)
        if missing:
            return f"missing required Auth0 settings: {', '.join(missing)}"
        return None

    if settings.app_env is AppEnvironment.PRODUCTION:
        return "AUTH_MODE=local_principal is not allowed in production"
    if not settings.local_principal_catalog_json:
        return "LOCAL_PRINCIPAL_CATALOG_JSON must define at least one principal"
    return None
