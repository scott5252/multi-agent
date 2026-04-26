from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from multi_agent_platform.config.model_skill import ConfigKind, ModelSkillErrorCategory


class RollbackError(RuntimeError):
    def __init__(self, category: ModelSkillErrorCategory, message: str) -> None:
        super().__init__(message)
        self.category = category


@dataclass(frozen=True, slots=True)
class RollbackPlan:
    rollback_record_id: UUID
    config_kind: ConfigKind
    scope_hash: str
    from_version_id: UUID
    to_version_id: UUID
    reason: str


def plan_rollback(
    *,
    config_kind: ConfigKind,
    scope_hash: str,
    current_active_version_id: UUID,
    expected_active_version_id: UUID | None,
    target_version_id: UUID,
    target_scope_hash: str,
    reason: str,
) -> RollbackPlan:
    if expected_active_version_id is not None and (
        expected_active_version_id != current_active_version_id
    ):
        raise RollbackError(
            ModelSkillErrorCategory.STALE_CONFIGURATION,
            "active version changed since rollback was previewed",
        )
    if scope_hash != target_scope_hash:
        raise RollbackError(
            ModelSkillErrorCategory.VALIDATION_FAILED,
            "rollback target must belong to the same config kind and scope",
        )
    return RollbackPlan(
        rollback_record_id=uuid4(),
        config_kind=config_kind,
        scope_hash=scope_hash,
        from_version_id=current_active_version_id,
        to_version_id=target_version_id,
        reason=reason,
    )
