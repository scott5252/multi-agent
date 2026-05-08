#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

PHASES = ("specify", "clarify", "plan", "tasks", "analyze", "implement")
SPEC_RANGE = range(48, 60)


class RouteHint(NamedTuple):
    route: str
    expected_text: str
    principal: str


ROUTE_HINTS: dict[str, RouteHint] = {
    "048": RouteHint("/admin/app/migration", "Migration", "platform-admin"),
    "049": RouteHint("/admin/app", "Admin", "platform-admin"),
    "050": RouteHint("/admin/app/workflows", "Workflow", "tenant-admin-acme"),
    "051": RouteHint("/admin/app/governance", "Governance", "platform-admin"),
    "052": RouteHint("/admin/app/skills", "Skill", "platform-admin"),
    "053": RouteHint("/admin/app/test-bench", "Test Bench", "tenant-admin-acme"),
    "054": RouteHint("/admin/app/memberships", "Membership", "platform-admin"),
    "055": RouteHint("/admin/app/channels", "Channels", "tenant-admin-acme"),
    "056": RouteHint("/admin/app/usage", "Usage", "platform-admin"),
    "057": RouteHint("/admin/app/operations", "Operations", "platform-admin"),
    "058": RouteHint("/admin/app/migration", "Live", "platform-admin"),
    "059": RouteHint("/admin/app", "Admin", "platform-admin"),
}


@dataclass(frozen=True)
class RoadmapSpec:
    number: str
    title: str
    slug: str
    prompts: dict[str, str]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def extract_fenced_text(section: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)} Prompt\s*```text\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(section)
    if not match:
        raise SystemExit(f"missing prompt block: {heading}")
    return match.group(1).strip()


def extract_global_prefix(text: str) -> str:
    pattern = re.compile(
        r"^## Global Prompt Prefix\s*.*?```text\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit("missing Global Prompt Prefix block")
    return match.group(1).strip()


def extract_execution_notes(text: str) -> str:
    if "\n## Rollout Notes" in text:
        return text.split("\n## Rollout Notes", 1)[1].strip()
    if "\n## Execution Notes" in text:
        return text.split("\n## Execution Notes", 1)[1].strip()
    raise SystemExit("missing Rollout Notes or Execution Notes section")


def parse_specs(text: str) -> list[RoadmapSpec]:
    heading_pattern = re.compile(
        r"^## Spec (?P<number>\d{3}) - (?P<title>.+)$", re.MULTILINE
    )
    matches = list(heading_pattern.finditer(text))
    specs: list[RoadmapSpec] = []

    for index, match in enumerate(matches):
        number = match.group("number")
        if int(number) not in SPEC_RANGE:
            continue
        title = match.group("title").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        prompts = {
            phase: extract_fenced_text(section, phase.title()) for phase in PHASES
        }
        specs.append(
            RoadmapSpec(
                number=number,
                title=title,
                slug=slugify(title),
                prompts=prompts,
            )
        )

    expected = {f"{number:03d}" for number in SPEC_RANGE}
    actual = {spec.number for spec in specs}
    missing = sorted(expected - actual)
    if missing:
        raise SystemExit(f"missing specs in roadmap: {', '.join(missing)}")

    return sorted(specs, key=lambda spec: spec.number)


