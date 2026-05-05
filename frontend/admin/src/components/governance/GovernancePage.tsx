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

  async function savePrompt(url: string) {
    setPromptResult(
      await savePromptSummary(url, {
        idempotency_key: "prompt-save-ui-qa031",
        publish: false,
        revision: "prompt-rev-qa031-current",
        safe_summary: "Review fixture-safe prompt summary.",
      }),
    );
  }

  async function runPromptPreview(url: string, unsafe: boolean) {
    setPromptPreview(
      await previewPrompt(url, {
        fixture_id: unsafe ? "qa031-unsafe-preview" : "qa031-safe-preview",
      }),
    );
  }

  async function saveProfile(
    url: string,
    profile: GovernanceDashboard["profiles"][number],
  ) {
    const result = await saveRuntimeProfile(url, {
      idempotency_key: "profile-save-ui-qa031",
      model_binding: profile.model_binding,
      provider_binding: profile.provider_binding,
      revision: "profile-rev-qa031-current",
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
        profile_id: "briefing-runtime",
        skill_id: "weather-readonly",
        workflow_context: "Daily briefing workflow",
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

  if (!dashboard || !promptPreview || !profileResolution) {
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
        onSave={(url) => void savePrompt(url)}
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
      <div className="governance-review-grid">
        <PolicyHistoryPanel history={dashboard.policy_history} />
        <ProvenancePanel provenance={dashboard.run_provenance} />
      </div>
    </div>
  );
}
