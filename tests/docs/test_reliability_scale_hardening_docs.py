from __future__ import annotations

from pathlib import Path


def test_operator_guidance_covers_required_reliability_topics() -> None:
    text = Path("docs/reliability-scale-hardening.md").read_text()
    for topic in (
        "Backpressure",
        "Quotas",
        "Recovery",
        "Compensation",
        "Breakers",
        "Dead Letters",
        "Incident Escalation",
    ):
        assert topic in text
