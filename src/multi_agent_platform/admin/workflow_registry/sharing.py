from __future__ import annotations


def sharing_visibility_label(*, scope_type: str) -> str:
    if scope_type == "platform":
        return "Platform"
    return "Tenant"
