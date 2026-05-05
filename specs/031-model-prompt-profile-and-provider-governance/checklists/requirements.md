# Requirements Checklist: Model, Prompt, Profile, And Provider Governance

**Purpose**: Validate that the Spec 031 requirements are complete, testable, tenant-safe, and ready for planning.
**Created**: 2026-05-05
**Feature**: [spec.md](../spec.md)

## Specification Quality

- [X] CHK001 User stories identify platform-admin and tenant-admin journeys with independent tests.
- [X] CHK002 Acceptance scenarios are written in observable Given/When/Then form.
- [X] CHK003 Requirements are mandatory, measurable, and avoid implementation-only phrasing where user behavior is being specified.
- [X] CHK004 Edge cases cover credential reference failures, provider probe failures, unsafe prompt previews, tenant leakage, direct-call attempts, and audit uncertainty.
- [X] CHK005 Success criteria define local QA outcomes for provider governance, prompt preview, profile resolution, routing preview, provenance, dual auth, Playwright, and full Spec QA.

## Security And Privacy

- [X] CHK006 Requirements explicitly fail closed for authorization, tenant scope, credential policy, provider routing policy, direct-call guardrails, and audit persistence uncertainty.
- [X] CHK007 Requirements prohibit rendering, logging, exporting, or persisting raw secrets, resolved credential values, provider tokens, authorization headers, raw prompts, raw completions, provider payloads, private messages, memory, connector payloads, stack traces, local paths, and unauthorized tenant labels.
- [X] CHK008 Provider mutation and credential-reference mutation boundaries are specified as platform-admin only.
- [X] CHK009 Tenant visibility is limited to authorized provider catalog, prompt grants, profile grants, routing previews, policy history, and provenance.
- [X] CHK010 Local/CI validation avoids live provider, Telegram, credential, connector, and direct SDK calls.

## Coverage And Validation

- [X] CHK011 Dual-auth-mode validation is mandatory for local-principal and Auth0-shaped protected routes/actions.
- [X] CHK012 Backend-owned JSON contracts and generated TypeScript contracts are required.
- [X] CHK013 Prompt preview, provider probe, routing preview, credential diagnostics, direct-call guardrail, policy history, and run provenance evidence are all required.
- [X] CHK014 Existing Jinja/admin fallback routes remain available until the migration hardening spec retires them.
- [X] CHK015 QA documents, Playwright evidence, backend tests, frontend tests, generated contract checks, and full Spec QA are required before advancing.
