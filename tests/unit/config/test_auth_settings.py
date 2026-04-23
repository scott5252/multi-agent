from __future__ import annotations

import pytest

from multi_agent_platform.auth.config import auth_configuration_error
from multi_agent_platform.config.settings import Settings


def test_auth0_requires_domain_issuer_and_audience() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, app_env="test", auth_mode="auth0")


def test_production_rejects_local_principal_mode() -> None:
    with pytest.raises(ValueError):
        Settings(
            _env_file=None,
            app_env="production",
            auth_mode="local_principal",
            local_principal_catalog_json={
                "dev-user": {
                    "catalog_key": "dev-user",
                    "display_name": "Dev User",
                }
            },
        )


def test_auth_configuration_error_reports_empty_local_catalog(settings) -> None:
    broken = settings.model_copy(update={"local_principal_catalog_json": {}})
    assert auth_configuration_error(broken) == (
        "LOCAL_PRINCIPAL_CATALOG_JSON must define at least one principal"
    )
