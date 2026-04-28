from __future__ import annotations

from pathlib import Path


def test_readme_mentions_model_provider_gateway_user_flow() -> None:
    readme = Path("README.md").read_text()

    assert "/admin/model-providers" in readme
    assert "Safe provider tests" in readme
    assert "Catalog sync" in readme
    assert "ModelGateway" in readme
