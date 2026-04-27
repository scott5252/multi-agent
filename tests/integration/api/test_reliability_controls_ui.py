from __future__ import annotations

from multi_agent_platform.api.ui.reliability_controls import reliability_template


def test_reliability_ui_templates_exist() -> None:
    assert reliability_template("index.html").exists()
    assert reliability_template("breakers.html").exists()
    assert reliability_template("dead_letters.html").exists()
