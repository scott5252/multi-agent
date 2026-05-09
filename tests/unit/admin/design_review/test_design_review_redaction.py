from __future__ import annotations

import pytest

from multi_agent_platform.admin.design_review.redaction import (
    UnsafeDesignReviewContentError,
    digest_safe_text,
    safe_metadata,
    validate_safe_text,
)


def test_validate_safe_text_normalizes_whitespace() -> None:
    assert validate_safe_text("  review   summary  ", field_name="summary") == (
        "review summary"
    )


@pytest.mark.parametrize(
    "value",
    [
        "Authorization: Bearer secret-token",
        "sk-testsecretsecret",
        "-----BEGIN PRIVATE KEY-----",
        "raw_prompt: hidden",
    ],
)
def test_validate_safe_text_blocks_protected_content(value: str) -> None:
    with pytest.raises(UnsafeDesignReviewContentError):
        validate_safe_text(value, field_name="summary")


def test_digest_safe_text_is_stable() -> None:
    assert digest_safe_text("summary") == digest_safe_text("summary")
    assert digest_safe_text("summary") != digest_safe_text("other")


def test_validate_safe_text_requires_non_empty_and_bounded_values() -> None:
    with pytest.raises(UnsafeDesignReviewContentError):
        validate_safe_text("   ", field_name="summary")

    with pytest.raises(UnsafeDesignReviewContentError):
        validate_safe_text("x" * 4001, field_name="summary")


def test_safe_metadata_normalizes_scalars_and_blocks_unsafe_values() -> None:
    metadata = safe_metadata(
        {
            " reviewer ": " approved   with notes ",
            "score": 5,
            "accepted": True,
            "ratio": 0.75,
            "none": None,
            "list": ["safe", "items"],
        }
    )

    assert metadata == {
        "reviewer": "approved with notes",
        "score": 5,
        "accepted": True,
        "ratio": 0.75,
        "none": None,
        "list": "['safe', 'items']",
    }

    with pytest.raises(UnsafeDesignReviewContentError):
        safe_metadata({"Authorization:": "hidden"})
