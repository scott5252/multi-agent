from __future__ import annotations

from pathlib import Path

TEST_BENCH_TEMPLATE_PATHS = (
    "src/multi_agent_platform/web_admin/templates/agent_tests/index.html",
    "src/multi_agent_platform/web_admin/templates/agent_tests/suite_form.html",
    "src/multi_agent_platform/web_admin/templates/agent_tests/suite_detail.html",
    "src/multi_agent_platform/web_admin/templates/agent_tests/case_form.html",
    "src/multi_agent_platform/web_admin/templates/agent_tests/run_detail.html",
    (
        "src/multi_agent_platform/web_admin/templates/agent_tests/components/"
        "assertions.html"
    ),
    (
        "src/multi_agent_platform/web_admin/templates/agent_tests/components/"
        "gate_status.html"
    ),
    (
        "src/multi_agent_platform/web_admin/templates/agent_tests/components/"
        "result_summary.html"
    ),
    (
        "src/multi_agent_platform/web_admin/templates/agent_tests/components/"
        "trace_steps.html"
    ),
)

TEST_BENCH_BROWSER_ROUTER_PATHS = (
    "src/multi_agent_platform/api/routers/admin_agent_tests.py",
)


def test_test_bench_owned_templates_are_deleted() -> None:
    for path in TEST_BENCH_TEMPLATE_PATHS:
        assert not Path(path).exists(), path


def test_test_bench_browser_router_does_not_render_templates() -> None:
    for path in TEST_BENCH_BROWSER_ROUTER_PATHS:
        text = Path(path).read_text(encoding="utf-8")
        assert "TemplateResponse" not in text
        assert "workflow_ui_templates" not in text
        assert "agent_tests/" not in text
