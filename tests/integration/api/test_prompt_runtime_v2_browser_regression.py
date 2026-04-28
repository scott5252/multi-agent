from __future__ import annotations

from pathlib import Path


def test_admin_run_detail_template_has_gateway_metadata_unavailable_state() -> None:
    template = Path(
        "src/multi_agent_platform/web_admin/templates/runs/detail.html"
    ).read_text()

    assert "pre_v2_metadata_unavailable" in template
    assert "gateway_operation_id" in template


def test_prompt_runtime_script_allows_intentional_form_submits() -> None:
    script = Path(
        "src/multi_agent_platform/web_admin/static/prompt_runtime.js"
    ).read_text()

    assert 'document.addEventListener("submit"' in script
    assert "delete form.dataset.dirty" in script
    assert 'form.dataset.submitting = "true"' in script
    assert ":not([data-submitting='true'])" in script
