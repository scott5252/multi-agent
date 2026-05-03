#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from autopilot_config import JsonObject, load_config, repo_root_from
from run_spec_qa import start_processes, stop_processes


def absolutize(base_url: str, target: str) -> str:
    if target.startswith(("http://", "https://", "file://")):
        return target
    return urljoin(f"{base_url.rstrip('/')}/", target.lstrip("/"))


def flow_steps(playwright_config: JsonObject) -> list[JsonObject]:
    flows = playwright_config.get("flows", [])
    if not isinstance(flows, list):
        raise SystemExit("playwright.flows must be a list")

    steps: list[JsonObject] = []
    for flow in flows:
        if not isinstance(flow, dict):
            raise SystemExit("each Playwright flow must be an object")
        flow_id = str(flow.get("id", "unnamed-flow"))
        flow_steps_value = flow.get("steps", [])
        if not isinstance(flow_steps_value, list):
            raise SystemExit(f"{flow_id}: steps must be a list")
        for step in flow_steps_value:
            if not isinstance(step, dict):
                raise SystemExit(f"{flow_id}: each step must be an object")
            step = dict(step)
            step["_flow_id"] = flow_id
            steps.append(step)
    return steps


def print_dry_run(playwright_config: JsonObject) -> None:
    for step in flow_steps(playwright_config):
        flow_id = step.pop("_flow_id")
        print(f"==> {flow_id}: {step}")


def step_selector(step: JsonObject) -> str:
    selector = step.get("selector")
    if not isinstance(selector, str) or not selector:
        raise SystemExit(f"{step.get('_flow_id')}: step requires selector")
    return selector


def run_step(page: Any, step: JsonObject, *, base_url: str, output_dir: Path) -> None:
    flow_id = str(step.get("_flow_id", "unnamed-flow"))

    if "goto" in step:
        page.goto(absolutize(base_url, str(step["goto"])))

    if "wait_for_load_state" in step:
        page.wait_for_load_state(str(step["wait_for_load_state"]))

    if "wait_for_selector" in step:
        page.wait_for_selector(str(step["wait_for_selector"]))

    if "click" in step:
        page.locator(str(step["click"])).click()

    if "fill" in step:
        fill_value = step["fill"]
        if isinstance(fill_value, dict):
            selector = str(fill_value["selector"])
            value = str(fill_value["value"])
        else:
            selector = step_selector(step)
            value = str(fill_value)
        page.locator(selector).fill(value)

    if "press" in step:
        press_value = step["press"]
        if isinstance(press_value, dict):
            selector = str(press_value["selector"])
            key = str(press_value["key"])
        else:
            selector = step_selector(step)
            key = str(press_value)
        page.locator(selector).press(key)

    if "check" in step:
        page.locator(str(step["check"])).check()

    if "select" in step:
        select_value = step["select"]
        if not isinstance(select_value, dict):
            raise SystemExit(f"{flow_id}: select must be an object")
        page.locator(str(select_value["selector"])).select_option(
            str(select_value["value"])
        )

    if "expect_text" in step:
        expected = step["expect_text"]
        if isinstance(expected, dict):
            selector = expected.get("selector")
            text = str(expected["text"])
            target = page.locator(str(selector)) if selector else page.locator("body")
            target.get_by_text(text).first.wait_for()
        else:
            page.get_by_text(str(expected)).first.wait_for()

    if "expect_url" in step:
        page.wait_for_url(str(step["expect_url"]))

    if "screenshot" in step:
        screenshot_path = output_dir / str(step["screenshot"])
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(screenshot_path), full_page=bool(step.get("full_page"))
        )
        print(f"==> screenshot: {screenshot_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Playwright UI checks from Spec Kit validation config."
    )
    parser.add_argument("validation_file", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--start-processes",
        action="store_true",
        help="Start top-level validation processes before running browser flows.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation_file = args.validation_file.resolve()
    if not validation_file.exists():
        raise SystemExit(f"validation file not found: {validation_file}")

    repo_root = (
        args.repo_root.resolve() if args.repo_root else repo_root_from(validation_file)
    )
    config = load_config(validation_file)
    playwright_config = config.get("playwright")
    if not isinstance(playwright_config, dict):
        raise SystemExit("validation file does not define a playwright object")

    if args.dry_run:
        if args.start_processes:
            start_processes(
                config,
                cwd=repo_root,
                base_env=os.environ.copy(),
                dry_run=True,
            )
        print_dry_run(playwright_config)
        print("Playwright dry run completed")
        return 0

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Install it with "
            "`uv add --dev playwright` and run `uv run playwright install chromium`."
        ) from exc

    base_url = str(playwright_config.get("base_url", "http://127.0.0.1:8000"))
    output_dir = repo_root / str(
        playwright_config.get("output_dir", "output/playwright")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    processes = []
    try:
        if args.start_processes:
            processes = start_processes(
                config,
                cwd=repo_root,
                base_env=os.environ.copy(),
                dry_run=False,
            )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed)
            page = browser.new_page()
            try:
                for step in flow_steps(playwright_config):
                    run_step(page, step, base_url=base_url, output_dir=output_dir)
            finally:
                browser.close()
    finally:
        stop_processes(processes)

    print("Playwright UI validation completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
