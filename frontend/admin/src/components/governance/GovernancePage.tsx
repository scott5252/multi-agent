import { useEffect, useState } from "react";

import {
  fetchGovernanceDashboard,
  previewPrompt,
  previewRouting,
  resolveRuntimeProfile,
  runProviderProbe,
  savePromptSummary,
  saveRuntimeProfile,
} from "../../api/client";
import type {
  GovernanceDashboard,
  GovernanceMutationResult,
  ProfileResolutionPreview,
  SafePromptPreview,
} from "../../api/generated/reactAdminApi";
import {
  buildIdempotencyKey,
  generatedRevisionMarker,
} from "../../utils/adminActionMetadata";
import { CommonState } from "../states/CommonState";
import { GovernanceSectionNav } from "./GovernanceSectionNav";
import { PolicyHistoryPanel } from "./PolicyHistoryPanel";
import { ProfileGovernancePanel } from "./ProfileGovernancePanel";
import { PromptGovernancePanel } from "./PromptGovernancePanel";
import { ProviderGovernancePanel } from "./ProviderGovernancePanel";
import { ProvenancePanel } from "./ProvenancePanel";
import { RoutingPreviewPanel } from "./RoutingPreviewPanel";

export function GovernancePage({ governanceUrl }: { governanceUrl: string }) {
  const [dashboard, setDashboard] = useState<GovernanceDashboard | null>(null);
  const [activeSection, setActiveSection] = useState("setup");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [probeResult, setProbeResult] = useState<GovernanceMutationResult | null>(
    null,
  );
  const [promptResult, setPromptResult] =
    useState<GovernanceMutationResult | null>(null);
  const [profileResult, setProfileResult] =
    useState<GovernanceMutationResult | null>(null);
  const [routingResult, setRoutingResult] =
    useState<GovernanceMutationResult | null>(null);
  const [promptPreview, setPromptPreview] = useState<SafePromptPreview | null>(
    null,
  );
  const [profileResolution, setProfileResolution] =
    useState<ProfileResolutionPreview | null>(null);
  const [probing, setProbing] = useState(false);

  useEffect(() => {
    let alive = true;
    fetchGovernanceDashboard(governanceUrl)
      .then((payload) => {
        if (alive) {
          setDashboard(payload);
          setPromptPreview(payload.prompt_preview);
          setProfileResolution(payload.profile_resolution);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(caught instanceof Error ? caught.message : "Governance unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [governanceUrl]);

  async function probeProvider(url: string) {
    setProbing(true);
    try {
      setProbeResult(await runProviderProbe(url));
    } catch (caught: unknown) {
      setLoadError(caught instanceof Error ? caught.message : "Provider probe failed");
    } finally {
      setProbing(false);
    }
  }

  async function savePrompt(
    url: string,
    prompt: GovernanceDashboard["prompts"][number],
  ) {
    const action = prompt.authorized_actions.find((candidate) =>
      candidate.action_id.startsWith("prompt-save"),
    );
    setPromptResult(
      await savePromptSummary(url, {
        idempotency_key: buildIdempotencyKey("prompt-save"),
        publish: false,
        revision:
          action?.action_metadata?.revision ??
          prompt.draft_version ??
          prompt.published_version ??
          generatedRevisionMarker("prompt-save"),
        safe_summary: "Review safe prompt summary.",
      }),
    );
  }

  async function runPromptPreview(url: string, unsafe: boolean) {
    setPromptPreview(
      await previewPrompt(url, {
        fixture_id: unsafe ? "redaction-check" : "safe-summary",
      }),
    );
  }

  async function saveProfile(
    url: string,
    profile: GovernanceDashboard["profiles"][number],
  ) {
    const action = profile.authorized_actions.find(
      (candidate) => candidate.action_id.startsWith("profile-save"),
    );
    const result = await saveRuntimeProfile(url, {
      idempotency_key: buildIdempotencyKey("profile-save"),
      model_binding: profile.model_binding,
      provider_binding: profile.provider_binding,
      revision:
        action?.action_metadata?.revision ??
        profile.draft_version ??
        generatedRevisionMarker("profile-save"),
    });
    setProfileResult(result);
    if (result.profile_resolution) {
      setProfileResolution(result.profile_resolution);
    }
  }

  async function resolveProfile(url: string) {
    setProfileResolution(await resolveRuntimeProfile(url));
  }

  async function runRoutingPreview() {
    const action = dashboard?.actions.find(
      (candidate) => candidate.action_id === "routing-preview",
    );
    if (!action) {
      return;
    }
    setRoutingResult(
      await previewRouting(action.href, {
        profile_id: dashboard?.profiles[0]?.profile_id ?? null,
        skill_id: dashboard?.profiles[0]?.skill_requirements[0] ?? null,
        workflow_context: `${dashboard?.scope.label ?? "Active scope"} governance preview`,
      }),
    );
  }

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Governance unavailable",
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
          summary: "Loading provider, prompt, profile, routing, and provenance summaries.",
          title: "Loading governance",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="governance-page">
      <section className="patterns-hero governance-hero">
        <p className="eyebrow">Governance</p>
        <h2>{dashboard.title}</h2>
        <p>{dashboard.description}</p>
      </section>
      {dashboard.provenance ? (
        <section className="state-provenance" aria-label="Governance provenance">
          <dl className="compact-dl">
            <div>
              <dt>Source</dt>
              <dd>{dashboard.provenance.source_label}</dd>
            </div>
            {dashboard.provenance.source_detail ? (
              <div>
                <dt>Evidence</dt>
                <dd>{dashboard.provenance.source_detail}</dd>
              </div>
            ) : null}
          </dl>
        </section>
      ) : null}
      {dashboard.empty_state ? (
        <section className="governance-panel" aria-label="Governance empty state">
          <p className="eyebrow">Empty state</p>
          <h2>{dashboard.empty_state.title}</h2>
          <p>{dashboard.empty_state.summary}</p>
          {dashboard.empty_state.setup_hint ? (
            <small>{dashboard.empty_state.setup_hint}</small>
          ) : null}
        </section>
      ) : null}
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <GovernanceSectionNav
        activeSection={activeSection}
        onChange={setActiveSection}
        sections={dashboard.sections}
      />
      <section className="governance-panel setup-panel" aria-label="Setup summary">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Setup</p>
            <h2>Readiness summary</h2>
          </div>
        </div>
        <ul>
          {dashboard.setup_summary.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      <ProviderGovernancePanel
        onProbe={(url) => void probeProvider(url)}
        probeResult={probeResult}
        probing={probing}
        providers={dashboard.providers}
      />
      <PromptGovernancePanel
        mutationResult={promptResult}
        onPreview={(url, unsafe) => void runPromptPreview(url, unsafe)}
        onSave={(url, prompt) => void savePrompt(url, prompt)}
        preview={promptPreview}
        prompts={dashboard.prompts}
      />
      <ProfileGovernancePanel
        mutationResult={profileResult}
        onResolve={(url) => void resolveProfile(url)}
        onSave={(url, profile) => void saveProfile(url, profile)}
        profiles={dashboard.profiles}
        resolution={profileResolution}
      />
      <RoutingPreviewPanel
        lastResult={routingResult}
        onPreview={() => void runRoutingPreview()}
        preview={dashboard.routing_preview}
      />
      <section className="governance-panel" aria-labelledby="legacy-routes-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Migration</p>
            <h2 id="legacy-routes-title">Legacy route redirects</h2>
          </div>
        </div>
        <div className="governance-card-grid">
          {dashboard.legacy_routes.map((route) => (
            <article className="governance-card" key={route.legacy_path}>
              <div>
                <h3>{route.legacy_path}</h3>
                <small>{route.compatibility_status}</small>
              </div>
              <p>{route.react_path}</p>
              <p className="safe-note">{route.authorization_behavior}</p>
              <small>{route.evidence_summary}</small>
            </article>
          ))}
        </div>
      </section>
      <div className="governance-review-grid">
        <PolicyHistoryPanel history={dashboard.policy_history} />
        <ProvenancePanel provenance={dashboard.run_provenance} />
      </div>
    </div>
  );
}
