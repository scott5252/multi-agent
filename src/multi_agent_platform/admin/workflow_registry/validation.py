from __future__ import annotations

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument


def validate_authoring_document(
    document: WorkflowDraftDocument,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if not document.roles:
        findings.append(
            {
                "category": "roles",
                "severity": "advisory",
                "message": "Draft has no roles yet; this is allowed during authoring.",
            }
        )
    return findings
