from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.model_skill_config import (
    HistoryResponse,
    RunProvenanceResponse,
)
from multi_agent_platform.api.ui.model_skill_config import (
    build_history_page_model,
    build_model_routing_page_model,
    build_run_provenance_page_model,
)


def test_model_skill_ui_models_are_built_from_safe_schemas() -> None:
    routing = build_model_routing_page_model(missing_default=True)
    history = build_history_page_model(HistoryResponse(items=[]))
    provenance = build_run_provenance_page_model(
        RunProvenanceResponse(workflow_run_id=uuid4())
    )

    assert routing.missing_default
    assert history.title == "Configuration History"
    assert provenance.title == "Run Provenance"
