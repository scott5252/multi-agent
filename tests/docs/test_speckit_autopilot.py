from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_autopilot_skill_command_and_workflow_exist() -> None:
    required = [
        ".agents/skills/speckit-autopilot/SKILL.md",
        ".agents/skills/speckit-autopilot-setup/SKILL.md",
        ".agents/skills/speckit-autopilot-setup/scripts/create_autopilot_spec.py",
        ".specify/templates/commands/autopilot.md",
        ".specify/workflows/speckit-autopilot/workflow.yml",
        "docs/speckit-autopilot.md",
        "scripts/qa/run_spec_qa.py",
        "scripts/qa/run_playwright_ui.py",
    ]

    for relative_path in required:
        path = ROOT / relative_path
        assert path.exists(), relative_path
        assert path.read_text(encoding="utf-8").strip()


def test_autopilot_command_documents_all_eight_phases() -> None:
    command = read(".specify/templates/commands/autopilot.md")

    expected_phases = [
        "Phase 1: Preflight",
        "Phase 2: Specify",
        "Phase 3: Clarify Auto",
        "Phase 4: Plan",
        "Phase 5: Tasks",
        "Phase 6: Analyze Auto",
        "Phase 7: Implement",
        "Phase 8: Validate",
    ]

    for phase in expected_phases:
        assert phase in command

    assert "review gate" not in command.lower()
    assert "run_playwright_ui.py" in command
    assert "run_spec_qa.py" in command


def test_autopilot_workflow_is_registered_without_review_gates() -> None:
    registry = json.loads(read(".specify/workflows/workflow-registry.json"))
    assert "speckit-autopilot" in registry["workflows"]

    codex_manifest = json.loads(read(".specify/integrations/codex.manifest.json"))
    assert ".agents/skills/speckit-autopilot/SKILL.md" in codex_manifest["files"]

    workflow = read(".specify/workflows/speckit-autopilot/workflow.yml")
    assert "speckit.autopilot" in workflow
    assert "type: gate" not in workflow


def test_example_autopilot_files_are_portable_json_yaml() -> None:
    example_dir = ROOT / "specs/_autopilot/example"
    for filename in ("autopilot.yml", "policy.yml", "validation.yml"):
        data = json.loads((example_dir / filename).read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"

    manifest = json.loads((example_dir / "autopilot.yml").read_text(encoding="utf-8"))
    assert manifest["prompt_files"] == ["prompt.md"]
    assert manifest["policy_file"] == "policy.yml"
    assert manifest["validation_file"] == "validation.yml"


def test_spec_015_uses_shared_autopilot_defaults() -> None:
    policy = json.loads(
        read("specs/_autopilot/015-agent-workflow-test-bench/policy.yml")
    )
    validation = json.loads(
        read("specs/_autopilot/015-agent-workflow-test-bench/validation.yml")
    )

    assert policy["extends"] == "../shared/policy.base.yml"
    assert validation["extends"] == "../shared/validation.base.yml"
    assert policy["variables"]["qa_database"] == "multi_agent_platform_qa015"
    assert validation["variables"]["qa_id"] == "qa015"
    assert "playwright" in validation


def test_qa_runners_support_dry_run_from_validation_file() -> None:
    validation_file = ROOT / "specs/_autopilot/example/validation.yml"

    api_result = subprocess.run(
        [
            sys.executable,
            "scripts/qa/run_spec_qa.py",
            str(validation_file),
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert api_result.returncode == 0, api_result.stderr
    assert api_result.stdout.index("confirm-python") < api_result.stdout.index(
        "start api"
    )
    assert api_result.stdout.index("start api") < api_result.stdout.index("health-live")
    assert "health-live" in api_result.stdout
    assert "pytest-coverage" in api_result.stdout

    ui_result = subprocess.run(
        [
            sys.executable,
            "scripts/qa/run_playwright_ui.py",
            str(validation_file),
            "--dry-run",
            "--start-processes",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ui_result.returncode == 0, ui_result.stderr
    assert "start api" in ui_result.stdout
    assert "local-login-smoke" in ui_result.stdout
    assert "Playwright dry run completed" in ui_result.stdout


def test_autopilot_setup_script_scaffolds_thin_spec_files(tmp_path: Path) -> None:
    config_path = tmp_path / "spec-setup.json"
    config_path.write_text(
        json.dumps(
            {
                "spec_number": "099",
                "title": "Example Review Console",
                "prompts": {
                    "specify": "/speckit.specify Build the example review console.",
                    "plan": "/speckit.plan Plan the example review console.",
                    "tasks": "/speckit.tasks Create implementation tasks.",
                },
                "playwright": {
                    "path": "/admin/example-review/ui",
                    "expected_text": "Example Review",
                },
                "extra_commands": [
                    {
                        "id": "example-review-health",
                        "command": "curl --fail --silent http://127.0.0.1:8000/admin/example-review/ui",
                        "expect_exit_code": 0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            ".agents/skills/speckit-autopilot-setup/scripts/create_autopilot_spec.py",
            "--config",
            str(config_path),
            "--repo-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    spec_dir = tmp_path / "specs/_autopilot/099-example-review-console"
    assert spec_dir.exists()

    for filename in (
        "autopilot.yml",
        "specify.md",
        "plan.md",
        "tasks.md",
        "policy.yml",
        "validation.yml",
    ):
        assert (spec_dir / filename).exists(), filename

    policy = json.loads((spec_dir / "policy.yml").read_text(encoding="utf-8"))
    validation = json.loads((spec_dir / "validation.yml").read_text(encoding="utf-8"))

    assert policy["extends"] == "../shared/policy.base.yml"
    assert validation["extends"] == "../shared/validation.base.yml"
    assert validation["variables"]["qa_database"] == "multi_agent_platform_qa099"
    assert (
        validation["playwright"]["flows"][0]["id"] == "example-review-console-ui-login"
    )
    assert validation["extra_commands"][0]["id"] == "example-review-health"


def test_spec_015_validation_resolves_shared_defaults() -> None:
    validation_file = (
        ROOT / "specs/_autopilot/015-agent-workflow-test-bench/validation.yml"
    )

    api_result = subprocess.run(
        [
            sys.executable,
            "scripts/qa/run_spec_qa.py",
            str(validation_file),
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert api_result.returncode == 0, api_result.stderr
    assert "multi_agent_platform_qa015" in api_result.stdout
    assert "manual-qa-user-guide-required" in api_result.stdout
    assert "qa015_user_guide.md" in api_result.stdout

    ui_result = subprocess.run(
        [
            sys.executable,
            "scripts/qa/run_playwright_ui.py",
            str(validation_file),
            "--dry-run",
            "--start-processes",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert ui_result.returncode == 0, ui_result.stderr
    assert "agent-test-bench-ui-login" in ui_result.stdout
    assert "output/playwright/qa015_ui" not in ui_result.stdout
