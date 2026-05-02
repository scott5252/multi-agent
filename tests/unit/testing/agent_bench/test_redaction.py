from __future__ import annotations

from multi_agent_platform.testing.agent_bench.redaction import (
    REDACTED,
    redact_value,
    safe_artifact_summary,
    safe_fixture_summary,
    safe_transcript_summary,
)


def test_fixture_summary_redacts_sensitive_keys_and_values() -> None:
    summary = safe_fixture_summary(
        {
            "request": "summarize intake",
            "api_key": "qa015-secret-value",
            "nested": {"prompt": "raw prompt body"},
        }
    )

    assert summary["fields"] == ["api_key", "nested", "request"]
    assert summary["preview"]["api_key"] == REDACTED
    assert summary["preview"]["nested"]["prompt"] == REDACTED
    assert summary["redacted"] is True


def test_transcript_summary_is_bounded_and_redacted() -> None:
    summary = safe_transcript_summary(
        [{"role": "user", "content": f"message {index}"} for index in range(7)]
        + [{"role": "assistant", "token": "secret-token"}]
    )

    assert summary["message_count"] == 8
    assert summary["truncated"] is True
    assert len(summary["messages"]) == 5


def test_redaction_handles_empty_fixtures_sequences_and_artifact_metadata() -> None:
    empty = safe_fixture_summary({})
    redacted = redact_value(
        {
            "items": ("public", "token should hide"),
            "long": "x" * 220,
        },
        max_string_length=12,
    )
    artifact = safe_artifact_summary(
        artifact_type="transcript",
        storage_uri="fs://qa015/transcript.json",
        checksum_sha256="abc123",
        size_bytes=123,
    )
    inline = safe_artifact_summary(
        artifact_type="result",
        storage_uri=None,
        checksum_sha256=None,
        size_bytes=None,
    )

    assert empty == {"fields": [], "redacted": False}
    assert redacted["items"][1] == REDACTED
    assert redacted["long"].endswith("...")
    assert artifact["storage_ref"] == "available"
    assert inline["storage_ref"] == "inline"
