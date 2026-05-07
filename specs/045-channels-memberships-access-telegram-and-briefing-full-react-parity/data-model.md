# Data Model: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

## LegacyRedirectContext

- `source_route`: old browser route requested by the user.
- `react_destination`: React path selected by the compatibility handler.
- `tenant_id`: optional tenant scope preserved only when authorized.
- `panel`: optional React panel hint, such as `memberships`, `telegram`,
  `briefing`, `aliases`, `tokens`, `identities`, or `diagnostics`.
- `resource_id`: optional safe identifier for principal, membership, grant,
  alias, token metadata, or export metadata.
- `saved_filter_id`: optional saved filter identifier.
- `safe_query`: allowlisted query parameters forwarded to React.

## MembershipCompatibilityResult

- `status`: `redirected`, `mutated`, `denied`, or `not_found`.
- `destination`: React destination for the browser response.
- `mutation_summary`: safe summary for invitation, principal link, role grant,
  role revoke, principal status, or membership status actions.
- `audit_reference_id`: safe audit reference created by the existing service.
- `revision`: optional revision token when present in existing contracts.
- `redaction_notes`: bounded explanation of hidden email, subject, or tenant
  detail.

## TelegramCompatibilityResult

- `status`: `redirected`, `mutated`, `validated`, `denied`, or `not_found`.
- `destination`: React channel workspace destination.
- `tenant_id`: authorized tenant scope.
- `config_revision`: safe Telegram config revision.
- `alias_id`: optional alias identifier.
- `link_token_visible_once`: boolean indicating the current response is the
  immediate creation result.
- `token_metadata`: safe token expiration and audit metadata.
- `diagnostic_summary`: redacted readiness, identity, webhook, and delivery
  evidence.

## BriefingCompatibilityResult

- `status`: `redirected`, `saved`, `imported`, `exported`, `denied`, or
  `not_found`.
- `destination`: React channel briefing destination.
- `tenant_id`: authorized tenant scope.
- `profile_revision`: immutable briefing preference revision.
- `artifact_reference`: safe import/export artifact reference.
- `admin_summary`: redacted summary visible only to authorized admin scopes.
- `user_summary`: user-safe profile summary.

## DeletedTemplateEvidence

- `path`: retired template path.
- `old_routes`: browser routes formerly rendering the template.
- `replacement`: React route or safe compatibility response.
- `test_evidence`: focused tests proving route behavior.
- `scanner_evidence`: unit scanner test proving no converted runtime reference
  remains.
