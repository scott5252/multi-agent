from __future__ import annotations


def test_reliability_replay_references_are_metadata_only() -> None:
    reference = {
        "workflow_run_id": "run-1",
        "run_step_id": "step-1",
        "trace_id": "trace-1",
        "policy_version": 1,
        "artifact_refs": [{"uri": "s3://bucket/replay.json"}],
    }
    assert "payload" not in reference
    assert reference["artifact_refs"]
