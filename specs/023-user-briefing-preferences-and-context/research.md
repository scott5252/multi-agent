# Research: User Briefing Preferences And Context

## Decision: Dedicated Tables With Immutable Revisions

**Decision**: Store the current profile in `briefing_preference_profiles` and
append every update to `briefing_preference_revisions`.

**Rationale**: Briefing preferences are operational user context used during run
creation. They need tenant/principal lookup, optimistic revision checks,
import/export, admin summaries, and runtime provenance. Dedicated tables provide
fast fail-closed lookup while preserving immutable history.

**Alternatives considered**:

- Generic immutable memory only: rejected because admin summaries, import/export,
  and field validation would require bespoke indexing and filtering outside the
  memory domain.
- In-memory service state: rejected because it violates durability and runtime
  restart requirements.

## Decision: Safe References For Account Fields

**Decision**: Calendar and email account fields accept only reference-like
values with approved prefixes such as `delegated:`, `secret-ref:`, `account:`,
`local:`, `test:`, or `none`.

**Rationale**: The profile must identify which delegated account to use without
storing raw credentials. Prefix validation prevents obvious token/API key
mistakes during local QA.

**Alternatives considered**:

- Accept arbitrary strings and redact later: rejected because raw values may
  already be persisted.

## Decision: IANA Timezone Validation

**Decision**: Validate timezones with `zoneinfo.ZoneInfo`.

**Rationale**: Scheduled briefing time and workday context are meaningful only
when the timezone is valid and portable across worker processes.

## Decision: Admin Safe Summaries

**Decision**: Admin summaries show timezone, location label, list counts, masked
sample values, account reference labels, schedule enabled/time, style, readiness,
revision id, content digest prefix, and timestamps.

**Rationale**: Operators can verify rollout readiness without expanding access
to private sender lists or credential-bearing account selectors.

## Decision: Runtime Resolver Contract

**Decision**: Runtime resolution returns a typed result with `available`,
`preferences`, `safe_summary`, `revision_id`, `content_digest`, and `trace_id`.
Missing or denied results contain no private fields.

**Rationale**: Channel handlers, future schedulers, and workflow graph execution
can share one contract and pin the exact preference revision used to start a
run.

## Decision: Import/Export Own Profile Only

**Decision**: v1 supports JSON export and import for the authenticated
principal's own profile; admin bulk import is out of scope.

**Rationale**: This meets user portability needs while avoiding high-risk
cross-principal ownership ambiguity.
