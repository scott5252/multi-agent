from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.api.ui.admin_console import (
    AdminScope,
    filter_profiles,
    normalize_filter_criteria,
)


def test_filter_profiles_cover_useful_admin_areas() -> None:
    profiles = filter_profiles()

    assert set(profiles) == {
        "workflows",
        "model_providers",
        "model_skill_history",
        "operations",
        "briefing_preferences",
        "run_inspection",
        "reliability_breakers",
        "reliability_dead_letters",
        "telegram_configuration",
    }
    assert profiles["run_inspection"].destination_href == "/admin/runs"


def test_tenant_filter_scope_mismatch_is_rejected() -> None:
    active_tenant = uuid4()

    with pytest.raises(ValueError):
        normalize_filter_criteria(
            "run_inspection",
            {"tenant_id": str(uuid4()), "status": "failed"},
            active_scope=AdminScope.tenant(active_tenant),
        )


def test_restore_summary_is_safe_and_string_bounded() -> None:
    normalized = normalize_filter_criteria(
        "reliability_dead_letters",
        {"status": "open", "failure_category": "timeout"},
        active_scope=AdminScope.platform(),
    )

    assert normalized.safe_summary == {
        "failure_category": "timeout",
        "status": "open",
    }
