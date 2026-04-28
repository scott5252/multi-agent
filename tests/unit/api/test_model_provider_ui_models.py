from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.ui.model_providers import (
    build_catalog_page,
    build_detail_page,
    build_form_page,
    build_list_page,
)
from multi_agent_platform.model_providers.models import (
    HealthState,
    ProviderConnectionSummary,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
)


def test_model_provider_ui_builders_preserve_page_state() -> None:
    summary = ProviderConnectionSummary(
        provider_connection_id=uuid4(),
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(),
        active=True,
        health_state=HealthState.UNTESTED,
        model_count=1,
    )

    list_page = build_list_page([summary], can_mutate=True)
    form_page = build_form_page(connection_id=None, can_mutate=True)
    detail_page = build_detail_page(
        connection=summary,
        models=("gpt-test",),
        tenant_ids=(),
        latest_test=None,
        can_mutate=True,
    )
    catalog_page = build_catalog_page(entries=(), can_mutate=False)

    assert list_page.connections == (summary,)
    assert form_page.action == "/admin/model-providers"
    assert detail_page.title == "Provider"
    assert catalog_page.title == "Model Provider Catalog"
