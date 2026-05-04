from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceRuntimeContext,
    BriefingPreferenceService,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)


async def resolve_briefing_preferences(
    *,
    repository: BriefingPreferenceRepository,
    tenant_id: UUID,
    principal_id: str,
    source_channel: str,
    trace_id: str | None,
) -> BriefingPreferenceRuntimeContext:
    return await BriefingPreferenceService(repository).resolve_runtime_context(
        tenant_id=tenant_id,
        principal_id=principal_id,
        source_channel=source_channel,
        trace_id=trace_id,
    )