def render_phase_prompt(
    *,
    spec: RoadmapSpec,
    phase: str,
    global_prefix: str,
    execution_notes: str,
    roadmap_path: Path,
) -> str:
    feature_dir = f"specs/{spec.number}-{spec.slug}"
    branch = f"codex/{spec.number}-{spec.slug}"
    prompt = spec.prompts[phase]
    phase_title = phase.title()
    specify_hint = ""
    if phase == "specify":
        specify_hint = (
            f"\nSPECIFY_FEATURE_DIRECTORY={feature_dir}\nGIT_BRANCH_NAME={branch}\n"
        )

    autonomy = ""
    if phase == "clarify":
        autonomy = (
            "\n## Autonomous Clarification\n\n"
            "Use the recommended defaults in the roadmap and established repo "
            "patterns for low-risk answers. Record every auto-selected answer "
            "in spec.md with `(autopilot)`. Stop for security, tenant, audit, "
            "credential, destructive data, production resource, external "
            "side-effect, irreversible live-data deletion, compatibility route "
            "behavior, or approval/resume ambiguity.\n"
        )
    if phase == "analyze":
        autonomy = (
            "\n## Autonomous Analysis Handling\n\n"
            "After the read-only analysis report, remediate CRITICAL/HIGH "
            "findings only when the fix is explicit from the roadmap or local "
            "artifacts, then rerun analysis up to two loops. Do not implement "
            "with remaining CRITICAL findings.\n"
        )

    validation_contract = (
        "\n## Required Post-Spec Validation Contract\n\n"
        "After implementation, the active spec must pass QA document "
        "validation, `run_spec_qa.py`, Playwright UI validation, post-UI "
        "backend API or QA database verification, and the "
        "`multi-agent-curl-test` runner before the next spec starts. "
        "Playwright must exercise the UI; for safe mutation surfaces it must "
        "perform a user-visible action that writes through the backend and "
        "then verify persisted state through an API or redaction-safe QA "
        "database query. If any validation fails, fix only the active spec and "
        "rerun the failed command plus downstream checks.\n"
    )

    return (
        f"# Spec {spec.number} - {spec.title}: {phase_title}\n\n"
        f"Roadmap source: `{roadmap_path}`\n\n"
        "## Deterministic Targets\n\n"
        f"- Feature directory: `{feature_dir}`\n"
        f"- Git branch: `{branch}`\n"
        f"- QA id: `qa{spec.number}`\n"
        f"- QA database: `multi_agent_platform_qa{spec.number}`\n"
        f"- Post-spec curl-test database: `multi_agent_curl_test`\n"
        f"{specify_hint}\n"
        "## Global Prompt Prefix\n\n"
        f"{global_prefix}\n\n"
        f"## {phase_title} Prompt\n\n"
        f"{prompt}\n"
        f"{autonomy}"
        f"{validation_contract}"
        "## Roadmap Rollout Notes\n\n"
        f"{execution_notes}\n"
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def spec_variables(spec: RoadmapSpec) -> dict[str, str]:
    return {
        "spec_title": f"Spec {spec.number} - {spec.title}",
        "spec_number": spec.number,
        "spec_slug": spec.slug,
        "feature_dir": f"specs/{spec.number}-{spec.slug}",
        "autopilot_dir": (
            f"specs/_autopilot/remove-mock-data-roadmap/{spec.number}-{spec.slug}"
        ),
        "branch": f"codex/{spec.number}-{spec.slug}",
        "qa_id": f"qa{spec.number}",
        "qa_label": f"QA{spec.number}",
        "qa_database": f"multi_agent_platform_qa{spec.number}",
        "qa_env_file": f"specs/{spec.number}-{spec.slug}/.env.qa{spec.number}",
        "artifact_root": f".data/qa{spec.number}-artifacts",
        "playwright_output_dir": f"output/playwright/qa{spec.number}_ui",
        "manual_qa_user_guide": (
            f"specs/{spec.number}-{spec.slug}/qa{spec.number}_user_guide.md"
        ),
        "curl_test_output_dir": f".data/curl_test_runs/qa{spec.number}-after-spec",
    }


def render_autopilot(spec: RoadmapSpec) -> dict[str, object]:
    return {
        "schema_version": "1.2",
        "roadmap_file": "remove_mock_data_specs.md",
        "spec_number": spec.number,
        "feature": {
            "name": spec.slug,
            "title": spec.title,
            "feature_directory": f"specs/{spec.number}-{spec.slug}",
            "branch": f"codex/{spec.number}-{spec.slug}",
        },
        "phase_prompt_files": {phase: f"{phase}.md" for phase in PHASES},
        "prompt_files": ["specify.md", "plan.md", "tasks.md"],
        "policy_file": "policy.yml",
        "validation_file": "validation.yml",
        "post_spec_validation": {
            "playwright_must_exercise_ui": True,
            "verify_backend_persistence_via_api_or_database": True,
            "required_curl_skill": "multi-agent-curl-test",
            "curl_command": (
                "uv run python "
                ".agents/skills/multi-agent-curl-test/scripts/run_curl_test.py "
                "--output-dir ${curl_test_output_dir}"
            ),
        },
    }


def render_policy(spec: RoadmapSpec) -> dict[str, object]:
    return {
        "extends": "../../shared/policy.base.yml",
        "variables": spec_variables(spec),
        "autonomy": {
            "auto_select_clarifications": True,
            "minimum_confidence": 0.85,
            "record_auto_choices_in_spec": True,
        },
        "validation": {
            "required_playwright_flows": [f"qa{spec.number}-live-data-ui-api-smoke"],
            "required_post_spec_commands": [
                "post-ui-api-or-database-verification",
                "multi-agent-curl-test",
            ],
        },
    }


def render_validation(spec: RoadmapSpec) -> dict[str, object]:
    hint = ROUTE_HINTS[spec.number]
    return {
        "extends": "../../shared/validation.base.yml",
        "variables": spec_variables(spec),
        "playwright": {
            "flows": [
                {
                    "id": f"qa{spec.number}-live-data-ui-api-smoke",
                    "steps": [
                        {"goto": (f"/auth/local-login?redirect_to={hint.route}")},
                        {"wait_for_load_state": "networkidle"},
                        {
                            "click": (
                                f'form:has(input[value="{hint.principal}"]) button'
                            )
                        },
                        {"wait_for_load_state": "networkidle"},
                        {"expect_text": hint.expected_text},
                        {
                            "screenshot": (
                                f"qa{spec.number}-live-data-ui-api-smoke.png"
                            ),
                            "full_page": True,
                        },
                    ],
                }
            ]
        },
        "post_spec_validation": {
            "playwright_database_requirement": (
                "Before this spec is marked complete, update this manifest or "
                "the spec status evidence with the UI action exercised by "
                "Playwright and the backend API or QA database check proving "
                "the UI reflected or persisted live backend state."
            ),
            "curl_test": {
                "skill": "multi-agent-curl-test",
                "database": "multi_agent_curl_test",
                "command": (
                    "uv run python "
                    ".agents/skills/multi-agent-curl-test/scripts/"
                    "run_curl_test.py --output-dir ${curl_test_output_dir}"
                ),
            },
        },
    }


def write_spec_bundle(
    *,
    spec: RoadmapSpec,
    output_root: Path,
    global_prefix: str,
    execution_notes: str,
    roadmap_path: Path,
) -> dict[str, object]:
    spec_dir = output_root / f"{spec.number}-{spec.slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)

    for phase in PHASES:
        (spec_dir / f"{phase}.md").write_text(
            render_phase_prompt(
                spec=spec,
                phase=phase,
                global_prefix=global_prefix,
                execution_notes=execution_notes,
                roadmap_path=roadmap_path,
            ),
            encoding="utf-8",
        )

    write_json(spec_dir / "autopilot.yml", render_autopilot(spec))
    write_json(spec_dir / "policy.yml", render_policy(spec))
    write_json(spec_dir / "validation.yml", render_validation(spec))

    return {
        "number": spec.number,
        "title": spec.title,
        "slug": spec.slug,
        "autopilot_dir": str(spec_dir),
        "autopilot_file": str(spec_dir / "autopilot.yml"),
        "validation_file": str(spec_dir / "validation.yml"),
        "feature_dir": f"specs/{spec.number}-{spec.slug}",
        "branch": f"codex/{spec.number}-{spec.slug}",
        "status": "pending",
        "phases": {phase: "pending" for phase in PHASES},
        "validation": "pending",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract remove-mock-data live-data cleanup roadmap prompts into "
            "autonomous Spec Kit bundles."
        )
    )
    parser.add_argument(
        "--roadmap", type=Path, default=Path("remove_mock_data_specs.md")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("specs/_autopilot/remove-mock-data-roadmap"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roadmap_path = args.roadmap.resolve()
    output_root = args.output

    if not roadmap_path.exists():
        raise SystemExit(f"roadmap not found: {roadmap_path}")

    text = roadmap_path.read_text(encoding="utf-8")
    global_prefix = extract_global_prefix(text)
    execution_notes = extract_execution_notes(text)
    specs = parse_specs(text)

    output_root.mkdir(parents=True, exist_ok=True)
    queue_specs = [
        write_spec_bundle(
            spec=spec,
            output_root=output_root,
            global_prefix=global_prefix,
            execution_notes=execution_notes,
            roadmap_path=Path(args.roadmap),
        )
        for spec in specs
    ]

    queue = {
        "schema_version": "1.0",
        "roadmap_file": str(args.roadmap),
        "spec_range": "048..059",
        "next_spec": "048",
        "specs": queue_specs,
    }
    write_json(output_root / "queue.json", queue)

    status_path = output_root / "status.json"
    if not status_path.exists():
        write_json(
            status_path,
            {
                "schema_version": "1.0",
                "state": "prepared",
                "current_spec": "048",
                "completed_specs": [],
                "blocked": None,
                "history": [],
            },
        )

    print(
        f"Extracted {len(specs)} specs into {output_root}. "
        f"Queue: {output_root / 'queue.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
