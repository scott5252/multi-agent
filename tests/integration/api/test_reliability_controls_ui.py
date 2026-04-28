from __future__ import annotations

from multi_agent_platform.api.ui.reliability_controls import (
    reliability_breakers_filter_profile,
    reliability_dead_letters_filter_profile,
    reliability_template,
)


def test_reliability_ui_templates_exist() -> None:
    assert reliability_template("index.html").exists()
    assert reliability_template("breakers.html").exists()
    assert reliability_template("dead_letters.html").exists()


def test_reliability_filter_profiles_point_to_shell_destinations() -> None:
    assert (
        reliability_breakers_filter_profile().destination_href
        == "/admin/reliability/ui/breakers"
    )
    assert (
        reliability_dead_letters_filter_profile().destination_href
        == "/admin/reliability/ui/dead-letters"
    )
