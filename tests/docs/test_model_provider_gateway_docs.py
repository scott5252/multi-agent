from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_model_provider_gateway_docs_cover_required_surfaces() -> None:
    text = (ROOT / "docs" / "model-provider-gateway.md").read_text()

    for expected in (
        "/admin/model-providers",
        "Local Provider Safety",
        "Safe Probes And Health",
        "Catalog Publication",
        "Runtime Gateway",
        "qa011.md",
        "QA011_UI.MD",
        "qa025.md",
        "secret_reference_invalid",
    ):
        assert expected in text


def test_qa011_ui_guide_covers_all_admin_pages() -> None:
    text = (ROOT / "specs" / "011-model-provider-gateway" / "QA011_UI.MD").read_text()

    for expected in (
        "Provider List",
        "Create Provider",
        "Edit Provider",
        "Detail Page",
        "Test Action",
        "Catalog Sync Action",
        "Catalog Page",
        "Tenant Visibility Check",
    ):
        assert expected in text
