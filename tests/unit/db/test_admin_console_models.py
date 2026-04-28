from __future__ import annotations

from multi_agent_platform.db.models.admin_console import AdminSavedFilter


def test_admin_saved_filter_model_fields_and_constraints() -> None:
    columns = AdminSavedFilter.__table__.columns
    constraint_names = {
        constraint.name for constraint in AdminSavedFilter.__table__.constraints
    }

    assert "admin_saved_filter_id" in columns
    assert "criteria" in columns
    assert "safe_summary" in columns
    assert "tenant_id" in columns
    assert "uq_admin_saved_filters_scope_name" in constraint_names
    assert "ck_admin_saved_filters_scope_tenant" in constraint_names
