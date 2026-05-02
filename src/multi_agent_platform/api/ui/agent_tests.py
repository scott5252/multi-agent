from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from multi_agent_platform.api.schemas.agent_tests import (
    AgentTestRunResponse,
    AgentTestSuiteResponse,
)


class AgentTestIndexPage(BaseModel):
    title: str = "Agent Tests"
    suites: list[AgentTestSuiteResponse] = Field(default_factory=list)
    create_href: str = "/admin/agent-tests/ui/suites/new"
    tenant_id: str | None = None


class AgentTestSuitePage(BaseModel):
    title: str
    suite: AgentTestSuiteResponse
    cases: list[dict[str, Any]] = Field(default_factory=list)
    runs: list[AgentTestRunResponse] = Field(default_factory=list)
    gate_status: dict[str, Any] = Field(default_factory=dict)


class AgentTestRunPage(BaseModel):
    title: str
    run: AgentTestRunResponse


def redaction_notice() -> str:
    return (
        "Sensitive fixtures, prompts, provider messages, credentials, tool "
        "payloads, and transcripts are redacted from this page."
    )
