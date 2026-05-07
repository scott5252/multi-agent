# Research: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

## Decision: Reuse Existing React Workspaces

**Decision**: Use `/admin/app/memberships` and `/admin/app/channels` as the only
browser destinations for this spec.

**Rationale**: Specs 034 and 036 already added React membership and channel
workspaces with backend-owned contracts. Rebuilding new routes would increase
surface area and delay Jinja retirement.

**Alternatives Considered**:

- Keep Jinja fallback pages. Rejected because React UI2 requires complete Jinja
  removal.
- Add new React pages for every legacy route. Rejected because query-state
  redirects preserve old links with less duplicated UI state.

## Decision: Preserve API Routes

**Decision**: Keep all `/api/*` routes for memberships, Telegram, and briefing
preferences.

**Rationale**: React and tests already depend on those contracts. The target is
browser-rendered Jinja removal, not API retirement.

**Alternatives Considered**:

- Move old APIs under `/admin/app`. Rejected for this spec because it would
  change clients unrelated to Jinja deletion.

## Decision: Redirect Browser GET Routes

**Decision**: Old browser GET routes redirect to React with allowlisted query
keys.

**Rationale**: Redirects preserve bookmarks, direct links, saved filters, and
operator context while removing duplicate templates.

**Alternatives Considered**:

- Return 410 gone responses. Rejected for safe links because old bookmarks are
  expected to remain navigable during migration.

## Decision: Keep Browser Form Compatibility

**Decision**: Old browser form-post routes remain as non-Jinja compatibility
handlers around existing services, then redirect to React.

**Rationale**: The old routes may be present in user bookmarks, docs, or saved
browser sessions. Preserving service behavior reduces migration risk.

**Alternatives Considered**:

- Remove form routes. Rejected because destructive and mutation routes need
  explicit compatibility evidence before deletion.

## Decision: Token Visibility Is Creation-Only

**Decision**: Link tokens are visible only in immediate creation responses.
Redirects, summaries, logs, screenshots, and exports use safe token metadata.

**Rationale**: Link tokens are credential-like and must not be recoverable from
persisted admin pages after creation.

**Alternatives Considered**:

- Show raw tokens in diagnostics. Rejected as a secret hygiene violation.

## Decision: Delete Only Domain Templates

**Decision**: Delete `memberships/index.html`, `telegram/index.html`, and
`briefing_preferences/index.html`; keep admin shell templates and global Jinja
infrastructure for Spec 047.

**Rationale**: The remaining admin shell templates are shared infrastructure and
are outside Spec 045's bounded domain parity scope.

**Alternatives Considered**:

- Delete admin shell templates now. Rejected because Spec 047 owns final Jinja
  infrastructure decommission.
