from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResearchFinding(BaseModel):
    source_url: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class AgentHandoffEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_run_id: str
    from_agent: str
    to_agent: str
    contract_name: str
    contract_version: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    trace_id: str
    payload: dict[str, Any]


class ResearchCompletedPayload(BaseModel):
    topic: str
    findings: list[ResearchFinding]
    overall_confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("findings")
    @classmethod
    def findings_must_not_be_empty(cls, value: list[ResearchFinding]) -> list[ResearchFinding]:
        if not value:
            raise ValueError("at least one research finding is required")
        return value

    @field_validator("overall_confidence")
    @classmethod
    def confidence_must_meet_gate(cls, value: float) -> float:
        if value < 0.70:
            raise ValueError("handoff rejected because confidence is below 0.70")
        return value


def validate_research_handoff(envelope: AgentHandoffEnvelope) -> ResearchCompletedPayload:
    if envelope.contract_name != "research_completed":
        raise ValueError("unexpected contract for research handoff")

    return ResearchCompletedPayload.model_validate(envelope.payload)
