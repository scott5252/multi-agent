#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

PHASES = ("specify", "clarify", "plan", "tasks", "analyze", "implement")
SPEC_RANGE = range(38, 48)

ROUTE_HINTS: dict[str, tuple[str, str]] = {
    "038": ("/admin/app/migration", "Migration"),
    "039": ("/admin/app", "Admin"),
    "040": ("/admin/app/workflows", "Workflow"),
    "041": ("/admin/app/governance", "Governance"),
    "042": ("/admin/app/skills", "Skill"),
    "043": ("/admin/app/test-bench", "Test Bench"),
    "044": ("/admin/app/operations", "Operations"),
    "045": ("/admin/app/channels", "Telegram"),
    "046": ("/runs", "Run"),
    "047": ("/admin/app/migration", "Jinja"),
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
    marker = "\n## Execution Notes"
    if marker not in text:
        raise SystemExit("missing Execution Notes section")
    return text.split(marker, 1)[1].strip()


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
            "side-effect, irreversible migration, legacy-route retirement, "
            "dependency deletion, or approval/resume ambiguity.\n"
        )
    if phase == "analyze":
        autonomy = (
            "\n## Autonomous Analysis Handling\n\n"
            "After the read-only analysis report, remediate CRITICAL/HIGH "
            "findings only when the fix is explicit from the roadmap or local "
            "artifacts, then rerun analysis up to two loops. Do not implement "
            "with remaining CRITICAL findings.\n"
        )

    return (
        f"# Spec {spec.number} - {spec.title}: {phase_title}\n\n"
        f"Roadmap source: `{roadmap_path}`\n\n"
        "## Deterministic Targets\n\n"
        f"- Feature directory: `{feature_dir}`\n"
        f"- Git branch: `{branch}`\n"
        f"- QA id: `qa{spec.number}`\n"
        f"- QA database: `multi_agent_platform_qa{spec.number}`\n"
        f"{specify_hint}\n"
        "## Global Prompt Prefix\n\n"
        f"{global_prefix}\n\n"
        f"## {phase_title} Prompt\n\n"
        f"{prompt}\n"
        f"{autonomy}\n"
        "## Roadmap Execution Notes\n\n"
        f"{execution_notes}\n"
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def render_autopilot(spec: RoadmapSpec) -> dict[str, object]:
    return {
        "schema_version": "1.1",
        "roadmap_file": "react_ui2.md",
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
            "required_playwright_flows": [f"qa{spec.number}-react-ui2-smoke"],
        },
    }


def spec_variables(spec: RoadmapSpec) -> dict[str, str]:
    return {
        "spec_title": f"Spec {spec.number} - {spec.title}",
        "spec_number": spec.number,
        "spec_slug": spec.slug,
        "feature_dir": f"specs/{spec.number}-{spec.slug}",
        "autopilot_dir": (
            f"specs/_autopilot/react-ui2-roadmap/{spec.number}-{spec.slug}"
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
    }


def render_validation(spec: RoadmapSpec) -> dict[str, object]:
    route, expected_text = ROUTE_HINTS[spec.number]
    return {
        "extends": "../../shared/validation.base.yml",
        "variables": spec_variables(spec),
        "playwright": {
            "flows": [
                {
                    "id": f"qa{spec.number}-react-ui2-smoke",
                    "steps": [
                        {"goto": route},
                        {"wait_for_load_state": "networkidle"},
                        {"expect_text": expected_text},
                        {
                            "screenshot": f"qa{spec.number}-react-ui2-smoke.png",
                            "full_page": True,
                        },
                    ],
                }
            ]
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
            "Extract React UI2 full Jinja removal roadmap prompts into "
            "autonomous Spec Kit bundles."
        )
    )
    parser.add_argument("--roadmap", type=Path, default=Path("react_ui2.md"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("specs/_autopilot/react-ui2-roadmap"),
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
        "spec_range": "038..047",
        "next_spec": "038",
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
                "current_spec": "038",
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
