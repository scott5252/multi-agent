#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def first_heading(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return None


def section_excerpt(path: Path, heading: str, *, max_lines: int = 18) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = None
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    for index, line in enumerate(lines):
        if pattern.match(line.strip()):
            start = index + 1
            break
    if start is None:
        return []
    excerpt: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.strip():
            excerpt.append(line.rstrip())
        if len(excerpt) >= max_lines:
            break
    return excerpt


def task_counts(path: Path) -> tuple[int, int]:
    if not path.exists():
        return (0, 0)
    complete = 0
    total = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("- ["):
            total += 1
            if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                complete += 1
    return complete, total


def collect_spec_summary(item: dict[str, object]) -> dict[str, object]:
    feature_dir_value = item.get("feature_dir")
    if not isinstance(feature_dir_value, str):
        raise SystemExit(f"queue item missing feature_dir: {item!r}")
    feature_dir = Path(feature_dir_value)
    spec_md = feature_dir / "spec.md"
    plan_md = feature_dir / "plan.md"
    tasks_md = feature_dir / "tasks.md"
    number = str(item.get("number", "unknown"))

    qa_user_guide = feature_dir / f"qa{number}_user_guide.md"
    qa_ui = feature_dir / f"qa{number}_ui.md"
    complete, total = task_counts(tasks_md)

    return {
        "number": number,
        "title": item.get("title", ""),
        "status": item.get("status", ""),
        "validation": item.get("validation", ""),
        "feature_dir": str(feature_dir),
        "spec_heading": first_heading(spec_md),
        "plan_heading": first_heading(plan_md),
        "tasks_complete": complete,
        "tasks_total": total,
        "overview": section_excerpt(spec_md, "Overview")
        or section_excerpt(spec_md, "Summary")
        or section_excerpt(plan_md, "Summary"),
        "user_story": section_excerpt(spec_md, "User Stories & Testing")
        or section_excerpt(spec_md, "User Stories"),
        "qa_user_guide": str(qa_user_guide) if qa_user_guide.exists() else None,
        "qa_ui": str(qa_ui) if qa_ui.exists() else None,
    }


def render_markdown(
    queue: dict[str, object], summaries: list[dict[str, object]], autopilot_dir: Path
) -> str:
    lines = [
        f"# Autopilot Summary: {queue.get('autopilot_root', str(autopilot_dir))}",
        "",
        f"- Roadmap file: `{queue.get('roadmap_file', 'unknown')}`",
        f"- Spec range: `{queue.get('spec_range', 'unknown')}`",
        f"- Next spec: `{queue.get('next_spec')}`",
        "",
        "## Completed Spec Context",
        "",
    ]

    for summary in summaries:
        lines.extend(
            [
                f"### Spec {summary['number']} - {summary['title']}",
                "",
                f"- Status: `{summary['status']}`",
                f"- Validation: `{summary['validation']}`",
                f"- Feature dir: `{summary['feature_dir']}`",
                f"- Tasks: `{summary['tasks_complete']}/{summary['tasks_total']}`",
            ]
        )
        if summary.get("qa_user_guide"):
            lines.append(f"- User guide: `{summary['qa_user_guide']}`")
        if summary.get("qa_ui"):
            lines.append(f"- UI walkthrough: `{summary['qa_ui']}`")
        overview = summary.get("overview")
        if isinstance(overview, list) and overview:
            lines.extend(["", "Key context:"])
            lines.extend(f"- {line}" for line in overview[:8])
        user_story = summary.get("user_story")
        if isinstance(user_story, list) and user_story:
            lines.extend(["", "User-facing behavior:"])
            lines.extend(f"- {line}" for line in user_story[:8])
        lines.append("")

    lines.extend(
        [
            "## Documentation Update Checklist",
            "",
            "- Update README.md with new user-facing capabilities and where to start.",
            "- Update user_guide.md with visible UI navigation and happy-path steps.",
            "- Keep API/curl details secondary unless the existing guide already "
            "uses them.",
            "- Avoid fake/demo wording, raw secrets, raw prompts outside editors, "
            "raw transcripts, stack traces, and local filesystem paths.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a completed specs/_autopilot roadmap for docs updates."
    )
    parser.add_argument("autopilot_dir", type=Path)
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of Markdown"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue_path = args.autopilot_dir / "queue.json"
    if not queue_path.exists():
        raise SystemExit(f"queue not found: {queue_path}")
    queue = read_json(queue_path)
    specs = queue.get("specs")
    if not isinstance(specs, list):
        raise SystemExit(f"queue specs is not a list: {queue_path}")

    summaries = [collect_spec_summary(item) for item in specs if isinstance(item, dict)]
    if args.json:
        print(json.dumps({"queue": queue, "summaries": summaries}, indent=2))
    else:
        print(render_markdown(queue, summaries, args.autopilot_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
