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


def test_admin_model_skill_ui_exposes_routing_skills_tools_and_provenance_states() -> (
    None
):
    routing = build_model_routing_page_model(missing_default=True)
    history = build_history_page_model(HistoryResponse(items=[]))
    provenance = build_run_provenance_page_model(
        RunProvenanceResponse(
            workflow_run_id=uuid4(),
            resolution_digest="digest",
            decisions=[
                {
                    "outcome": "deny",
                    "safe_reason": "credential_unsatisfied",
                }
            ],
        )
    )

    assert routing.missing_default
    assert routing.policy_create_actions is not None
    assert "credential_requirement" in routing.policy_create_actions
    assert history.history.items == []
    assert provenance.provenance.decisions[0]["outcome"] == "deny"
