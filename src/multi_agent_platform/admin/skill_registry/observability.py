from __future__ import annotations

import logging
from dataclasses import dataclass, field

from multi_agent_platform.admin.skill_registry.audit import redact_for_audit

LOGGER = logging.getLogger("multi_agent_platform.skill_registry")


@dataclass(frozen=True, slots=True)
class SkillRegistryTraceContext:
    trace_id: str
    tenant_id: str | None = None
    package_slug: str | None = None
    package_version: str | None = None
    installation_id: str | None = None
    validation_job_id: str | None = None
    smoke_test_run_id: str | None = None
    extra: dict[str, object] = field(default_factory=dict)

    def labels(self) -> dict[str, str]:
        return {
            key: value
            for key, value in {
                "trace_id": self.trace_id,
                "tenant_id": self.tenant_id,
                "package_slug": self.package_slug,
                "package_version": self.package_version,
                "installation_id": self.installation_id,
                "validation_job_id": self.validation_job_id,
                "smoke_test_run_id": self.smoke_test_run_id,
            }.items()
            if value is not None
        }


def safe_log_context(context: SkillRegistryTraceContext) -> dict[str, object]:
    return {**context.labels(), "extra": redact_for_audit(context.extra)}


def log_lifecycle_event(
    message: str,
    *,
    context: SkillRegistryTraceContext,
    level: int = logging.INFO,
) -> None:
    LOGGER.log(level, message, extra={"skill_registry": safe_log_context(context)})
