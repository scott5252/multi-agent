#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

PHASES = ("specify", "clarify", "plan", "tasks", "analyze", "implement")
REQUIRED_PROMPTS = ("specify", "plan", "tasks", "implement")
DOCKER_POSTGRES_PREFIX = (
    "if ! docker info >/dev/null 2>&1; then "
    "command -v open >/dev/null 2>&1 && open -a Docker || true; "
    "for i in $(seq 1 60); do "
    "docker info >/dev/null 2>&1 && break; sleep 5; "
    "done; "
    "fi; docker info >/dev/null && docker compose up -d postgres"
)


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


def output_dir_for_roadmap(roadmap: Path) -> Path:
    stem = roadmap.stem
    if stem.endswith("_specs"):
        stem = stem[: -len("_specs")]
    name = slugify(stem)
    if not name.endswith("roadmap"):
        name = f"{name}-roadmap"
    return Path("specs/_autopilot") / name


def extract_fenced_prompt(section: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^###\s+{re.escape(heading)}\s+Prompt\s*```(?:text|md|markdown)?\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(section)
    if match:
        return match.group(1).strip()

    pattern = re.compile(
        rf"^###\s+{re.escape(heading)}\s+Prompt\s*\n+\s*```(?:text|md|markdown)?\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(section)
    return match.group(1).strip() if match else None


def extract_global_prefix(text: str) -> str:
    pattern = re.compile(
        r"^##\s+Global Prompt Prefix\s*.*?```(?:text|md|markdown)?\s*(.*?)\s*```",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def remove_global_prefix(text: str) -> str:
    return re.sub(
        r"\n?##\s+Global Prompt Prefix\s+.*?```(?:text|md|markdown)?\s*.*?\s*```\s*",
        "\n",
        text,
        flags=re.MULTILINE | re.DOTALL | re.IGNORECASE,
    ).strip()


def extract_roadmap_context(text: str) -> str:
    match = re.search(r"^##\s+Spec\s+\d{3}\b", text, re.MULTILINE)
    if not match:
        raise SystemExit("missing numbered spec sections like '## Spec 074 - Title'")
    return remove_global_prefix(text[: match.start()]).strip()


def extract_completion_notes(text: str) -> str:
    for marker in (
        "\n## Completion Review Checklist",
        "\n## Execution Notes",
        "\n## Final Stability Gate",
    ):
        if marker in text:
            heading = marker.strip()
            return f"{heading}\n\n{text.split(marker, 1)[1].strip()}"
    return "Verify every roadmap completion criterion described by the source document."


def synthesize_clarify(spec: RoadmapSpec, roadmap_path: Path) -> str:
    return (
        "/speckit.clarify Run autonomous clarification for "
        f"Spec {spec.number} - {spec.title}. Prefer explicit defaults in "
        f"{roadmap_path}, current spec artifacts, AGENTS.md, the active plan, "
        "and established FastAPI/Pydantic/SQLAlchemy/React/Admin/Playwright "
        "patterns. Auto-answer low-risk questions covered by those sources and "
        "record every auto-selected answer in spec.md under ## Clarifications "
        "with `(autopilot)`. Stop only for ambiguity that changes tenant "
        "isolation, role boundaries, secret or credential handling, destructive "
        "data behavior, production provider calls, real external side effects, "
        "irreversible migration behavior, approval or resume semantics, raw "
        "prompt/completion/test transcript exposure, credential readiness "
        "behavior, or publish-gate trust semantics."
    )


def synthesize_analyze(spec: RoadmapSpec, roadmap_path: Path) -> str:
    return (
        "/speckit.analyze Perform non-destructive cross-artifact analysis for "
        f"Spec {spec.number} - {spec.title}. Review spec.md, plan.md, tasks.md, "
        "contracts, data model, quickstart, QA docs, validation.yml, generated "
        "TypeScript expectations, Playwright journeys, frontend and backend "
        f"quality gates, and roadmap criteria from {roadmap_path}. Treat "
        "CRITICAL findings as blockers. Auto-remediate CRITICAL/HIGH findings "
        "only when the fix is local to Spec Kit artifacts and directly implied "
        "by the roadmap or repository patterns, then rerun analysis up to two "
        "loops."
    )


def build_prompts(
    section: str, spec: RoadmapSpec, roadmap_path: Path
) -> dict[str, str]:
    prompts: dict[str, str] = {}
    for phase in PHASES:
        prompt = extract_fenced_prompt(section, phase.title())
        if prompt is None and phase in REQUIRED_PROMPTS:
            raise SystemExit(
                f"missing prompt block: Spec {spec.number} {phase.title()} Prompt"
            )
        if prompt is not None:
            prompts[phase] = prompt

    prompts.setdefault("clarify", synthesize_clarify(spec, roadmap_path))
    prompts.setdefault("analyze", synthesize_analyze(spec, roadmap_path))
    return {phase: prompts[phase] for phase in PHASES}


def parse_specs(text: str, roadmap_path: Path) -> list[RoadmapSpec]:
    heading_pattern = re.compile(
        r"^##\s+Spec\s+(?P<number>\d{3})\s+-\s+(?P<title>.+)$",
        re.MULTILINE,
    )
    matches = list(heading_pattern.finditer(text))
    if not matches:
        raise SystemExit("no spec headings found")

    specs: list[RoadmapSpec] = []
    for index, match in enumerate(matches):
        number = match.group("number")
        title = match.group("title").strip()
        spec = RoadmapSpec(number=number, title=title, slug=slugify(title), prompts={})
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        specs.append(
            RoadmapSpec(
                number=spec.number,
                title=spec.title,
                slug=spec.slug,
                prompts=build_prompts(section, spec, roadmap_path),
            )
        )

    return sorted(specs, key=lambda item: item.number)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def read_json_object(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"existing JSON is invalid: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"existing JSON is not an object: {path}")
    return value


def spec_variables(
    *,
    spec: RoadmapSpec,
    output_root: Path,
    roadmap_file: Path,
) -> dict[str, str]:
    return {
        "spec_title": f"Spec {spec.number} - {spec.title}",
        "spec_number": spec.number,
        "spec_slug": spec.slug,
        "feature_dir": f"specs/{spec.number}-{spec.slug}",
        "autopilot_dir": f"{output_root}/{spec.number}-{spec.slug}",
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
        "roadmap_file": str(roadmap_file),
    }


def render_phase_prompt(
    *,
    spec: RoadmapSpec,
    phase: str,
    global_prefix: str,
    roadmap_context: str,
    completion_notes: str,
    roadmap_file: Path,
) -> str:
    feature_dir = f"specs/{spec.number}-{spec.slug}"
    branch = f"codex/{spec.number}-{spec.slug}"
    phase_title = phase.title()
    specify_hint = ""
    if phase == "specify":
        specify_hint = (
            f"\nSPECIFY_FEATURE_DIRECTORY={feature_dir}\nGIT_BRANCH_NAME={branch}\n"
        )

    validation_contract = (
        "After implementation, the active spec must pass QA document "
        "validation, `run_spec_qa.py`, Playwright UI validation when browser "
        "behavior exists, focused backend/frontend quality gates, and curl "
        "coverage review for new or changed APIs before the next spec starts. "
        "Update the spec status files and queue status before continuing. Do "
        "not stage, commit, push, or create pull requests unless the user "
        "explicitly asks."
    )

    sections = [
        f"# Spec {spec.number} - {spec.title}: {phase_title}",
        f"Roadmap source: `{roadmap_file}`",
        "## Deterministic Targets\n\n"
        f"- Feature directory: `{feature_dir}`\n"
        f"- Git branch: `{branch}`\n"
        f"- QA id: `qa{spec.number}`\n"
        f"- QA database: `multi_agent_platform_qa{spec.number}`\n"
        f"{specify_hint}",
        "## Autonomy Rules\n\n"
        "- Continue directly to the next spec after validation passes.\n"
        "- Keep local QA deterministic with local-principal auth and mocked "
        "provider/model/tool paths unless a spec explicitly allows otherwise.\n"
        "- Preserve tenant isolation, redaction, auditability, backend-owned "
        "validation and publish readiness, generated TypeScript contract "
        "integrity, truthful live-data UI states, and browser-first QA.\n"
        "- Do not expose raw secrets, credentials, provider payloads, prompts "
        "outside authorized edit forms, completions, memory contents, private "
        "messages, raw tool payloads, raw test transcripts, stack traces, local "
        "filesystem paths, or unauthorized tenant labels.",
        f"## {phase_title} Prompt\n\n{spec.prompts[phase]}",
        f"## Required Post-Spec Validation Contract\n\n{validation_contract}",
    ]
    if global_prefix:
        sections.append(f"## Global Prompt Prefix\n\n{global_prefix}")
    if roadmap_context:
        sections.append(f"## Roadmap Context\n\n{roadmap_context}")
    sections.append(f"## Roadmap Completion Notes\n\n{completion_notes}")
    return "\n\n".join(sections).rstrip() + "\n"


def render_autopilot(
    spec: RoadmapSpec, output_root: Path, roadmap_file: Path
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "roadmap_file": str(roadmap_file),
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
            "curl_testing_file": "curl_testing.md",
            "curl_command": (
                f"{DOCKER_POSTGRES_PREFIX} && uv run python "
                ".agents/skills/multi-agent-curl-test/scripts/run_curl_test.py "
                "--output-dir ${curl_test_output_dir}"
            ),
        },
        "git": {"commit": False, "stage": False, "push": False},
    }


def render_policy(
    spec: RoadmapSpec, output_root: Path, roadmap_file: Path
) -> dict[str, object]:
    return {
        "extends": "../../shared/policy.base.yml",
        "variables": spec_variables(
            spec=spec, output_root=output_root, roadmap_file=roadmap_file
        ),
        "autonomy": {
            "auto_select_clarifications": True,
            "minimum_confidence": 0.85,
            "record_auto_choices_in_spec": True,
            "continue_after_each_completed_spec": True,
            "do_not_commit": True,
        },
        "validation": {
            "required_playwright_flows": [f"qa{spec.number}-autopilot-smoke"],
            "required_quality_commands": [
                "generated-react-types-fresh",
                "frontend-install-deps",
                "frontend-typecheck",
                "frontend-vitest",
                "frontend-build",
            ],
            "required_post_spec_commands": ["curl-testing-coverage-review"],
        },
    }


def render_validation(
    *,
    spec: RoadmapSpec,
    output_root: Path,
    roadmap_file: Path,
    default_route: str,
    default_expected_text: str,
    principal: str,
) -> dict[str, object]:
    return {
        "extends": "../../shared/validation.base.yml",
        "variables": spec_variables(
            spec=spec, output_root=output_root, roadmap_file=roadmap_file
        ),
        "playwright": {
            "flows": [
                {
                    "id": f"qa{spec.number}-autopilot-smoke",
                    "steps": [
                        {"goto": f"/auth/local-login?redirect_to={default_route}"},
                        {"wait_for_load_state": "networkidle"},
                        {"click": f'form:has(input[value="{principal}"]) button'},
                        {"wait_for_load_state": "networkidle"},
                        {"expect_text": default_expected_text},
                        {
                            "screenshot": f"qa{spec.number}-autopilot-smoke.png",
                            "full_page": True,
                        },
                    ],
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
                    "Record curl_testing.md sections covering new or changed "
                    "APIs in this spec's status.json. If no API changed, "
                    "record that decision."
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


def render_initial_status(spec: RoadmapSpec) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "spec_number": spec.number,
        "title": spec.title,
        "state": "pending",
        "current_phase": None,
        "completed_phases": [],
        "validation": "pending",
        "blocker": None,
        "history": [],
    }


def write_spec_bundle(
    *,
    spec: RoadmapSpec,
    output_root: Path,
    global_prefix: str,
    roadmap_context: str,
    completion_notes: str,
    roadmap_file: Path,
    default_route: str,
    default_expected_text: str,
    principal: str,
) -> dict[str, object]:
    spec_dir = output_root / f"{spec.number}-{spec.slug}"
    spec_dir.mkdir(parents=True, exist_ok=True)

    for phase in PHASES:
        (spec_dir / f"{phase}.md").write_text(
            render_phase_prompt(
                spec=spec,
                phase=phase,
                global_prefix=global_prefix,
                roadmap_context=roadmap_context,
                completion_notes=completion_notes,
                roadmap_file=roadmap_file,
            ),
            encoding="utf-8",
        )

    write_json(
        spec_dir / "autopilot.yml", render_autopilot(spec, output_root, roadmap_file)
    )
    write_json(spec_dir / "policy.yml", render_policy(spec, output_root, roadmap_file))
    write_json(
        spec_dir / "validation.yml",
        render_validation(
            spec=spec,
            output_root=output_root,
            roadmap_file=roadmap_file,
            default_route=default_route,
            default_expected_text=default_expected_text,
            principal=principal,
        ),
    )
    status_path = spec_dir / "status.json"
    if not status_path.exists():
        write_json(status_path, render_initial_status(spec))

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


def merge_existing_queue_state(
    generated_specs: list[dict[str, object]],
    existing_queue: dict[str, object] | None,
) -> list[dict[str, object]]:
    if existing_queue is None or not isinstance(existing_queue.get("specs"), list):
        return generated_specs

    existing_by_number: dict[str, dict[str, object]] = {}
    for item in existing_queue["specs"]:
        if isinstance(item, dict) and isinstance(item.get("number"), str):
            existing_by_number[item["number"]] = item

    merged: list[dict[str, object]] = []
    for generated in generated_specs:
        number = generated.get("number")
        existing = existing_by_number.get(number) if isinstance(number, str) else None
        if existing is None:
            merged.append(generated)
            continue

        item = dict(generated)
        for key in ("status", "validation"):
            value = existing.get(key)
            if isinstance(value, str):
                item[key] = value

        existing_phases = existing.get("phases")
        generated_phases = generated.get("phases")
        if isinstance(existing_phases, dict) and isinstance(generated_phases, dict):
            phases = dict(generated_phases)
            for phase in PHASES:
                value = existing_phases.get(phase)
                if isinstance(value, str):
                    phases[phase] = value
            item["phases"] = phases

        merged.append(item)
    return merged


def resolve_next_spec(
    generated_specs: list[dict[str, object]],
    existing_queue: dict[str, object] | None,
) -> str | None:
    specs_by_number = {
        spec["number"]: spec
        for spec in generated_specs
        if isinstance(spec.get("number"), str)
    }
    if existing_queue is not None:
        existing_next = existing_queue.get("next_spec")
        existing_next_spec = (
            specs_by_number.get(existing_next)
            if isinstance(existing_next, str)
            else None
        )
        if existing_next_spec is not None and (
            existing_next_spec.get("status") != "completed"
            or existing_next_spec.get("validation") != "completed"
        ):
            return existing_next

    for spec in generated_specs:
        number = spec.get("number")
        if not isinstance(number, str):
            continue
        if spec.get("status") != "completed" or spec.get("validation") != "completed":
            return number
    return None


def final_gate_commands(
    output_root: Path, specs: list[RoadmapSpec]
) -> list[dict[str, str]]:
    feature_dirs = " ".join(f"specs/{spec.number}-{spec.slug}" for spec in specs)
    curl_output = f".data/curl_test_runs/{output_root.name}-final"
    return [
        {
            "id": "queue-complete",
            "command": (
                "jq -e '.next_spec == null and all(.specs[]; "
                '.status == "completed" and .validation == "completed")\' '
                f"{output_root}/queue.json"
            ),
        },
        {
            "id": "qa-docs-all",
            "command": (
                f"set -e; for d in {feature_dirs}; do "
                "bash .specify/extensions/qa-docs/scripts/bash/"
                'validate-qa-documents.sh "$d"; done'
            ),
        },
        {
            "id": "spec-qa-all",
            "command": (
                f"set -e; for f in {output_root}/*/validation.yml; do "
                'uv run python scripts/qa/run_spec_qa.py "$f"; done'
            ),
        },
        {
            "id": "playwright-all",
            "command": (
                f"set -e; for f in {output_root}/*/validation.yml; do "
                'uv run python scripts/qa/run_playwright_ui.py "$f" '
                "--start-processes; done"
            ),
        },
        {"id": "ruff-check", "command": "uv run ruff check ."},
        {"id": "ruff-format-check", "command": "uv run ruff format --check ."},
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
                "uv run python scripts/frontend/generate_admin_react_types.py --check"
            ),
        },
        {"id": "frontend-install-deps", "command": "cd frontend/admin && npm ci"},
        {
            "id": "frontend-typecheck",
            "command": "cd frontend/admin && npm run typecheck",
        },
        {"id": "frontend-vitest", "command": "cd frontend/admin && npm test"},
        {"id": "frontend-build", "command": "cd frontend/admin && npm run build"},
        {
            "id": "multi-agent-curl-test-final",
            "command": (
                f"{DOCKER_POSTGRES_PREFIX} && uv run python "
                ".agents/skills/multi-agent-curl-test/scripts/run_curl_test.py "
                f"--output-dir {curl_output}"
            ),
        },
    ]


def ensure_output_root(path: Path) -> None:
    resolved = path.resolve()
    autopilot_root = Path("specs/_autopilot").resolve()
    if not (resolved == autopilot_root or autopilot_root in resolved.parents):
        raise SystemExit("output directory must be under specs/_autopilot")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a specs/_autopilot roadmap queue from a Markdown roadmap."
    )
    parser.add_argument("roadmap", type=Path, help="Roadmap Markdown file")
    parser.add_argument(
        "--output", type=Path, help="Output directory under specs/_autopilot"
    )
    parser.add_argument("--default-route", default="/admin/app")
    parser.add_argument("--default-expected-text", default="Admin")
    parser.add_argument("--principal", default="tenant-admin-acme")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse without writing files"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roadmap_file = args.roadmap
    if not roadmap_file.exists():
        raise SystemExit(f"roadmap not found: {roadmap_file}")

    output_root = args.output or output_dir_for_roadmap(roadmap_file)
    ensure_output_root(output_root)

    text = roadmap_file.read_text(encoding="utf-8")
    global_prefix = extract_global_prefix(text)
    roadmap_context = extract_roadmap_context(text)
    completion_notes = extract_completion_notes(text)
    specs = parse_specs(text, roadmap_file)

    if args.dry_run:
        print(
            f"Would prepare {len(specs)} specs in {output_root}. "
            f"Spec range: {specs[0].number}..{specs[-1].number}"
        )
        return 0

    output_root.mkdir(parents=True, exist_ok=True)
    existing_queue = read_json_object(output_root / "queue.json")
    queue_specs = [
        write_spec_bundle(
            spec=spec,
            output_root=output_root,
            global_prefix=global_prefix,
            roadmap_context=roadmap_context,
            completion_notes=completion_notes,
            roadmap_file=roadmap_file,
            default_route=args.default_route,
            default_expected_text=args.default_expected_text,
            principal=args.principal,
        )
        for spec in specs
    ]
    queue_specs = merge_existing_queue_state(queue_specs, existing_queue)

    spec_numbers = [spec.number for spec in specs]
    queue = {
        "schema_version": "1.0",
        "roadmap_file": str(roadmap_file),
        "autopilot_root": str(output_root),
        "spec_range": f"{spec_numbers[0]}..{spec_numbers[-1]}",
        "next_spec": resolve_next_spec(queue_specs, existing_queue),
        "specs": queue_specs,
        "run_contract": {
            "continue_after_each_completed_spec": True,
            "do_not_commit": True,
            "update_readme_after_roadmap": True,
            "update_user_guide_after_roadmap": True,
            "update_curl_testing_for_new_or_changed_apis": True,
            "run_playwright_after_every_spec": True,
            "run_frontend_quality_after_every_spec": True,
        },
        "final_stability_gate": {
            "required": True,
            "run_after_next_spec_null": True,
            "commands": final_gate_commands(output_root, specs),
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
                "current_spec": spec_numbers[0],
                "completed_specs": [],
                "blocked": None,
                "history": [],
            },
        )

    print(
        f"Prepared {len(specs)} specs in {output_root}. "
        f"Queue: {output_root / 'queue.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
