import { useEffect, useState } from "react";

import {
  createTelegramLinkToken,
  exportBriefingPreferences,
  fetchChannelTelegramBriefingDashboard,
  importBriefingPreferences,
  runTelegramAliasAction,
  saveBriefingPreferences,
  saveTelegramAlias,
  saveTelegramConfig,
  validateTelegramWebhook,
} from "../../api/client";
import type {
  BriefingPreferenceMutationResult,
  ChannelMutationResult,
  ChannelTelegramBriefingDashboard,
  LinkTokenResult,
  TelegramAliasRecord,
  TelegramTenantConfiguration,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { AliasManagementPanel } from "./AliasManagementPanel";
import { BriefingPreferenceAdminPanel } from "./BriefingPreferenceAdminPanel";
import { BriefingPreferenceMutationResultPanel } from "./BriefingPreferenceMutationResultPanel";
import { BriefingPreferencePanel } from "./BriefingPreferencePanel";
import { ChannelReadinessHeader } from "./ChannelReadinessHeader";
import { ChannelStatePanel } from "./ChannelStatePanel";
import { DeliveryDiagnosticsPanel } from "./DeliveryDiagnosticsPanel";
import { IdentityLinkPanel } from "./IdentityLinkPanel";
import { ReadinessCardGrid } from "./ReadinessCardGrid";
import { TelegramConfigPanel } from "./TelegramConfigPanel";
import { WebhookValidationPanel } from "./WebhookValidationPanel";

export function ChannelTelegramBriefingPage({ channelsUrl }: { channelsUrl: string }) {
  const [dashboard, setDashboard] = useState<ChannelTelegramBriefingDashboard | null>(
    null,
  );
  const [mutation, setMutation] = useState<ChannelMutationResult | null>(null);
  const [tokenResult, setTokenResult] = useState<LinkTokenResult | null>(null);
  const [preferenceResult, setPreferenceResult] =
    useState<BriefingPreferenceMutationResult | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchChannelTelegramBriefingDashboard(channelsUrl)
      .then((payload) => {
        if (alive) {
          setDashboard(payload);
          setTokenResult(payload.link_token_result);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(caught instanceof Error ? caught.message : "Channels unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [channelsUrl]);

  async function refresh() {
    const payload = await fetchChannelTelegramBriefingDashboard(channelsUrl);
    setDashboard(payload);
    setTokenResult(payload.link_token_result);
    setLoadError(null);
  }

  async function handleConfigSave(config: TelegramTenantConfiguration) {
    setMutation(
      await saveTelegramConfig(withSearch("/admin/app/channels/telegram/config"), {
        bot_token_reference_label: config.bot_token_reference_label,
        enabled: config.enabled,
        idempotency_key: "qa036-config-save",
        revision: config.revision,
        webhook_signing_reference_label: config.webhook_signing_reference_label,
      }),
    );
  }

  async function handleWebhookValidate(config: TelegramTenantConfiguration) {
    setMutation(
      await validateTelegramWebhook(
        withSearch("/admin/app/channels/telegram/webhook/validate"),
        {
          idempotency_key: "qa036-webhook",
          revision: config.revision,
          tenant_id: config.tenant_id,
        },
      ),
    );
  }

  async function handleAliasCreate() {
    setMutation(
      await saveTelegramAlias(withSearch("/admin/app/channels/telegram/aliases"), {
        alias_id: null,
        alias_text: "Morning briefing",
        idempotency_key: "qa036-alias-create",
        revision: null,
        target_summary: "Daily briefing workflow",
      }),
    );
  }

  async function handleAliasAction(alias: TelegramAliasRecord, action: string) {
    setMutation(
      await runTelegramAliasAction(
        withSearch(`/admin/app/channels/telegram/aliases/${alias.alias_id}/${action}`),
        {
          idempotency_key: `qa036-alias-${action}`,
          revision: alias.revision,
        },
      ),
    );
  }

  async function handleCreateToken() {
    setTokenResult(
      await createTelegramLinkToken(
        withSearch("/admin/app/channels/telegram/link-tokens"),
        {
          expires_in_minutes: 10,
          idempotency_key: "qa036-link-token",
          principal_label: "Acme briefing user",
        },
      ),
    );
  }

  async function handlePreferenceSave() {
    setPreferenceResult(
      await saveBriefingPreferences(withSearch("/admin/app/channels/briefing/preferences"), {
        commute_mode: "transit",
        default_account_summary: "2 masked account refs",
        idempotency_key: "qa036-preference-save",
        location_summary: "Metro area summary",
        news_topics_summary: "4 topic categories",
        output_style: "executive",
        revision: dashboard?.preference_profiles.current_user_profile?.revision ?? null,
        scheduled_time_summary: "Profile preference 07:45",
        timezone: "America/New_York",
        vip_sender_summary: "3 masked sender hints",
        workday_hours: "08:30-17:30",
      }),
    );
  }

  async function handlePreferenceImport() {
    setPreferenceResult(
      await importBriefingPreferences(
        withSearch("/admin/app/channels/briefing/preferences/import"),
        {
          artifact_reference: "preference-artifact-qa036",
          field_count: 9,
          idempotency_key: "qa036-preference-import",
        },
      ),
    );
  }

  async function handlePreferenceExport() {
    setPreferenceResult(
      await exportBriefingPreferences(
        withSearch("/admin/app/channels/briefing/preferences/export"),
        {
          format: "json",
          idempotency_key: "qa036-preference-export",
        },
      ),
    );
  }

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Channel workspace unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading channel readiness, Telegram aliases, and preferences.",
          title: "Loading channels",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="channel-page">
      <ChannelReadinessHeader dashboard={dashboard} onRefresh={() => void refresh()} />
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <ReadinessCardGrid readiness={dashboard.readiness} />
      <ChannelStatePanel states={dashboard.states} />
      <TelegramConfigPanel
        configs={dashboard.tenant_configs}
        result={mutation}
        onSave={(config) => void handleConfigSave(config)}
      />
      <WebhookValidationPanel
        configs={dashboard.tenant_configs}
        diagnostics={dashboard.webhook_diagnostics}
        result={mutation}
        onValidate={(config) => void handleWebhookValidate(config)}
      />
      <AliasManagementPanel
        aliases={dashboard.aliases}
        result={mutation}
        onAction={(alias, action) => void handleAliasAction(alias, action)}
        onCreate={() => void handleAliasCreate()}
      />
      <IdentityLinkPanel
        identities={dashboard.linked_identities}
        tokenResult={tokenResult}
        onCreateToken={() => void handleCreateToken()}
      />
      <DeliveryDiagnosticsPanel
        attempts={dashboard.delivery_attempts}
        receipts={dashboard.webhook_diagnostics}
        onOpenRun={(href) => {
          window.location.assign(href);
        }}
      />
      <BriefingPreferencePanel
        profile={dashboard.preference_profiles.current_user_profile}
        onSave={() => void handlePreferenceSave()}
      />
      <BriefingPreferenceAdminPanel
        evidence={dashboard.preference_profiles.import_export_evidence}
        summaries={dashboard.preference_profiles.admin_summaries}
        onExport={() => void handlePreferenceExport()}
        onImport={() => void handlePreferenceImport()}
      />
      <BriefingPreferenceMutationResultPanel result={preferenceResult} />
    </div>
  );
}

function withSearch(url: string): string {
  if (!window.location.search || url.includes("?")) {
    return url;
  }
  return `${url}${window.location.search}`;
}
