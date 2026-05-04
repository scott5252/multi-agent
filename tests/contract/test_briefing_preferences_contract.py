from __future__ import annotations

from pathlib import Path


def test_briefing_preferences_contract_documents_required_surfaces() -> None:
    contract = Path(
        "specs/023-user-briefing-preferences-and-context/contracts/"
        "briefing-preferences.md"
    ).read_text(encoding="utf-8")

    for path in (
        "/admin/briefing-preferences",
        "/admin/briefing-preferences/api/profile",
        "/admin/briefing-preferences/api/summaries",
        "/admin/briefing-preferences/api/export",
        "/admin/briefing-preferences/api/import",
        "/admin/briefing-preferences/api/resolve",
    ):
        assert path in contract
    assert "Runtime Resolver" in contract
    assert "raw VIP senders" in contract
