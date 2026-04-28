from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ValidationStatus = Literal["passed", "failed"]
FindingSeverity = Literal["blocking", "advisory"]


@dataclass(frozen=True, slots=True)
class PromptVariableDeclaration:
    name: str
    purpose: str
    required: bool = True
    allowed_value_category: str = "synthetic"
    safety_classification: str = "safe_fixture"
    sample_guidance: str = ""
    display_order: int = 0

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "required": self.required,
            "allowed_value_category": self.allowed_value_category,
            "safety_classification": self.safety_classification,
            "sample_guidance": self.sample_guidance,
            "display_order": self.display_order,
        }


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    code: str
    severity: FindingSeverity
    message: str
    field: str | None = None

    def to_json(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
        }
        if self.field is not None:
            payload["field"] = self.field
        return payload


@dataclass(frozen=True, slots=True)
class PromptValidationReport:
    status: ValidationStatus
    findings: tuple[ValidationFinding, ...] = field(default_factory=tuple)

    @property
    def blocking_issue_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "blocking")

    @property
    def advisory_issue_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "advisory")

    def to_json_findings(self) -> list[dict[str, object]]:
        return [finding.to_json() for finding in self.findings]


@dataclass(frozen=True, slots=True)
class SanitizedFixtureValues:
    values_by_variable: dict[str, str]
    redaction_categories: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PromptPreview:
    rendered_preview: str
    redaction_categories: tuple[str, ...] = ()
    missing_variables: tuple[str, ...] = ()
