from __future__ import annotations


def sharing_visibility_label(*, scope_type: str) -> str:
    if scope_type == "platform":
        return "Platform"
    return "Tenant"


def can_grant_workflow_version_to_tenant(*, scope_type: str) -> bool:
    return scope_type == "platform"
