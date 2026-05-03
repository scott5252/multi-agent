from __future__ import annotations

from pathlib import Path


def test_agent_test_bench_contract_documents_required_routes() -> None:
    contract = Path(
        "specs/015-agent-workflow-test-bench/contracts/agent-test-bench.openapi.yaml"
    ).read_text()

    for path in (
        "/admin/agent-tests/suites",
        "/admin/agent-tests/suites/{suite_id}/cases",
        "/admin/agent-tests/suites/{suite_id}/runs",
        "/admin/agent-tests/runs/{run_id}",
        "/admin/agent-tests/publish-gates/evaluate",
    ):
        assert path in contract
