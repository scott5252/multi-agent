from __future__ import annotations

from time import perf_counter

from multi_agent_platform.prompts.template import parse_template_variables


def test_prompt_runtime_template_validation_smoke_latency() -> None:
    template = "\n".join(f"Hello {{{{name_{index}}}}}" for index in range(100))

    started = perf_counter()
    placeholders = parse_template_variables(template)
    elapsed_ms = (perf_counter() - started) * 1000

    assert len(placeholders) == 100
    assert elapsed_ms < 100
