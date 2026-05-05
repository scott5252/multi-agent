# UI Contract: React Admin Migration Hardening

## Route

- `/admin/app`
- `/admin/app/migration`

Both routes render the React admin shell and migration hardening dashboard for authorized principals. Unauthenticated users are denied before protected dashboard data is returned.

## Dashboard Regions

1. **Migration Summary Header**
   - Shows total destinations, React primary count, redirect count, retained fallback count, retirement candidates, blocked count, and overall status.
   - Includes updated timestamp and safe next step.

2. **Parity Matrix**
   - Groups routes by admin area.
   - Shows legacy route, React route, decision, scope requirement, auth modes, evidence, preserved redirect state, fallback notice, retirement eligibility, rollback reference, and audit reference.
   - Rows are bounded and dense for scanning.

3. **Rollback Plan**
   - Shows feature flag label, asset version label, owner, reviewed timestamp, rollback steps, and verification steps.
   - Does not contain machine-local paths or production credentials.

4. **Performance Budget**
   - Shows route bootstrap, interactivity, and compressed asset measurements with pass/warning/fail states.
   - Shows mitigation notes when a budget is close to or over its limit.

5. **Accessibility Audit**
   - Shows viewport coverage, keyboard status, focus status, landmark status, label status, contrast-sensitive state, text-overlap status, and evidence references.

6. **Redaction And Tenant Sweeps**
   - Shows checked artifact counts, unsafe match counts, safe summaries, and evidence references.
   - Unsafe matches must be zero for acceptance.

7. **Migration States**
   - Shows retained fallback, blocked retirement, rollback, stale evidence, or audit-unavailable states when present.

## Expected Interactions

- Platform admins can review the full matrix.
- Tenant admins see tenant-safe route status and denied platform-only decisions without platform-only payloads.
- Tenant users see user-safe route coverage and preference/run-status migration notes only.
- Rows link to React destinations or legacy fallback routes only when the current principal is authorized.
- No browser logic determines whether retirement is allowed; the backend contract owns that decision.

## Empty, Error, And Loading States

- Loading state says migration evidence is being loaded.
- Dependency-unavailable state links to the existing admin console.
- Empty matrix state explains that no route evidence is available and blocks retirement.
- Denied state uses the shared safe problem pattern.

## Redaction Rules

The UI must not render raw secrets, credential values, provider headers, raw prompts, raw completions, raw memory content, private channel messages, raw run payloads, raw tool payloads, raw package payloads, raw test transcripts, private briefing preference values, full Telegram identifiers, one-time link tokens, stack traces, local filesystem paths, or unauthorized tenant labels.
