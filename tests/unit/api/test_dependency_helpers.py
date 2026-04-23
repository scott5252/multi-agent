from __future__ import annotations

from types import SimpleNamespace

import pytest

from multi_agent_platform.api.deps import (
    get_container,
    get_secret_provider,
    get_settings,
    get_storage_provider,
)


def test_dependency_helpers_return_container_members(settings) -> None:
    container = SimpleNamespace(
        settings=settings,
        secret_provider=SimpleNamespace(provider_name="static"),
        storage_provider=SimpleNamespace(provider_name="filesystem"),
        workflow_ui_templates=SimpleNamespace(
            directory=settings.web_admin_templates_dir
        ),
    )
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(container=container))
    )
    assert get_container(request) is container
    assert get_settings(container) is settings
    assert get_secret_provider(container).provider_name == "static"
    assert get_storage_provider(container).provider_name == "filesystem"
    assert str(container.workflow_ui_templates.directory).endswith("/templates")


def test_get_scope_raises_when_missing() -> None:
    from multi_agent_platform.api.deps import get_scope

    request = SimpleNamespace(state=SimpleNamespace())
    with pytest.raises(RuntimeError):
        get_scope(request)
