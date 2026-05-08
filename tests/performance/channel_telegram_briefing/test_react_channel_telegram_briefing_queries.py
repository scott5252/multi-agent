from __future__ import annotations

from tests.fixtures.channel_telegram_briefing import (
    ACME_TENANT_ID,
    seed_channel_telegram_briefing_live_data,
)

from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
)
from multi_agent_platform.admin.channel_telegram_briefing import (
    build_channel_telegram_briefing_dashboard,
    build_delivery_diagnostics,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)


async def test_react_channel_builders_return_bounded_collections(
    session,
    settings,
) -> None:
    await seed_channel_telegram_briefing_live_data(session)
    telegram_repository = TelegramConfigRepository(session)
    briefing_repository = BriefingPreferenceRepository(session)
    channel_repository = ChannelRepository(session)
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        role_codes=("tenant_user", "tenant_admin"),
        tenant_id=ACME_TENANT_ID,
    )
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=ACME_TENANT_ID,
        label="Acme",
    )

    dashboard = await build_channel_telegram_briefing_dashboard(
        telegram_repository=telegram_repository,
        telegram_service=TelegramConfigurationService(
            repository=telegram_repository,
            settings=settings,
            channel_service=ChannelService(settings=settings),
        ),
        briefing_repository=briefing_repository,
        briefing_service=BriefingPreferenceService(briefing_repository),
        channel_repository=channel_repository,
        runtime_repository=RuntimeOrchestrationRepository(session),
        scope=scope,
        principal=principal,
    )
    diagnostics = await build_delivery_diagnostics(
        telegram_repository=telegram_repository,
        channel_repository=channel_repository,
        scope=scope,
        principal=principal,
    )

    assert len(dashboard.aliases) <= 25
    assert len(dashboard.delivery_attempts) <= 25
    assert diagnostics.limit == 25
