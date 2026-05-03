from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from multi_agent_platform.testing.agent_bench.models import (
    AssertionComparator,
    AssertionEvaluation,
    AssertionKind,
)


def evaluate_deterministic_assertion(
    *,
    assertion_id: str | None,
    comparator: AssertionComparator,
    output: Mapping[str, Any],
    path: str | None = None,
    expected_value: Any = None,
    expected_schema: Mapping[str, Any] | None = None,
    threshold: float | int | None = None,
    severity: str = "blocking",
) -> AssertionEvaluation:
    actual = _resolve_path(output, path)
    passed = False
    expected: Any = expected_value

    if comparator is AssertionComparator.EQUALS:
        passed = actual == expected_value
    elif comparator is AssertionComparator.CONTAINS:
        passed = expected_value in actual if isinstance(actual, str | list) else False
    elif comparator is AssertionComparator.MATCHES_REGEX:
        passed = bool(re.search(str(expected_value), str(actual or "")))
    elif comparator is AssertionComparator.JSON_SCHEMA:
        expected = expected_schema or {}
        passed = _matches_schema(actual, expected)
    elif comparator is AssertionComparator.STATUS_IS:
        passed = str(actual) == str(expected_value)
    elif comparator is AssertionComparator.LATENCY_UNDER_MS:
        expected = threshold if threshold is not None else expected_value
        passed = _numeric(actual) <= _numeric(expected)
    elif comparator is AssertionComparator.USAGE_UNDER_TOKENS:
        expected = threshold if threshold is not None else expected_value
        passed = _numeric(actual) <= _numeric(expected)

    return AssertionEvaluation(
        assertion_id=assertion_id,
        kind=AssertionKind.DETERMINISTIC,
        comparator=comparator,
        path=path,
        passed=passed,
        expected=expected,
        actual=actual,
        safe_message="Assertion passed" if passed else "Assertion failed",
        severity=severity,
    )


def evaluate_evaluator_assertion(
    *,
    assertion_id: str | None,
    score: float,
    threshold: float,
    rationale: str,
    severity: str = "blocking",
) -> AssertionEvaluation:
    passed = score >= threshold
    return AssertionEvaluation(
        assertion_id=assertion_id,
        kind=AssertionKind.EVALUATOR,
        comparator=None,
        path="evaluator.score",
        passed=passed,
        expected=threshold,
        actual=score,
        safe_message=rationale[:240]
        or ("Evaluator passed" if passed else "Evaluator failed"),
        severity=severity,
    )


def _resolve_path(output: Mapping[str, Any], path: str | None) -> Any:
    if not path:
        return output
    current: Any = output
    for part in path.split("."):
        if isinstance(current, Mapping):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            current = current[index] if 0 <= index < len(current) else None
        else:
            return None
    return current


def _numeric(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def _matches_schema(actual: Any, schema: Mapping[str, Any]) -> bool:
    expected_type = schema.get("type")
    if expected_type == "object" and not isinstance(actual, Mapping):
        return False
    if expected_type == "array" and not isinstance(actual, list):
        return False
    if expected_type == "string" and not isinstance(actual, str):
        return False
    if expected_type == "number" and not isinstance(actual, int | float):
        return False
    if expected_type == "boolean" and not isinstance(actual, bool):
        return False
    if isinstance(actual, Mapping):
        required = schema.get("required", [])
        if any(key not in actual for key in required):
            return False
        properties = schema.get("properties", {})
        if isinstance(properties, Mapping):
            for key, child_schema in properties.items():
                if key in actual and isinstance(child_schema, Mapping):
                    if not _matches_schema(actual[key], child_schema):
                        return False
    return True
