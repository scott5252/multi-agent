from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_patterns import (
    ExportSnapshot,
    SafeProblemDetail,
    ValidationFieldError,
    redacted_dict,
)


def test_safe_problem_rejects_raw_payload_markers() -> None:
    problem = SafeProblemDetail(
        title="Validation needed",
        status=400,
        detail="Review the highlighted fields.",
        reason_category="validation_error",
        field_errors=(
            ValidationFieldError(
                field="sample_name",
                label="Sample name",
                message="Enter a sample name.",
                code="required",
            ),
        ),
    )

    assert problem.field_errors[0].message == "Enter a sample name."

    with pytest.raises(ValidationError):
        SafeProblemDetail(
            title="Traceback from provider payload",
            status=500,
            detail="unsafe",
            reason_category="unexpected_error",
        )


def test_export_snapshot_rejects_filesystem_paths() -> None:
    snapshot = ExportSnapshot(
        export_id="sample-export",
        status="complete",
        summary="Safe artifact reference is ready.",
        artifact_reference_id="artifact-ref-qa028",
    )

    assert snapshot.artifact_reference_id == "artifact-ref-qa028"

    with pytest.raises(ValidationError):
        ExportSnapshot(
            export_id="unsafe",
            status="complete",
            summary="Safe summary",
            artifact_reference_id="/Users/scott/raw.csv",
        )


def test_redacted_dict_drops_secret_like_values() -> None:
    payload = redacted_dict(
        {
            "safe": "visible",
            "secret": "sk-test-hidden",
            "count": 2,
            "nested": {"raw": "payload"},
        }
    )

    assert payload == {"safe": "visible", "count": 2}
