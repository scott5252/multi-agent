from __future__ import annotations

from uuid import UUID


def prompt_audit_summary(
    *,
    action: str,
    prompt_lineage_id: UUID | None,
    prompt_version_id: UUID | None,
    outcome: str,
    finding_codes: tuple[str, ...] = (),
    redaction_categories: tuple[str, ...] = (),
) -> dict[str, object]:
    summary: dict[str, object] = {
        "action": action,
        "outcome": outcome,
        "finding_codes": list(finding_codes),
        "redaction_categories": list(redaction_categories),
    }
    if prompt_lineage_id is not None:
        summary["prompt_lineage_id"] = str(prompt_lineage_id)
    if prompt_version_id is not None:
        summary["prompt_version_id"] = str(prompt_version_id)
    return summary
