from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles
from multi_agent_platform.model_providers.models import ProviderConnectionSummary


@dataclass(frozen=True, slots=True)
class ModelProviderListPage:
    title: str
    connections: tuple[ProviderConnectionSummary, ...]
    can_mutate: bool
    new_href: str = "/admin/model-providers/new"
    catalog_href: str = "/admin/model-providers/catalog"


@dataclass(frozen=True, slots=True)
class ModelProviderFormPage:
    title: str
    action: str
    connection_id: UUID | None
    can_mutate: bool
    provider_types: tuple[str, ...] = ("openai", "local_openai_compatible")
    visibility_modes: tuple[str, ...] = ("platform_default", "tenant_allowlist")


@dataclass(frozen=True, slots=True)
class ModelProviderDetailPage:
    title: str
    connection: object
    models: tuple[object, ...]
    tenant_ids: tuple[UUID, ...]
    latest_test: object | None
    can_mutate: bool


@dataclass(frozen=True, slots=True)
class ModelProviderCatalogPage:
    title: str
    entries: tuple[object, ...]
    can_mutate: bool


def build_list_page(
    connections: list[ProviderConnectionSummary],
    *,
    can_mutate: bool,
) -> ModelProviderListPage:
    return ModelProviderListPage(
        title="Model Providers",
        connections=tuple(connections),
        can_mutate=can_mutate,
    )


def build_form_page(
    *,
    connection_id: UUID | None,
    can_mutate: bool,
) -> ModelProviderFormPage:
    return ModelProviderFormPage(
        title="New Model Provider" if connection_id is None else "Edit Model Provider",
        action="/admin/model-providers"
        if connection_id is None
        else f"/admin/model-providers/{connection_id}",
        connection_id=connection_id,
        can_mutate=can_mutate,
    )


def build_detail_page(
    *,
    connection: object,
    models: tuple[object, ...],
    tenant_ids: tuple[UUID, ...],
    latest_test: object | None,
    can_mutate: bool,
) -> ModelProviderDetailPage:
    display_name = getattr(connection, "display_name", "Model Provider")
    return ModelProviderDetailPage(
        title=str(display_name),
        connection=connection,
        models=models,
        tenant_ids=tenant_ids,
        latest_test=latest_test,
        can_mutate=can_mutate,
    )


def build_catalog_page(
    *,
    entries: tuple[object, ...],
    can_mutate: bool,
) -> ModelProviderCatalogPage:
    return ModelProviderCatalogPage(
        title="Model Provider Catalog",
        entries=entries,
        can_mutate=can_mutate,
    )


def model_provider_filter_profile() -> FilterProfile:
    return filter_profiles()["model_providers"]
