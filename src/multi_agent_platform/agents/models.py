from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ProfileValidationStatus = Literal["passed", "failed"]
FindingSeverity = Literal["blocking", "advisory"]


@dataclass(frozen=True, slots=True)
class ProfileValidationFinding:
    code: str
    severity: FindingSeverity
    message: str
    section: str

    def to_json(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "section": self.section,
        }


@dataclass(frozen=True, slots=True)
class ProfileValidationReport:
    status: ProfileValidationStatus
    findings: tuple[ProfileValidationFinding, ...] = field(default_factory=tuple)

    @property
    def blocking_issue_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "blocking")

    def to_json_findings(self) -> list[dict[str, object]]:
        return [finding.to_json() for finding in self.findings]
