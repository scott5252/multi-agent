# Research: Generic Scenario Intake And Durable Draft Blueprint

## Decisions

### Decision 1: Compose existing React Admin workflow APIs
Use existing workflow draft create action, full document save action, validation refresh, and generated React API contracts.

**Rationale**: Existing backend contracts already own workflow durability, validation, evidence, tenant scope, audit, and publish readiness.

**Alternatives considered**:
- New onboarding backend route family: rejected because it would duplicate workflow registry and builder contracts.
- Browser-only setup state: rejected because publish and readiness decisions must remain backend-owned.

### Decision 2: Fixed-frame steps with pagination

Use a compact step rail, bounded body, and fixed footer. Collections are paged or summarized instead of made scrollable.

**Rationale**: The roadmap requires every screen to fit 1280 x 800 without page or panel scrolling.

**Alternatives considered**:
- Long forms: rejected because they fail the no-scroll requirement.
- Nested cards: rejected to keep the operational UI dense and predictable.

### Decision 3: Scenario-neutral defaults only

The wizard may generate editable generic scaffolding, but it must not encode tutorial product names or scenario-specific wording.

**Rationale**: The onboarding path is for arbitrary workflows, not for replaying Design Reviewer or Daily Briefing tutorials.

## Risks

- Existing data may produce many roles, contracts, or evidence items; bounded pagination mitigates overflow.
- Backend readiness may block publish; recovery messaging keeps this truthful.
- QA environments may be clean; empty-state metadata and create actions must be real and visible.
