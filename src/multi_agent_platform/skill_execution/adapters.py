from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.skill_execution.fixtures import fixture_for_tool
from multi_agent_platform.skill_execution.redaction import summarize_payload
from multi_agent_platform.skill_execution.schemas import (
    AdapterExecutionResult,
    ExecutionMode,
    SkillToolExecutionRequest,
)

DAILY_BRIEFING_TOOL_NAMES: tuple[str, ...] = (
    "google_calendar.events.read",
    "gmail.messages.read",
    "news.search",
    "weather.forecast.read",
    "commute.lookup",
)


@dataclass(slots=True)
class SkillToolAdapter:
    tool_name: str
    display_name: str
    skill_package: str
    required_credential_kind: str
    allowed_domains: tuple[str, ...]
    read_only: bool = True
    action_category: str = "read"
    contract_version: str = "v1"
    invocation_count: int = 0

    async def execute(
        self,
        request: SkillToolExecutionRequest,
    ) -> AdapterExecutionResult:
        self.invocation_count += 1
        payload = fixture_for_tool(self.tool_name, request.input)
        if request.execution_mode is ExecutionMode.LIVE_PROBE:
            payload = {
                **payload,
                "live_probe": {
                    "status": "adapter_interface_ready",
                    "provider_payload_stored_inline": False,
                },
            }
        output = {"contract_version": self.contract_version, **payload}
        return AdapterExecutionResult(
            tool_name=self.tool_name,
            contract_version=self.contract_version,
            output=output,
            response_summary=summarize_payload(self.tool_name, output),
        )


def default_adapter_registry() -> dict[str, SkillToolAdapter]:
    adapters = (
        SkillToolAdapter(
            tool_name="google_calendar.events.read",
            display_name="Google Calendar Events",
            skill_package="daily-briefing-calendar",
            required_credential_kind="google_calendar_oauth",
            allowed_domains=("www.googleapis.com", "calendar.googleapis.com"),
        ),
        SkillToolAdapter(
            tool_name="gmail.messages.read",
            display_name="Gmail Messages",
            skill_package="daily-briefing-gmail",
            required_credential_kind="gmail_oauth",
            allowed_domains=("gmail.googleapis.com", "www.googleapis.com"),
        ),
        SkillToolAdapter(
            tool_name="news.search",
            display_name="News Search",
            skill_package="daily-briefing-news",
            required_credential_kind="news_api_key",
            allowed_domains=("news.example", "api.search.example"),
        ),
        SkillToolAdapter(
            tool_name="weather.forecast.read",
            display_name="Weather Forecast",
            skill_package="daily-briefing-weather",
            required_credential_kind="weather_api_key",
            allowed_domains=("weather.example", "api.weather.example"),
        ),
        SkillToolAdapter(
            tool_name="commute.lookup",
            display_name="Commute Lookup",
            skill_package="daily-briefing-commute",
            required_credential_kind="traffic_api_key",
            allowed_domains=("traffic.example", "maps.googleapis.com"),
        ),
    )
    return {adapter.tool_name: adapter for adapter in adapters}
