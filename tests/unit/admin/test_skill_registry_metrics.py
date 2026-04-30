from __future__ import annotations

from multi_agent_platform.admin.skill_registry.metrics import (
    record_install_outcome,
    record_publication_outcome,
    record_validation_attempt,
)


def test_skill_registry_metrics_record_without_sensitive_labels() -> None:
    record_validation_attempt("passed", 0.01)
    record_publication_outcome("published")
    record_install_outcome("installed")
