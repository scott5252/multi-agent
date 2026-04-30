from __future__ import annotations

from prometheus_client import Counter, Histogram

VALIDATION_ATTEMPTS = Counter(
    "skill_registry_validation_attempts_total",
    "Skill package validation attempts.",
    ("outcome",),
)
VALIDATION_DURATION = Histogram(
    "skill_registry_validation_duration_seconds",
    "Skill package validation duration.",
    ("outcome",),
)
PUBLICATION_OUTCOMES = Counter(
    "skill_registry_publication_outcomes_total",
    "Skill package publication outcomes.",
    ("outcome",),
)
INSTALL_OUTCOMES = Counter(
    "skill_registry_install_outcomes_total",
    "Tenant skill installation outcomes.",
    ("outcome",),
)


def record_validation_attempt(outcome: str, duration_seconds: float) -> None:
    VALIDATION_ATTEMPTS.labels(outcome=outcome).inc()
    VALIDATION_DURATION.labels(outcome=outcome).observe(duration_seconds)


def record_publication_outcome(outcome: str) -> None:
    PUBLICATION_OUTCOMES.labels(outcome=outcome).inc()


def record_install_outcome(outcome: str) -> None:
    INSTALL_OUTCOMES.labels(outcome=outcome).inc()
