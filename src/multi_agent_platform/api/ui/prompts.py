from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PromptUiFinding:
    code: str
    severity: str
    message: str
    field: str | None = None


@dataclass(frozen=True, slots=True)
class PromptUiModel:
    title: str
    scope_type: str
    tenant_id: UUID | None = None
    prompt_lineage_id: UUID | None = None
    prompt_version_id: UUID | None = None
    current_revision_number: int = 0
    can_publish: bool = False
    can_preview: bool = False
    can_retire: bool = False
    findings: tuple[PromptUiFinding, ...] = field(default_factory=tuple)
    preview_redaction_categories: tuple[str, ...] = field(default_factory=tuple)
    submitted_fields: dict[str, object] = field(default_factory=dict)


def build_prompt_ui_model(
    *,
    title: str,
    scope_type: str,
    tenant_id: UUID | None = None,
    prompt_lineage_id: UUID | None = None,
    prompt_version_id: UUID | None = None,
    current_revision_number: int = 0,
    validation_status: str | None = None,
    required_fixture_missing: bool = False,
    status: str = "draft",
    findings: list[dict[str, object]] | None = None,
    submitted_fields: dict[str, object] | None = None,
) -> PromptUiModel:
    ui_findings = tuple(
        PromptUiFinding(
            code=str(item.get("code", "validation")),
            severity=str(item.get("severity", "blocking")),
            message=str(item.get("message", "Validation issue")),
            field=str(item["field"]) if item.get("field") else None,
        )
        for item in findings or []
    )
    can_publish = validation_status == "passed" and status == "draft"
    return PromptUiModel(
        title=title,
        scope_type=scope_type,
        tenant_id=tenant_id,
        prompt_lineage_id=prompt_lineage_id,
        prompt_version_id=prompt_version_id,
        current_revision_number=current_revision_number,
        can_publish=can_publish,
        can_preview=not required_fixture_missing and status == "draft",
        can_retire=status == "active",
        findings=ui_findings,
        submitted_fields=submitted_fields or {},
    )
