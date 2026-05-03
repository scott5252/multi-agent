#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", slug)


def load_json(path: Path) -> JsonObject:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("config must contain a JSON object")
    return data


def write_json(path: Path, data: JsonObject, *, force: bool) -> None:
    write_text(path, json.dumps(data, indent=2) + "\n", force=force)


def write_text(path: Path, text: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def prompt_value(prompts: JsonObject, key: str) -> str:
    value = prompts.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"prompts.{key} is required")
    return value.strip() + "\n"


def command_ids(commands: list[JsonObject]) -> list[str]:
    ids: list[str] = []
    for command in commands:
        command_id = command.get("id")
        if not isinstance(command_id, str) or not command_id:
            raise SystemExit("each extra command must have an id")
        ids.append(command_id)
    return ids


def playwright_flow(spec_slug: str, playwright: JsonObject | None) -> list[JsonObject]:
    if not playwright:
        return []

    path = playwright.get("path")
    if not isinstance(path, str) or not path.startswith("/"):
        raise SystemExit("playwright.path must be an absolute app path like /admin/foo")

    expected_text = playwright.get("expected_text")
    steps: list[JsonObject] = [
        {
            "goto": f"/auth/local-login?redirect_to={path}",
        }
    ]
    if isinstance(expected_text, str) and expected_text:
        steps.append({"expect_text": expected_text})
    else:
        steps.append({"expect_text": "Local Login"})
    steps.append({"screenshot": "01-local-login.png", "full_page": True})

    return [
        {
            "id": f"{spec_slug}-ui-login",
            "steps": steps,
        },
        {
            "id": f"{spec_slug}-ui-target",
            "steps": [
                {"goto": path},
                {"screenshot": f"02-{spec_slug}-target.png", "full_page": True},
            ],
        },
    ]


def build_variables(config: JsonObject) -> JsonObject:
    spec_number = str(config.get("spec_number", "")).zfill(3)
    if not re.fullmatch(r"\d{3}", spec_number):
        raise SystemExit("spec_number must be a three-digit value or integer")

    title = config.get("title")
    if not isinstance(title, str) or not title.strip():
        raise SystemExit("title is required")

    slug = config.get("slug")
    if not isinstance(slug, str) or not slug.strip():
        slug = slugify(title)
    slug = slugify(slug)

    directory_name = f"{spec_number}-{slug}"
    qa_id = f"qa{spec_number}"
    qa_label = f"QA{spec_number}"

    return {
        "spec_title": title.strip(),
        "spec_number": spec_number,
        "spec_slug": slug,
        "feature_dir": f"specs/{directory_name}",
        "autopilot_dir": f"specs/_autopilot/{directory_name}",
        "branch": str(config.get("branch") or f"codex/{directory_name}"),
        "qa_id": qa_id,
        "qa_label": qa_label,
        "qa_database": f"multi_agent_platform_{qa_id}",
        "qa_env_file": f"specs/{directory_name}/.env.{qa_id}",
        "artifact_root": f".data/{qa_id}-artifacts",
        "playwright_output_dir": f"output/playwright/{qa_id}_ui",
        "manual_qa_user_guide": f"specs/{directory_name}/{qa_id}_user_guide.md",
    }


def scaffold(config: JsonObject, *, repo_root: Path, force: bool) -> Path:
    variables = build_variables(config)
    autopilot_dir = repo_root / str(variables["autopilot_dir"])
    prompts = config.get("prompts")
    if not isinstance(prompts, dict):
        raise SystemExit("prompts object is required")

    playwright = config.get("playwright")
    if playwright is not None and not isinstance(playwright, dict):
        raise SystemExit("playwright must be an object when provided")

    flows = playwright_flow(str(variables["spec_slug"]), playwright)
    extra_commands = config.get("extra_commands", [])
    if not isinstance(extra_commands, list):
        raise SystemExit("extra_commands must be a list")
    if not all(isinstance(command, dict) for command in extra_commands):
        raise SystemExit("each extra command must be an object")

    autopilot = {
        "schema_version": "1.0",
        "feature": {
            "name": variables["spec_slug"],
            "branch": variables["branch"],
        },
        "prompt_files": ["specify.md", "plan.md", "tasks.md"],
        "policy_file": "policy.yml",
        "validation_file": "validation.yml",
    }

    policy = {
        "extends": "../shared/policy.base.yml",
        "variables": variables,
        "validation": {
            "required_playwright_flows": [flow["id"] for flow in flows],
            "required_extra_commands": command_ids(extra_commands),
        },
    }

    validation: JsonObject = {
        "extends": "../shared/validation.base.yml",
        "variables": variables,
        "playwright": {
            "flows": flows,
        },
    }
    if extra_commands:
        validation["extra_commands"] = extra_commands

    write_json(autopilot_dir / "autopilot.yml", autopilot, force=force)
    write_text(
        autopilot_dir / "specify.md",
        prompt_value(prompts, "specify"),
        force=force,
    )
    write_text(autopilot_dir / "plan.md", prompt_value(prompts, "plan"), force=force)
    write_text(autopilot_dir / "tasks.md", prompt_value(prompts, "tasks"), force=force)
    write_json(autopilot_dir / "policy.yml", policy, force=force)
    write_json(autopilot_dir / "validation.yml", validation, force=force)
    return autopilot_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a Spec Kit autopilot folder."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    output_dir = scaffold(config, repo_root=args.repo_root.resolve(), force=args.force)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
