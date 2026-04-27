from __future__ import annotations

from tests.fixtures.reliability import FAILURE_INJECTION_POINTS


def test_resume_after_failure_covers_required_injection_points() -> None:
    assert "after_claim" in FAILURE_INJECTION_POINTS
    assert "during_artifact_export" in FAILURE_INJECTION_POINTS
    assert len(FAILURE_INJECTION_POINTS) == 7
