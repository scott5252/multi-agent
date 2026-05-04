from __future__ import annotations

from multi_agent_platform.skill_execution.redaction import (
    redact_payload,
    redact_text,
    summarize_payload,
)


def test_redact_text_removes_tokens_emails_and_sensitive_queries() -> None:
    redacted = redact_text(
        "Bearer sk-live-secret for scott@example.com at "
        "https://provider.example/search?q=private&api_key=secret"
    )

    assert "sk-live-secret" not in redacted
    assert "scott@example.com" not in redacted
    assert "api_key=secret" not in redacted
    assert "[redacted-token]" in redacted
    assert "[redacted-email]" in redacted


def test_redact_payload_masks_sensitive_keys_and_nested_values() -> None:
    payload = {
        "access_token": "secret-token",
        "messages": [
            {
                "sender": "Sarah <sarah@example.com>",
                "body": "launch detail",
                "url": "https://mail.example/message?id=1&token=secret",
            }
        ],
    }

    redacted = redact_payload(payload)

    assert redacted["access_token"] == "[redacted]"
    message = redacted["messages"][0]
    assert message["sender"] == "Sarah <[redacted-email]>"
    assert message["body"] == "[redacted]"
    assert "token=secret" not in message["url"]


def test_summarize_payload_is_bounded_and_redacted() -> None:
    summary = summarize_payload(
        "gmail.messages.read",
        {
            "messages": [
                {
                    "sender": "vip@example.com",
                    "subject": "Launch date moved",
                    "body": "very private body",
                }
            ]
        },
    )

    assert "1 message" in summary
    assert "vip@example.com" not in summary
    assert "very private body" not in summary
