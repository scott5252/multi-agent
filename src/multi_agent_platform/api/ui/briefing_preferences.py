from __future__ import annotations

from pydantic import BaseModel

from multi_agent_platform.api.schemas.briefing_preferences import (
    BriefingPreferenceResponse,
    BriefingPreferenceSummaryResponse,
)


class BriefingPreferencesPage(BaseModel):
    title: str = "Briefing Preferences"
    profile: BriefingPreferenceResponse | None
    summaries: tuple[BriefingPreferenceSummaryResponse, ...] = ()
    conflict: bool = False
    error_message: str | None = None
    can_edit: bool = True

    @property
    def profile_ready_label(self) -> str:
        return "Ready" if self.profile is not None else "Not configured"

    @property
    def topic_text(self) -> str:
        if self.profile is None:
            return "AI, markets, product launches"
        return ", ".join(self.profile.news_topics)

    @property
    def vip_text(self) -> str:
        if self.profile is None:
            return "product lead, legal team"
        return ", ".join(self.profile.vip_senders)


def redaction_notice() -> str:
    return (
        "Admin summaries show safe counts, masked sender hints, reference "
        "labels, revision metadata, and timestamps only. Raw credentials, "
        "tokens, and private account values are never rendered."
    )
