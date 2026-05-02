from __future__ import annotations

from multi_agent_platform.testing.agent_bench.assertions import (
    evaluate_deterministic_assertion,
    evaluate_evaluator_assertion,
)
from multi_agent_platform.testing.agent_bench.models import AssertionComparator


def test_deterministic_assertions_cover_paths_schema_latency_and_usage() -> None:
    output = {
        "status": "passed",
        "contract": {"summary": "safe intake summary"},
        "latency_ms": 42,
        "usage": {"total_tokens": 84},
    }

    assert evaluate_deterministic_assertion(
        assertion_id="a1",
        comparator=AssertionComparator.EQUALS,
        output=output,
        path="status",
        expected_value="passed",
    ).passed
    assert evaluate_deterministic_assertion(
        assertion_id="a2",
        comparator=AssertionComparator.CONTAINS,
        output=output,
        path="contract.summary",
        expected_value="intake",
    ).passed
    assert evaluate_deterministic_assertion(
        assertion_id="a3",
        comparator=AssertionComparator.JSON_SCHEMA,
        output=output,
        path="contract",
        expected_schema={
            "type": "object",
            "required": ["summary"],
            "properties": {"summary": {"type": "string"}},
        },
    ).passed
    assert evaluate_deterministic_assertion(
        assertion_id="a4",
        comparator=AssertionComparator.LATENCY_UNDER_MS,
        output=output,
        path="latency_ms",
        threshold=100,
    ).passed
    assert evaluate_deterministic_assertion(
        assertion_id="a5",
        comparator=AssertionComparator.USAGE_UNDER_TOKENS,
        output=output,
        path="usage.total_tokens",
        threshold=100,
    ).passed


def test_assertion_failures_and_evaluator_thresholds_are_explicit() -> None:
    failed = evaluate_deterministic_assertion(
        assertion_id="a1",
        comparator=AssertionComparator.MATCHES_REGEX,
        output={"status": "failed"},
        path="status",
        expected_value="pass.*",
    )
    evaluator = evaluate_evaluator_assertion(
        assertion_id="e1",
        score=0.72,
        threshold=0.8,
        rationale="Evaluator rejected redacted answer",
    )

    assert failed.passed is False
    assert failed.safe_message == "Assertion failed"
    assert evaluator.passed is False
    assert evaluator.safe_message == "Evaluator rejected redacted answer"


def test_assertions_cover_nested_lists_schema_failures_and_default_messages() -> None:
    output = {
        "items": [{"name": "alpha"}, {"name": "beta"}],
        "latency_ms": "slow",
        "flags": {"ready": "yes"},
    }

    list_path = evaluate_deterministic_assertion(
        assertion_id="list-path",
        comparator=AssertionComparator.STATUS_IS,
        output=output,
        path="items.1.name",
        expected_value="beta",
    )
    root_schema = evaluate_deterministic_assertion(
        assertion_id="root-schema",
        comparator=AssertionComparator.JSON_SCHEMA,
        output=output,
        expected_schema={
            "type": "object",
            "required": ["items", "missing"],
            "properties": {"items": {"type": "array"}},
        },
    )
    child_schema = evaluate_deterministic_assertion(
        assertion_id="child-schema",
        comparator=AssertionComparator.JSON_SCHEMA,
        output=output,
        path="flags",
        expected_schema={
            "type": "object",
            "properties": {"ready": {"type": "boolean"}},
        },
    )
    numeric = evaluate_deterministic_assertion(
        assertion_id="numeric",
        comparator=AssertionComparator.LATENCY_UNDER_MS,
        output=output,
        path="latency_ms",
        threshold=100,
    )
    missing_path = evaluate_deterministic_assertion(
        assertion_id="missing",
        comparator=AssertionComparator.CONTAINS,
        output=output,
        path="items.10.name",
        expected_value="anything",
    )
    evaluator = evaluate_evaluator_assertion(
        assertion_id="empty-rationale",
        score=0.91,
        threshold=0.8,
        rationale="",
    )

    assert list_path.passed is True
    assert root_schema.passed is False
    assert child_schema.passed is False
    assert numeric.passed is False
    assert missing_path.actual is None
    assert evaluator.passed is True
    assert evaluator.safe_message == "Evaluator passed"
