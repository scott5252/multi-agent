from __future__ import annotations

from pathlib import Path


def test_skill_execution_gateway_contract_covers_runtime_and_diagnostics() -> None:
    contract = Path(
        "specs/021-real-skill-tool-execution-connectors/contracts/"
        "skill-execution-gateway.openapi.yaml"
    ).read_text(encoding="utf-8")

    for topic in (
        "/admin/skill-execution/api/diagnostics",
        "/admin/skill-execution/api/diagnostics/run",
        "SkillToolExecutionResult",
        "SkillToolDiagnosticRecord",
        "policy_decisions",
        "mock",
        "live_probe",
    ):
        assert topic in contract
