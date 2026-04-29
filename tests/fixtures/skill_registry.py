from __future__ import annotations

from copy import deepcopy


def valid_skill_manifest() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "slug": "calendar-assistant",
        "semantic_version": "1.2.3",
        "description": "Calendar assistant for safe scheduling operations.",
        "entrypoint": {
            "type": "approved_tool_ref",
            "approved_integration_ref": "tool:calendar:v1",
        },
        "tools": [
            {
                "tool_id": "calendar.list",
                "approved_integration_ref": "tool:calendar:v1",
                "display_name": "List calendars",
                "description": "Lists calendar metadata.",
                "action_categories": ["read"],
                "side_effect_profile": "read_only",
                "safe_usage": "Use for tenant-scoped calendar listing.",
            }
        ],
        "action_categories": ["read"],
        "network_requirements": [
            {
                "tool_id": "calendar.list",
                "action_category": "read",
                "allowed_schemes": ["https"],
                "allowed_domain_patterns": ["calendar.example.com"],
                "allowed_ports": [443],
                "required": True,
                "safe_description": "Calendar API endpoint.",
            }
        ],
        "credential_requirements": [
            {
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "tool_id": "calendar.list",
                "action_category": "read",
                "required": True,
                "delegated_credential_scopes": ["calendar.readonly"],
                "safe_description": "Delegated calendar read access.",
            }
        ],
        "runtime_permissions": [
            {
                "permission_key": "calendar-read",
                "permission_type": "tool_access",
                "tool_id": "calendar.list",
                "action_category": "read",
                "side_effect_level": "read_only",
                "required": True,
                "safe_description": "Read calendar metadata.",
            }
        ],
        "test_fixtures": [
            {
                "fixture_key": "list-calendars",
                "tool_id": "calendar.list",
                "action_category": "read",
                "fixture_kind": "policy_preview",
                "safe_input_summary": "Policy-only calendar list probe.",
                "fixture_digest": "sha256:fixture",
                "requires_credentials": True,
                "expected_outcome": "passed",
                "timeout_seconds": 10,
            }
        ],
        "compatibility": {"platform_min_version": "0.1.0"},
        "safe_documentation": {
            "summary": "Safe operator documentation.",
            "documentation_digest": "sha256:docs",
            "redaction_classification": "safe",
            "support_contacts": ["ops@example.com"],
        },
        "artifact_digests": {
            "package": "sha256:artifact",
            "documentation": "sha256:docs",
        },
    }


def invalid_secret_manifest() -> dict[str, object]:
    manifest = deepcopy(valid_skill_manifest())
    manifest["support"] = {"api_token": "sk-thisshouldnotbehere123456"}
    return manifest


def invalid_entrypoint_manifest() -> dict[str, object]:
    manifest = deepcopy(valid_skill_manifest())
    manifest["entrypoint"] = {
        "type": "python",
        "approved_integration_ref": "exec:unsafe",
    }
    return manifest
