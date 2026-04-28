from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from multi_agent_platform.model_providers.gateway import ModelGateway
    from multi_agent_platform.model_providers.service import ModelProviderService

__all__ = ["ModelGateway", "ModelProviderService"]
