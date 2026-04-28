from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.api.routers import admin_agent_profiles, admin_prompts


class _Templates:
    def TemplateResponse(  # noqa: N802
        self,
        request: object,
        template: str,
        context: dict[str, object],
        **kwargs: object,
    ) -> dict[str, object]:
        return {"request": request, "template": template, "context": context, **kwargs}


def _container() -> SimpleNamespace:
    return SimpleNamespace(workflow_ui_templates=_Templates())


def _principal() -> SimpleNamespace:
    return SimpleNamespace(principal_id="tenant-admin-acme")


async def _fake_shell_for_request(**kwargs: object) -> SimpleNamespace:
    title = str(kwargs.get("title", "Admin"))
    return SimpleNamespace(
        title=title,
        active_scope=SimpleNamespace(scope_type="tenant", tenant_id=uuid4()),
    )


@pytest.mark.asyncio
async def test_prompt_html_route_handlers_render_expected_templates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        admin_prompts,
        "build_shell_for_request",
        _fake_shell_for_request,
    )
    request = SimpleNamespace()
    principal = _principal()
    session = SimpleNamespace()
    container = _container()
    lineage_id = uuid4()
    version_id = uuid4()

    responses = [
        await admin_prompts.prompt_library_index(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_new(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_edit(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_detail(
            prompt_version_id=version_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_history(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_preview_page(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
    ]

    assert [response["template"] for response in responses] == [
        "prompts/index.html",
        "prompts/edit.html",
        "prompts/edit.html",
        "prompts/detail.html",
        "prompts/history.html",
        "prompts/preview.html",
    ]
    assert responses[2]["context"]["page"].prompt_lineage_id == lineage_id
    assert responses[3]["context"]["page"].prompt_version_id == version_id


@pytest.mark.asyncio
async def test_agent_profile_html_route_handlers_render_expected_templates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        admin_agent_profiles,
        "build_shell_for_request",
        _fake_shell_for_request,
    )
    request = SimpleNamespace()
    principal = _principal()
    session = SimpleNamespace()
    container = _container()
    profile_id = uuid4()
    version_id = uuid4()

    responses = [
        await admin_agent_profiles.agent_profiles_index(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_new(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_edit(
            agent_runtime_profile_id=profile_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_detail(
            agent_profile_version_id=version_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_history(
            agent_runtime_profile_id=profile_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_resolve(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
    ]

    assert [response["template"] for response in responses] == [
        "agent_profiles/index.html",
        "agent_profiles/edit.html",
        "agent_profiles/edit.html",
        "agent_profiles/detail.html",
        "agent_profiles/history.html",
        "agent_profiles/resolve.html",
    ]
    assert responses[2]["context"]["page"].agent_runtime_profile_id == profile_id
    assert responses[3]["context"]["page"].agent_profile_version_id == version_id
