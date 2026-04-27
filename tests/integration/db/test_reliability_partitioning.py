from __future__ import annotations

from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.reliability import AdmissionDecisionRecord


def test_reliability_models_register_with_metadata() -> None:
    import_models()
    assert AdmissionDecisionRecord.__tablename__ in {
        table.name for table in AdmissionDecisionRecord.metadata.sorted_tables
    }
