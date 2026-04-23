from __future__ import annotations

from pydantic import BaseModel, Field


class FieldHelpDefinition(BaseModel):
    field_key: str
    label: str
    title: str
    explanation: str
    runtime_impact: str
    example: str | None = None
    validation_hint: str | None = None


class EditorOption(BaseModel):
    value: str
    label: str


class WorkflowEditorMetadataResponse(BaseModel):
    field_help: dict[str, FieldHelpDefinition] = Field(default_factory=dict)
    scope_options: list[EditorOption] = Field(default_factory=list)
    workflow_kind_options: list[EditorOption] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)
