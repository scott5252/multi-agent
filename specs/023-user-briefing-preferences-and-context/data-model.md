# Data Model: User Briefing Preferences And Context

## BriefingPreferenceProfile

Current head projection for one `(tenant_id, principal_id)`.

Fields:

- `briefing_preference_profile_id` UUID primary key
- `tenant_id` UUID, required, indexed
- `principal_id` string, required
- `location_label` string, required, max 120
- `timezone` string, required, valid IANA timezone
- `news_topics` JSON array of strings, max 10 entries
- `vip_senders` JSON array of strings, max 20 entries
- `workday_start` string `HH:MM`
- `workday_end` string `HH:MM`
- `commute_mode` enum string: `none`, `driving`, `transit`, `walking`, `cycling`, `remote`
- `calendar_account_ref` string, safe reference only
- `email_account_ref` string, safe reference only
- `output_style` enum string: `concise`, `standard`, `detailed`, `executive`
- `scheduled_enabled` boolean
- `scheduled_time` nullable `HH:MM`
- `current_revision_id` UUID
- `content_digest` string
- `revision_token` string
- `created_at`, `updated_at`

Constraints:

- Unique `(tenant_id, principal_id)`
- Index `(tenant_id, updated_at)`
- Workday start must be before workday end
- Scheduled time required only when `scheduled_enabled` is true

## BriefingPreferenceRevision

Immutable version of each profile update.

Fields:

- `briefing_preference_revision_id` UUID primary key
- `briefing_preference_profile_id` UUID
- `tenant_id` UUID
- `principal_id` string
- `revision_number` integer
- `preference_payload` JSON object
- `safe_summary` JSON object
- `content_digest` string
- `created_by_principal_id` string
- `created_at` timestamp
- `trace_id` string

Constraints:

- Unique `(briefing_preference_profile_id, revision_number)`
- Index `(tenant_id, principal_id, created_at)`

## BriefingPreferenceAuditEvent

Safe append-only evidence for lifecycle and runtime operations.

Fields:

- `briefing_preference_audit_event_id` UUID primary key
- `tenant_id` UUID nullable only for platform-scope denials
- `principal_id` string nullable
- `actor_principal_id` string nullable
- `action` enum string
- `decision` enum string: `allow`, `deny`, `validation_error`, `missing`
- `summary` string, safe text only
- `profile_id` UUID nullable
- `revision_id` UUID nullable
- `content_digest` string nullable
- `trace_id` string
- `redacted_metadata` JSON object
- `created_at` timestamp

## Runtime Context Shape

```json
{
  "available": true,
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "principal_id": "tenant-admin-acme",
  "revision_id": "33333333-3333-3333-3333-333333333333",
  "content_digest": "sha256:...",
  "preferences": {
    "location_label": "Providence, RI",
    "timezone": "America/New_York",
    "news_topics": ["AI", "markets"],
    "vip_senders": ["sarah@example.com"],
    "workday_start": "09:00",
    "workday_end": "17:30",
    "commute_mode": "driving",
    "calendar_account_ref": "delegated:calendar:primary",
    "email_account_ref": "delegated:gmail:primary",
    "output_style": "standard",
    "scheduled_enabled": true,
    "scheduled_time": "08:00"
  },
  "safe_summary": {
    "profile_ready": true,
    "timezone": "America/New_York",
    "topic_count": 2,
    "vip_sender_count": 1,
    "calendar_account_label": "delegated:***",
    "email_account_label": "delegated:***"
  }
}
```
