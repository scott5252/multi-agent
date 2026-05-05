import type {
  BriefingPreferenceMutationResult,
  ChannelMutationResult,
  ChannelTelegramBriefingDashboard,
  DeliveryDiagnosticList,
  LinkTokenResult,
  RunStatusSummary,
} from "../api/generated/reactAdminApi";

export const channelDashboard: ChannelTelegramBriefingDashboard = {
  page_id: "qa036-channel-telegram-briefing",
  title: "Channel, Telegram, and Briefing Preferences",
  description:
    "Review channel readiness, Telegram aliases, delivery diagnostics, safe run status, and briefing preference evidence.",
  scope: {
    scope_type: "tenant",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    label: "Acme",
  },
  allowed_scope_options: [],
  readiness: [
    {
      readiness_id: "readiness-acme-qa036",
      status: "ready",
      channel_label: "Telegram",
      tenant_label: "Acme",
      telegram_enabled: true,
      webhook_status: "valid",
      secret_reference_status: "ready",
      linked_identity_count: 2,
      alias_count: 2,
      delivery_health_label: "Recent delivery evidence is healthy",
      preference_resolver_label: "Briefing resolver ready",
      audit_reference: "audit-qa036-readiness-acme",
      next_step: "Refresh webhook validation before changing aliases.",
    },
  ],
  tenant_configs: [
    {
      tenant_id: "11111111-1111-1111-1111-111111111111",
      tenant_label: "Acme",
      enabled: true,
      bot_token_reference_label: "Telegram provider ref ready",
      webhook_signing_reference_label: "Webhook signing ref ready",
      webhook_url_status: "ready",
      revision: "telegram-config-rev-qa036",
      last_validated_at: "2026-05-05T16:42:00Z",
      audit_reference: "audit-qa036-config-acme",
      actions: [
        {
          action_id: "validate-webhook",
          label: "Validate",
          href: "/admin/app/channels/telegram/webhook/validate",
          method: "post",
          enabled: true,
          disabled_reason: null,
        },
      ],
    },
  ],
  aliases: [
    {
      alias_id: "alias-morning-qa036",
      tenant_label: "Acme",
      alias_text: "Morning briefing",
      target_summary: "Daily briefing workflow",
      protected_readiness: "ready",
      status: "active",
      revision: "alias-rev-qa036",
      last_used_at: "2026-05-05T15:00:00Z",
      audit_reference: "audit-qa036-alias-acme",
      actions: [
        {
          action_id: "refresh",
          label: "Refresh",
          href: "/admin/app/channels/telegram/aliases/alias-morning-qa036/refresh",
          method: "post",
          enabled: true,
          disabled_reason: null,
        },
      ],
    },
  ],
  link_token_result: {
    link_token_request_id: "link-token-request-qa036-hidden",
    token_value: null,
    masked_status: "Previously created code is hidden after creation.",
    expires_at: "2026-05-05T17:04:00Z",
    consumed_at: null,
    next_step: "Create a new code if the user did not link in time.",
    audit_reference: "audit-qa036-link-token-hidden",
    display_mode: "masked",
  },
  linked_identities: [
    {
      identity_id: "identity-acme-qa036",
      principal_label: "Acme briefing user",
      telegram_label: "Telegram user tg-***-1842",
      chat_label: "Chat chat-***-9081",
      linked_at: "2026-05-02T17:00:00Z",
      status: "linked",
      audit_reference: "audit-qa036-identity-acme",
    },
  ],
  webhook_diagnostics: [
    {
      diagnostic_id: "webhook-acme-qa036",
      status: "valid",
      last_checked_at: "2026-05-05T16:42:00Z",
      safe_update_summary: "Mock-safe receipt categories are current",
      receipt_count: 3,
      next_step: "Run validation again after configuration changes.",
      audit_reference: "audit-qa036-webhook-acme",
    },
  ],
  delivery_attempts: [
    {
      attempt_id: "delivery-acme-qa036-1",
      tenant_label: "Acme",
      alias_label: "Morning briefing",
      status: "delivered",
      retry_category: "none",
      bot_api_boundary_status: "mocked",
      run_status_href: "/admin/app/channels/runs/qa036-run-morning-briefing",
      safe_error_summary: "No delivery issue",
      attempted_at: "2026-05-05T16:48:00Z",
      trace_reference: "trace-qa036-delivery-acme",
      audit_reference: "audit-qa036-delivery-acme",
    },
  ],
  run_status_links: [
    {
      run_id: "qa036-run-morning-briefing",
      status: "running",
      workflow_label: "Daily briefing workflow",
      requested_by_label: "Acme briefing user",
      started_at: "2026-05-05T16:54:00Z",
      completed_at: null,
      next_step: "Review safe progress only.",
      href: "/admin/app/channels/runs/qa036-run-morning-briefing",
      artifact_references: ["artifact-ref-qa036-safe-status"],
      audit_reference: "audit-qa036-run-acme",
    },
  ],
  preference_profiles: {
    current_user_profile: {
      profile_id: "briefing-profile-current-qa036",
      tenant_label: "Acme",
      principal_label: "tenant-user-acme",
      timezone: "America/New_York",
      location_summary: "Metro area summary",
      news_topics_summary: "4 topic categories",
      vip_sender_summary: "3 masked sender hints",
      workday_hours: "08:30-17:30",
      commute_mode: "transit",
      default_account_summary: "2 masked account refs",
      output_style: "executive",
      scheduled_time_summary: "Profile preference 07:45",
      revision: "briefing-pref-rev-qa036",
      runtime_ready: true,
      audit_reference: "audit-qa036-pref-acme",
    },
    admin_summaries: [],
    import_export_evidence: ["preference-artifact-qa036"],
  },
  states: [
    {
      reason: "stale_validation",
      title: "Validation age",
      detail: "Webhook validation is older than the preferred review window.",
      next_action: "Run validation when changing Telegram settings.",
      audit_reference: "audit-qa036-validation-age",
    },
  ],
  common_states: [],
  updated_at: "2026-05-05T17:00:00Z",
};

export const channelMutation: ChannelMutationResult = {
  status: "accepted",
  summary: "Webhook validation completed with local mock-safe evidence.",
  revision: "telegram-config-rev-qa036",
  idempotency_key: "qa036-webhook",
  replayed: false,
  field_errors: {},
  audit_reference: "audit-qa036-webhook-validate",
  next_step: "Delivery diagnostics can now use the refreshed readiness state.",
};

export const linkTokenResult: LinkTokenResult = {
  link_token_request_id: "link-token-request-qa036",
  token_value: "pair-code-10-qa036",
  masked_status: "Visible once. Future views show masked status only.",
  expires_at: "2026-05-05T17:10:00Z",
  consumed_at: null,
  next_step: "Share this code with Acme briefing user before it expires.",
  audit_reference: "audit-qa036-link-token-create",
  display_mode: "immediate",
};

export const deliveryDiagnostics: DeliveryDiagnosticList = {
  attempts: channelDashboard.delivery_attempts,
  limit: 25,
  total_rows: 1,
  webhook_receipts: channelDashboard.webhook_diagnostics,
};

export const runStatus: RunStatusSummary = channelDashboard.run_status_links[0];

export const preferenceMutation: BriefingPreferenceMutationResult = {
  status: "accepted",
  profile_summary: "Preference profile saved with redacted summaries.",
  revision: "briefing-pref-rev-qa036-next",
  field_errors: {},
  artifact_reference: "preference-export-artifact-qa036",
  row_count: 1,
  audit_reference: "audit-qa036-preference-save",
  next_step: "Runtime preference resolution is ready for the next briefing run.",
};
