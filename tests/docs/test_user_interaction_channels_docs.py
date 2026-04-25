from __future__ import annotations

from pathlib import Path


def test_user_interaction_channel_review_docs_are_present() -> None:
    required = [
        Path("docs/user-interaction-channels.md"),
        Path("specs/006-user-interaction-channels/testing-instructions.md"),
        Path("specs/006-user-interaction-channels/pr-review-notes.md"),
        Path("specs/006-user-interaction-channels/qa006.md"),
    ]

    for path in required:
        text = path.read_text()
        assert "Web UI" in text
        assert "Telegram" in text
        assert "Web API" in text
        assert "artifact" in text.lower()
