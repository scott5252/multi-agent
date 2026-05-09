#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

PHASES = ("specify", "clarify", "plan", "tasks", "analyze", "implement")
ROADMAP_FILE = "graphical_ui.md"
OUTPUT_ROOT = "specs/_autopilot/graphical-ui-roadmap"
SPEC_RANGE = range(65, 69)
DOCKER_POSTGRES_PREFIX = (
    "if ! docker info >/dev/null 2>&1; then "
    "command -v open >/dev/null 2>&1 && open -a Docker || true; "
    "for i in $(seq 1 60); do "
    "docker info >/dev/null 2>&1 && break; sleep 5; "
    "done; "
    "fi; docker info >/dev/null && docker compose up -d postgres"
)


class RouteHint(NamedTuple):
    route: str
    expected_text: str
    principal: str | None = None


ROUTE_HINTS: dict[str, RouteHint] = {
    "065": RouteHint("/openapi.json", "agent", None),
    "066": RouteHint("/admin/app/workflows", "Workflow", "tenant-admin-acme"),
    "067": RouteHint("/admin/app/operations", "Operations", "tenant-admin-acme"),
    "068": RouteHint("/admin/app/operations", "Operations", "tenant-admin-acme"),
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


def extract_fenced_text(section: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^### {re.escape(heading)} Prompt\s*```text\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(section)
    if not match:
        return None
    return match.group(1).strip()


def extract_architecture_context(text: str) -> str:
    match = re.search(r"^## Spec 065\b", text, re.MULTILINE)
    if not match:
        raise SystemExit("missing Spec 065 section")
    return text[: match.start()].strip()


def extract_rollout_notes(text: str) -> str:
    marker = "\n## Cross-Spec Dependency Order"
    if marker not in text:
        return "Implement specs 065 through 068 in ascending order."
    return text.split(marker, 1)[1].strip()


def render_generated_clarify(spec: RoadmapSpec) -> str:
    return (
        "/speckit.clarify Run autonomous clarification for "
        f"Spec {spec.number} - {spec.title}. Prefer the explicit defaults in "
        "graphical_ui.md and established repository patterns. Auto-answer "
        "low-risk questions covered by the roadmap, current spec artifacts, "
        "completed prior specs, or existing FastAPI/Pydantic/SQLAlchemy/React/"
        "React Flow/Admin/test patterns. Record every auto-selected answer in "
        "spec.md under ## Clarifications with `(autopilot)`. Stop only for "
        "ambiguity that changes tenant isolation, role boundaries, secret or "
        "credential handling, destructive data behavior, production provider "
        "calls, real external side effects, irreversible migration behavior, "
        "manual-resolution semantics, approval/exception policy, raw artifact/"
        "prompt/completion exposure, or whether Spec 068 should create durable "
        "interaction evidence despite existing runtime evidence being "
        "sufficient."
    )


def render_generated_analyze(spec: RoadmapSpec) -> str:
    return (
        "/speckit.analyze Perform non-destructive cross-artifact analysis for "
        f"Spec {spec.number} - {spec.title}. Review spec.md, plan.md, "
        "tasks.md, contracts, data model, quickstart, QA docs, curl_testing.md "
        "coverage requirements, and validation.yml for consistency with "
        "graphical_ui.md, AGENTS.md, tenant isolation, redaction, safe graph "
        "projection contracts, keyboard-readable graph equivalents, generated "
        "TypeScript contracts, deterministic QA/model mocks, Playwright "
        "coverage, and multi-agent-curl-test regression. Treat CRITICAL "
        "findings as blockers. Auto-remediate CRITICAL/HIGH findings only "
        "when the fix is local to Spec Kit artifacts and directly implied by "
        "the roadmap or repository patterns, then rerun analysis up to two "
        "loops."
    )


def build_prompts(section: str, spec: RoadmapSpec) -> dict[str, str]:
    prompts: dict[str, str] = {}
    required_headings = {
        "specify": "Specify",
        "plan": "Plan",
        "tasks": "Tasks",
        "implement": "Implement",
    }
    for phase, heading in required_headings.items():
        prompt = extract_fenced_text(section, heading)
        if prompt is None:
            raise SystemExit(
                f"missing prompt block: Spec {spec.number} {heading} Prompt"
            )
        prompts[phase] = prompt

    prompts["clarify"] = render_generated_clarify(spec)
    prompts["analyze"] = render_generated_analyze(spec)
    return {phase: prompts[phase] for phase in PHASES}


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
        spec = RoadmapSpec(
            number=number,
            title=title,
            slug=slugify(title),
            prompts={},
        )
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        specs.append(
            RoadmapSpec(
                number=spec.number,
                title=spec.title,
                slug=spec.slug,
                prompts=build_prompts(section, spec),
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
    architecture_context: str,
    rollout_notes: str,
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

    validation_contract = (
        "\n## Required Post-Spec Validation Contract\n\n"
        "After implementation, the active spec must pass QA document "
        "validation, `run_spec_qa.py`, Playwright UI validation, curl_testing.md "
        "coverage review/update, and the `multi-agent-curl-test` runner before "
        "the next spec starts. If the spec adds or changes an API, update "
        "`curl_testing.md` in the same spec and fix the implementation or curl "
        "commands until the multi-agent curl regression passes. Do not pause "
        "between completed specs and do not create git commits. After Spec 068 "
        "passes, run the final whole-roadmap stability gate from the "
        "`speckit-graphical-ui` skill before reporting completion.\n"
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
        f"- Curl regression source: `curl_testing.md`\n"
        f"{specify_hint}\n"
        "## Graphical UI Autonomy Rules\n\n"
        "- Continue directly to the next spec after validation passes.\n"
        "- Do not commit, stage, push, or create pull requests.\n"
        "- Keep all local QA deterministic with local-principal auth and mocked "
        "provider/model paths unless a spec explicitly allows otherwise.\n"
        "- Preserve tenant isolation, redaction, auditability, safe summaries, "
        "artifact references, generated TypeScript contract integrity, "
        "keyboard-readable graph equivalents, and truthful live-data UI states.\n"
        "- Use existing workflow builder, React Flow, operations workbench, "
        "run-debug, runtime timeline, handoff, gateway, tool-summary, and "
        "artifact-reference patterns before adding new abstractions.\n\n"
        f"## {phase_title} Prompt\n\n"
        f"{prompt}\n"
        f"{validation_contract}"
        "## Graphical Agent Workflow Context\n\n"
        f"{architecture_context}\n\n"
        "## Cross-Spec Rollout Notes\n\n"
        f"{rollout_notes}\n"
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def read_existing_queue(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"existing queue is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"existing queue is not a JSON object: {path}")
    return value


def merge_existing_queue_state(
    generated_specs: list[dict[str, object]],
    existing_queue: dict[str, object] | None,
) -> list[dict[str, object]]:
    if existing_queue is None:
        return generated_specs

    existing_specs = existing_queue.get("specs")
    if not isinstance(existing_specs, list):
        return generated_specs

    existing_by_number: dict[str, dict[str, object]] = {}
    for existing_spec in existing_specs:
        if not isinstance(existing_spec, dict):
            continue
        number = existing_spec.get("number")
        if isinstance(number, str):
            existing_by_number[number] = existing_spec

    merged_specs: list[dict[str, object]] = []
    for generated_spec in generated_specs:
        number = generated_spec.get("number")
        existing_spec = (
            existing_by_number.get(number) if isinstance(number, str) else None
        )
        if existing_spec is None:
            merged_specs.append(generated_spec)
            continue

        merged_spec = dict(generated_spec)
        for key in ("status", "validation"):
            value = existing_spec.get(key)
            if isinstance(value, str):
                merged_spec[key] = value

        existing_phases = existing_spec.get("phases")
        generated_phases = generated_spec.get("phases")
        if isinstance(existing_phases, dict) and isinstance(generated_phases, dict):
            merged_phases = dict(generated_phases)
            for phase in PHASES:
                value = existing_phases.get(phase)
                if isinstance(value, str):
                    merged_phases[phase] = value
            merged_spec["phases"] = merged_phases

        merged_specs.append(merged_spec)

    return merged_specs


def resolve_next_spec(
    *,
    generated_specs: list[dict[str, object]],
    existing_queue: dict[str, object] | None,
) -> str | None:
    numbers = {
        spec.get("number")
        for spec in generated_specs
        if isinstance(spec.get("number"), str)
    }
    if existing_queue is not None:
        existing_next = existing_queue.get("next_spec")
        if existing_next is None or existing_next in numbers:
            return existing_next

    for spec in generated_specs:
        number = spec.get("number")
        if not isinstance(number, str):
            continue
        if spec.get("validation") != "completed" or spec.get("status") != "completed":
            return number
    return None


def spec_variables(spec: RoadmapSpec) -> dict[str, str]:
    return {
        "spec_title": f"Spec {spec.number} - {spec.title}",
        "spec_number": spec.number,
        "spec_slug": spec.slug,
        "feature_dir": f"specs/{spec.number}-{spec.slug}",
        "autopilot_dir": f"{OUTPUT_ROOT}/{spec.number}-{spec.slug}",
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
        "roadmap_file": ROADMAP_FILE,
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
            "update_curl_testing_for_new_or_changed_apis": True,
            "required_curl_skill": "multi-agent-curl-test",
            "curl_testing_file": "curl_testing.md",
            "curl_command": (
                f"{DOCKER_POSTGRES_PREFIX} && uv run python "
                ".agents/skills/multi-agent-curl-test/scripts/run_curl_test.py "
                "--output-dir ${curl_test_output_dir}"
            ),
        },
        "git": {
            "commit": False,
            "stage": False,
            "push": False,
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
            "continue_after_each_completed_spec": True,
            "do_not_commit": True,
        },
        "validation": {
            "required_playwright_flows": [f"qa{spec.number}-graphical-ui-smoke"],
            "required_quality_commands": [
                "generated-react-types-fresh",
                "frontend-install-deps",
                "frontend-typecheck",
                "frontend-vitest",
                "frontend-build",
            ],
            "required_post_spec_commands": [
                "curl-testing-coverage-review",
                "multi-agent-curl-test",
            ],
        },
    }


def render_validation(spec: RoadmapSpec) -> dict[str, object]:
    hint = ROUTE_HINTS[spec.number]
    route = hint.route
    if hint.principal is not None:
        route = f"/auth/local-login?redirect_to={route}"
        steps: list[dict[str, object]] = [
            {"goto": route},
            {"wait_for_load_state": "networkidle"},
            {"click": f'form:has(input[value="{hint.principal}"]) button'},
            {"wait_for_load_state": "networkidle"},
            {"expect_text": hint.expected_text},
            {
                "screenshot": f"qa{spec.number}-graphical-ui-smoke.png",
                "full_page": True,
            },
        ]
    else:
        steps = [
            {"goto": route},
            {"wait_for_load_state": "networkidle"},
            {"expect_text": hint.expected_text},
            {
                "screenshot": f"qa{spec.number}-graphical-ui-smoke.png",
                "full_page": False,
            },
        ]

    return {
        "extends": "../../shared/validation.base.yml",
        "variables": spec_variables(spec),
        "playwright": {
            "flows": [
                {
                    "id": f"qa{spec.number}-graphical-ui-smoke",
                    "steps": steps,
                }
            ]
        },
        "extra_quality_commands": [
            {
                "id": "generated-react-types-fresh",
                "command": (
                    "uv run python scripts/frontend/generate_admin_react_types.py "
                    "--check"
                ),
                "expect_exit_code": 0,
                "timeout_seconds": 120,
            },
            {
                "id": "frontend-install-deps",
                "command": "cd frontend/admin && npm ci",
                "expect_exit_code": 0,
                "timeout_seconds": 300,
            },
            {
                "id": "frontend-typecheck",
                "command": "cd frontend/admin && npm run typecheck",
                "expect_exit_code": 0,
                "timeout_seconds": 300,
            },
            {
                "id": "frontend-vitest",
                "command": "cd frontend/admin && npm test",
                "expect_exit_code": 0,
                "timeout_seconds": 300,
            },
            {
                "id": "frontend-build",
                "command": "cd frontend/admin && npm run build",
                "expect_exit_code": 0,
                "timeout_seconds": 300,
            },
        ],
        "post_spec_validation": {
            "curl_testing": {
                "file": "curl_testing.md",
                "require_update_when_public_api_changes": True,
                "require_commands_for_new_route_families": True,
                "evidence_note": (
                    "Record the curl_testing.md sections covering new or "
                    "changed graphical agent workflow APIs in this spec's "
                    "status.json."
                ),
            },
            "curl_test": {
                "skill": "multi-agent-curl-test",
                "database": "multi_agent_curl_test",
                "command": (
                    f"{DOCKER_POSTGRES_PREFIX} && uv run python "
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
    architecture_context: str,
    rollout_notes: str,
    roadmap_path: Path,
) -> dict[str, object]:
    spec_dir = output_root / f"{spec.number}-{spec.slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)

    for phase in PHASES:
        (spec_dir / f"{phase}.md").write_text(
            render_phase_prompt(
                spec=spec,
                phase=phase,
                architecture_context=architecture_context,
                rollout_notes=rollout_notes,
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
            "Extract Graphical Agent Workflow UI roadmap prompts into "
            "autonomous Spec Kit bundles."
        )
    )
    parser.add_argument("--roadmap", type=Path, default=Path(ROADMAP_FILE))
    parser.add_argument("--output", type=Path, default=Path(OUTPUT_ROOT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roadmap_path = args.roadmap.resolve()
    output_root = args.output

    if not roadmap_path.exists():
        raise SystemExit(f"roadmap not found: {roadmap_path}")

    text = roadmap_path.read_text(encoding="utf-8")
    architecture_context = extract_architecture_context(text)
    rollout_notes = extract_rollout_notes(text)
    specs = parse_specs(text)

    output_root.mkdir(parents=True, exist_ok=True)
    existing_queue = read_existing_queue(output_root / "queue.json")
    queue_specs = [
        write_spec_bundle(
            spec=spec,
            output_root=output_root,
            architecture_context=architecture_context,
            rollout_notes=rollout_notes,
            roadmap_path=Path(args.roadmap),
        )
        for spec in specs
    ]
    queue_specs = merge_existing_queue_state(queue_specs, existing_queue)

    queue = {
        "schema_version": "1.0",
        "roadmap_file": str(args.roadmap),
        "spec_range": "065..068",
        "next_spec": resolve_next_spec(
            generated_specs=queue_specs,
            existing_queue=existing_queue,
        ),
        "specs": queue_specs,
        "run_contract": {
            "continue_after_each_completed_spec": True,
            "do_not_commit": True,
            "update_curl_testing_for_new_or_changed_apis": True,
            "run_multi_agent_curl_test_after_every_spec": True,
            "run_playwright_after_every_spec": True,
        },
        "final_stability_gate": {
            "required": True,
            "run_after_next_spec_null": True,
            "commands": [
                {
                    "id": "queue-complete",
                    "command": (
                        "jq -e '.next_spec == null and all(.specs[]; "
                        '.status == "completed" and .validation == '
                        '"completed")\' '
                        "specs/_autopilot/graphical-ui-roadmap/queue.json"
                    ),
                },
                {
                    "id": "qa-docs-all",
                    "command": (
                        "set -e; for d in "
                        "specs/065-agent-communication-graph-contracts-and-projections "
                        "specs/066-react-agent-graph-viewer-for-workflow-"
                        "drafts-and-versions "
                        "specs/067-runtime-agent-communication-graph-for-runs "
                        "specs/068-durable-agent-interaction-evidence-and-"
                        "replay-graph; "
                        "do bash .specify/extensions/qa-docs/scripts/bash/"
                        'validate-qa-documents.sh "$d"; done'
                    ),
                },
                {
                    "id": "spec-qa-all",
                    "command": (
                        "set -e; for f in specs/_autopilot/"
                        "graphical-ui-roadmap/*/validation.yml; do "
                        'uv run python scripts/qa/run_spec_qa.py "$f"; done'
                    ),
                },
                {
                    "id": "playwright-all",
                    "command": (
                        "set -e; for f in specs/_autopilot/"
                        "graphical-ui-roadmap/*/validation.yml; do "
                        'uv run python scripts/qa/run_playwright_ui.py "$f" '
                        "--start-processes; done"
                    ),
                },
                {"id": "ruff-check", "command": "uv run ruff check ."},
                {
                    "id": "ruff-format-check",
                    "command": "uv run ruff format --check .",
                },
                {"id": "mypy", "command": "uv run mypy src"},
                {
                    "id": "pytest-coverage",
                    "command": (
                        "uv run pytest --cov=src/multi_agent_platform "
                        "--cov-report=term-missing --cov-fail-under=90"
                    ),
                },
                {
                    "id": "generated-react-types-fresh",
                    "command": (
                        "uv run python scripts/frontend/"
                        "generate_admin_react_types.py --check"
                    ),
                },
                {
                    "id": "frontend-install-deps",
                    "command": "cd frontend/admin && npm ci",
                },
                {
                    "id": "frontend-typecheck",
                    "command": "cd frontend/admin && npm run typecheck",
                },
                {
                    "id": "frontend-vitest",
                    "command": "cd frontend/admin && npm test",
                },
                {
                    "id": "frontend-build",
                    "command": "cd frontend/admin && npm run build",
                },
                {
                    "id": "multi-agent-curl-test-final",
                    "command": (
                        f"{DOCKER_POSTGRES_PREFIX} && uv run python "
                        ".agents/skills/multi-agent-curl-test/scripts/"
                        "run_curl_test.py --output-dir "
                        ".data/curl_test_runs/graphical-ui-final"
                    ),
                },
            ],
        },
    }
    write_json(output_root / "queue.json", queue)

    status_path = output_root / "status.json"
    if not status_path.exists():
        write_json(
            status_path,
            {
                "schema_version": "1.0",
                "state": "prepared",
                "current_spec": "065",
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
