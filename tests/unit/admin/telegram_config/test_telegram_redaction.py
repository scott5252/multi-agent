from __future__ import annotations

from multi_agent_platform.admin.telegram_config.redaction import (
    fingerprint_value,
    mask_identifier,
    safe_reference_label,
    sanitize_metadata,
    sanitize_text,
)


def test_telegram_redaction_masks_identifiers_and_secret_markers() -> None:
    assert mask_identifier("123456789") == "123***789"
    assert "super-secret" not in sanitize_text("super-secret token")
    assert safe_reference_label("env:TELEGRAM_TOKEN") == "env:***"
    assert safe_reference_label("actual-token-value") == "configured value redacted"
    assert fingerprint_value("token") != "token"


def test_telegram_metadata_redacts_sensitive_keys() -> None:
    metadata = sanitize_metadata(
        {"webhook_secret": "abc", "attempt": 1, "status": "ok"}
    )

    assert metadata["webhook_secret"] == "redacted"
    assert metadata["attempt"] == 1
    assert metadata["status"] == "ok"
