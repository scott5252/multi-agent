from __future__ import annotations

from pydantic import BaseModel, Field


class Principal(BaseModel):
    principal_id: str = "system"
    actor_type: str = "system"
    roles: tuple[str, ...] = Field(default_factory=lambda: ("platform",))
    auth_enabled: bool = False

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles or "platform" in self.roles
