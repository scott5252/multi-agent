from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]
JsonValue = JsonObject | list[Any] | str | int | float | bool | None

VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z0-9_.-]+)\}")


def repo_root_from(start: Path) -> Path:
    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for path in (candidate, *candidate.parents):
        if (path / ".git").exists() and (path / ".specify").exists():
            return path
    return Path.cwd().resolve()


def parse_config_file(path: Path) -> JsonObject:
    text = path.read_text(encoding="utf-8")

    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        loaded = None

    if loaded is None and path.suffix == ".toml":
        loaded = tomllib.loads(text)

    if loaded is None:
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError as exc:
            raise SystemExit(
                f"{path} is not JSON/TOML. Install PyYAML or use JSON syntax "
                "inside the .yml file."
            ) from exc
        loaded = yaml.safe_load(text)

    if not isinstance(loaded, dict):
        raise SystemExit(f"{path} must contain a mapping/object at the top level")
    return loaded


def deep_merge(base: JsonObject, override: JsonObject) -> JsonObject:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_extends_path(config_path: Path, extends_value: str) -> Path:
    extends_path = Path(extends_value)
    if not extends_path.is_absolute():
        extends_path = config_path.parent / extends_path
    return extends_path.resolve()


def load_config(
    path: Path,
    seen: set[Path] | None = None,
    *,
    interpolate_result: bool = True,
) -> JsonObject:
    config_path = path.resolve()
    seen = seen or set()
    if config_path in seen:
        raise SystemExit(f"cyclic autopilot config extends detected: {config_path}")
    seen.add(config_path)

    config = parse_config_file(config_path)
    extends_value = config.pop("extends", None)

    merged: JsonObject = {}
    if extends_value:
        if isinstance(extends_value, str):
            extends_values = [extends_value]
        elif isinstance(extends_value, list) and all(
            isinstance(item, str) for item in extends_value
        ):
            extends_values = extends_value
        else:
            raise SystemExit(f"{config_path}: extends must be a string or string list")

        for item in extends_values:
            parent_path = resolve_extends_path(config_path, item)
            merged = deep_merge(
                merged,
                load_config(parent_path, seen=seen, interpolate_result=False),
            )

    merged = deep_merge(merged, config)
    if not interpolate_result:
        return merged

    variables = merged.get("variables", {})
    if variables and not isinstance(variables, dict):
        raise SystemExit(f"{config_path}: variables must be an object")

    return interpolate(merged, variables if isinstance(variables, dict) else {})


def interpolate(value: JsonValue, variables: JsonObject) -> JsonValue:
    if isinstance(value, dict):
        return {key: interpolate(item, variables) for key, item in value.items()}
    if isinstance(value, list):
        return [interpolate(item, variables) for item in value]
    if isinstance(value, str):
        return VARIABLE_PATTERN.sub(
            lambda match: str(resolve_variable(match.group(1), variables)),
            value,
        )
    return value


def resolve_variable(name: str, variables: JsonObject) -> Any:
    current: Any = variables
    for part in name.split("."):
        if not isinstance(current, dict) or part not in current:
            raise SystemExit(f"unknown autopilot config variable: {name}")
        current = current[part]
    return current
