# Data Model: React User And Tenant Membership Administration

## MembershipDashboard

- `page_id`
- `title`
- `description`
- `scope`
- `summary_cards`
- `sections`
- `directory`
- `filters`
- `allowed_scope_options`
- `invite_form`
- `role_grant_form`
- `status_actions`
- `access_history`
- `audit_timeline`
- `common_states`

Validation:

- Scope is platform or tenant.
- Tenant administrators receive only their own tenant scope option.
- All display fields are redaction-safe.

## UserDirectoryEntry

- `principal_identity_id`
- `display_name`
- `masked_email`
- `safe_subject_suffix`
- `principal_status`
- `tenant_memberships`
- `role_summaries`
- `last_access_summary`
- `raw_identifier_detail`
- `authorized_actions`

Validation:

- Raw identifier detail is nullable unless backend-authorized.
- Email and subject summaries are masked by default.
- Cross-tenant memberships are omitted for tenant administrators.

## InvitationSummary

- `invitation_id`
- `tenant_id`
- `tenant_label`
- `masked_email`
- `email_hash_label`
- `requested_roles`
- `status`
- `expires_label`
- `replayed`
- `next_request_effect`
- `audit_reference_id`
- `authorized_actions`

Validation:

- Invitation replay is explicit.
- Full email is not included in safe summaries.
- Requested roles are backend-eligible for the acting principal.

## PrincipalLinkSummary

- `principal_identity_id`
- `display_name`
- `masked_email`
- `safe_subject_suffix`
- `link_status`
- `conflict_summary`
- `audit_reference_id`

Validation:

- Full external subject is omitted unless specifically authorized in a detail
  panel.
- Duplicate subject conflicts fail closed.

## RoleGrantSummary

- `role_grant_id`
- `principal_identity_id`
- `principal_label`
- `scope_type`
- `tenant_id`
- `tenant_label`
- `role_code`
- `role_label`
- `grant_status`
- `effective_label`
- `revoked_label`
- `next_request_effect`
- `audit_reference_id`
- `authorized_actions`

Validation:

- Tenant admins can only receive eligible tenant-scoped role choices.
- Platform roles require platform admin authority.
- Revoked grants remain visible in audit/history summaries.

## MembershipStatusSummary

- `tenant_membership_id`
- `principal_identity_id`
- `tenant_id`
- `tenant_label`
- `membership_status`
- `revision`
- `membership_source`
- `status_reason`
- `authorized_actions`

Validation:

- Status actions require current revision and confirmation.
- Removed or suspended memberships remain audit-visible.

## AccessHistoryRecord

- `access_history_id`
- `principal_label`
- `tenant_label`
- `surface_key`
- `requested_action`
- `decision`
- `reason_category`
- `role_source_summary`
- `timestamp_label`
- `trace_id`
- `audit_reference_id`

Validation:

- History list is bounded.
- Denied records do not confirm unauthorized resource details.

## MembershipAuditRecord

- `audit_reference_id`
- `domain`
- `actor_label`
- `target_label`
- `tenant_scope_label`
- `action`
- `outcome`
- `safe_diff_summary`
- `timestamp_label`
- `redaction_class`

Validation:

- No raw email, full subject, password, credential, local path, or unauthorized
  tenant label is allowed.

## MembershipMutationResult

- `status`
- `summary`
- `toast`
- `directory_entry`
- `invitation`
- `principal_link`
- `role_grant`
- `membership_status`
- `access_history`
- `audit_reference_id`
- `field_errors`
- `stale_conflict`
- `idempotency_replay`
- `confirmation`
- `next_request_effect`

Validation:

- Mutation status is backend-owned.
- Stale conflicts include current revision recovery.
- Confirmation is explicit for access-changing actions.
