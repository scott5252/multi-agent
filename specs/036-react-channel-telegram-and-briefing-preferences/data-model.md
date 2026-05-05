# Data Model: React Channel, Telegram, And Briefing Preferences

## ChannelTelegramBriefingDashboard

- `page_id`: Stable React page identifier.
- `title`: Safe page title.
- `scope`: Active platform or tenant scope.
- `allowed_scope_options`: Backend-authorized scope choices.
- `readiness`: Channel and Telegram readiness summary.
- `tenant_config`: Tenant Telegram enablement and safe configuration form projection.
- `aliases`: Bounded alias records and action eligibility.
- `link_token_result`: Optional immediate one-time token creation result.
- `linked_identities`: Masked Telegram identity summaries.
- `webhook_diagnostics`: Safe validation and receipt summaries.
- `delivery_attempts`: Bounded delivery attempt rows.
- `run_status_links`: Safe run status summaries and links.
- `preference_profiles`: Current user's preference profile and admin-safe summaries.
- `states`: Safe empty, loading, denied, stale, dependency, audit, and validation states.
- `updated_at`: Backend timestamp.

## ChannelTelegramReadiness

- `status`: ready, partial, disabled, stale, failed, or unavailable.
- `channel_label`: Safe channel label.
- `telegram_enabled`: Whether tenant Telegram delivery is enabled.
- `webhook_status`: Current webhook validation category.
- `secret_reference_status`: Safe readiness category, never raw value.
- `linked_identity_count`: Bounded count.
- `alias_count`: Bounded count.
- `delivery_health_label`: Safe status for recent delivery attempts.
- `audit_reference`: Safe audit reference.

## TelegramTenantConfiguration

- `tenant_id`: Authorized tenant id or null for platform summary.
- `tenant_label`: Safe tenant label.
- `enabled`: Tenant enablement state.
- `bot_token_reference_label`: Safe reference label or readiness category.
- `webhook_secret_reference_label`: Safe reference label or readiness category.
- `webhook_url_status`: Safe readiness status, not full secret-bearing URL.
- `revision`: Backend revision token.
- `actions`: Authorized actions such as validate webhook or save config.

## TelegramAliasRecord

- `alias_id`: Stable safe alias id.
- `tenant_label`: Safe tenant label.
- `alias_text`: Safe natural-language alias, such as `Morning briefing`.
- `target_summary`: Safe workflow or channel target summary.
- `protected_readiness`: ready, blocked, missing_identity, missing_config, or validation_error.
- `status`: active, disabled, pending_validation, or deleted.
- `revision`: Backend revision token.
- `last_used_at`: Optional timestamp.
- `audit_reference`: Safe audit reference.
- `actions`: Backend-authorized create/edit/disable/delete/readiness actions.

## LinkTokenResult

- `link_token_request_id`: Stable safe request id.
- `token_value`: Present only on immediate creation result.
- `masked_status`: Summary for later page loads.
- `expires_at`: Expiration timestamp.
- `consumed_at`: Optional consumption timestamp.
- `next_step`: Safe guidance.
- `audit_reference`: Safe audit reference.

## LinkedTelegramIdentitySummary

- `identity_id`: Stable safe id.
- `principal_label`: Safe principal display label.
- `telegram_label`: Masked Telegram identity label.
- `chat_label`: Masked chat label.
- `linked_at`: Timestamp.
- `status`: linked, pending, revoked, or stale.
- `audit_reference`: Safe audit reference.

## DeliveryAttemptSummary

- `attempt_id`: Stable safe id.
- `tenant_label`: Safe tenant label.
- `alias_label`: Safe alias label.
- `status`: delivered, retrying, failed, skipped, or unavailable.
- `retry_category`: none, retryable, permanent, throttled, policy_denied, or dependency_unavailable.
- `bot_api_boundary_status`: mocked, skipped, delivered, failed, or unavailable.
- `run_status_href`: Optional safe link.
- `safe_error_summary`: Safe diagnostic category.
- `attempted_at`: Timestamp.
- `trace_reference`: Safe trace reference.
- `audit_reference`: Safe audit reference.

## WebhookDiagnosticSummary

- `diagnostic_id`: Stable safe id.
- `status`: valid, stale, failed, unavailable, or pending.
- `last_checked_at`: Timestamp.
- `safe_update_summary`: Safe webhook receipt category.
- `receipt_count`: Bounded count.
- `next_step`: Safe remediation guidance.
- `audit_reference`: Safe audit reference.

## RunStatusSummary

- `run_id`: Safe run id or masked reference.
- `status`: queued, running, waiting, completed, failed, cancelled, or unavailable.
- `workflow_label`: Safe workflow label.
- `requested_by_label`: Safe requester label.
- `started_at`: Optional timestamp.
- `completed_at`: Optional timestamp.
- `next_step`: Safe user-facing guidance.
- `href`: Authorized safe status link.
- `audit_reference`: Safe audit reference.

## BriefingPreferenceProfile

- `profile_id`: Tenant/principal profile id.
- `tenant_label`: Safe tenant label.
- `principal_label`: Safe user label.
- `timezone`: Valid timezone display.
- `location_summary`: Redacted location summary.
- `news_topics_summary`: Count or safe category summary.
- `vip_sender_summary`: Count or masked summary.
- `workday_hours`: Safe range display.
- `commute_mode`: Safe enum label.
- `default_account_summary`: Masked account readiness.
- `output_style`: Safe style label.
- `scheduled_time_summary`: Optional profile-only time label.
- `revision`: Immutable revision id.
- `runtime_ready`: Whether runtime resolver can use the profile.
- `audit_reference`: Safe audit reference.

## BriefingPreferenceMutationResult

- `status`: accepted, replayed, validation_error, denied, conflict, or audit_unavailable.
- `profile_summary`: Safe profile summary.
- `revision`: New immutable revision when accepted.
- `field_errors`: Safe validation errors.
- `artifact_reference`: Optional safe import/export artifact reference.
- `audit_reference`: Safe audit reference.
- `next_step`: Safe guidance.

## Validation Rules

- No schema field may render real bot token values, webhook secrets, full Telegram identifiers, link tokens after creation, private messages, raw preference values in admin summaries, raw prompts, run results, raw tool payloads, local filesystem paths, or unauthorized tenant labels.
- Tenant administrators may only receive records for their active tenant.
- Tenant users may only receive their own preference profile and authorized run status summaries.
- Link token values are only allowed in creation responses and never in bootstrap responses.
- All protected mutations require revision or idempotency evidence and an audit reference.
