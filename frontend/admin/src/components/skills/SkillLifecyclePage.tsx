import { useEffect, useState } from "react";

import {
  configureSkillCredential,
  fetchSkillLifecycleDashboard,
  installTenantSkill,
  previewSkillBinding,
  publishSkillCandidate,
  refreshSkillReadiness,
  runSkillDiagnostic,
  saveSkillCandidate,
  updateSkillPackageLifecycle,
  updateSkillTenantGrant,
  validateSkillCandidate,
} from "../../api/client";
import type {
  SkillLifecycleDashboard,
  SkillLifecycleMutationResult,
  TenantSkillGrantSummary,
  TenantSkillInstallationSummary,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { BindingAndDiagnosticsPanel } from "./BindingAndDiagnosticsPanel";
import { ConnectorReadinessPanel } from "./ConnectorReadinessPanel";
import { CredentialReadinessPanel } from "./CredentialReadinessPanel";
import { PackageLifecyclePanel } from "./PackageLifecyclePanel";
import { PackagePublicationPanel } from "./PackagePublicationPanel";
import { SkillLifecycleAuditPanel } from "./SkillLifecycleAuditPanel";
import { SkillLifecycleSectionNav } from "./SkillLifecycleSectionNav";
import { SmokeTestPanel } from "./SmokeTestPanel";
import { TenantSkillLifecyclePanel } from "./TenantSkillLifecyclePanel";

export function SkillLifecyclePage({ skillsUrl }: { skillsUrl: string }) {
  const [dashboard, setDashboard] = useState<SkillLifecycleDashboard | null>(null);
  const [activeSection, setActiveSection] = useState("publish");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [candidateResult, setCandidateResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [validationResult, setValidationResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [publishResult, setPublishResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [grantResult, setGrantResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [installResult, setInstallResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [credentialResult, setCredentialResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [readinessResult, setReadinessResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [diagnosticResult, setDiagnosticResult] =
    useState<SkillLifecycleMutationResult | null>(null);
  const [bindingResult, setBindingResult] =
    useState<SkillLifecycleMutationResult | null>(null);

  useEffect(() => {
    let alive = true;
    fetchSkillLifecycleDashboard(skillsUrl)
      .then((payload) => {
        if (alive) {
          setDashboard(payload);
          setActiveSection(payload.sections[0]?.section_id ?? "discover");
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Skill lifecycle unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [skillsUrl]);

  async function saveCandidate(url: string) {
    setCandidateResult(
      await saveSkillCandidate(url, {
        candidate_revision: null,
        idempotency_key: "candidate-save-ui-qa032",
        manifest_text: "Safe pasted fixture summary.",
        uploaded_fixture_id: "qa032-uploaded-manifest",
      }),
    );
  }

  async function validateCandidate(url: string, ready: boolean) {
    setValidationResult(await validateSkillCandidate(url, ready));
  }

  async function publishCandidate(url: string) {
    setPublishResult(
      await publishSkillCandidate(url, {
        candidate_revision: "candidate-rev-qa032-current",
        confirmed: true,
        idempotency_key: "candidate-publish-ui-qa032",
      }),
    );
  }

  async function updateGrant(url: string, grant: TenantSkillGrantSummary) {
    setGrantResult(
      await updateSkillTenantGrant(url, {
        grant_enabled: true,
        idempotency_key: "grant-ui-qa032",
        revision: "grant-rev-qa032-current",
        tenant_id: grant.tenant_id,
        version_id: "package-version-daily-briefing-1-4-0",
      }),
    );
  }

  async function updateLifecycle(url: string) {
    setGrantResult(await updateSkillPackageLifecycle(url));
  }

  async function installSkill(url: string, installation: TenantSkillInstallationSummary) {
    setInstallResult(
      await installTenantSkill(url, {
        idempotency_key: "install-ui-qa032",
        package_id: "package-daily-briefing-connectors",
        revision: installation.installation_revision,
        upgrade: false,
        version_id: "package-version-daily-briefing-1-4-0",
      }),
    );
  }

  async function configureCredential(
    url: string,
    installation: TenantSkillInstallationSummary,
    referenceId: string,
  ) {
    setCredentialResult(
      await configureSkillCredential(url, {
        idempotency_key: "credential-ui-qa032",
        revision: installation.installation_revision,
        selected_reference_id: referenceId,
      }),
    );
  }

  async function refreshReadiness(
    url: string,
    installation: TenantSkillInstallationSummary,
  ) {
    setReadinessResult(
      await refreshSkillReadiness(url, {
        idempotency_key: "readiness-ui-qa032",
        revision: installation.installation_revision,
      }),
    );
  }

  async function runDiagnostic(url?: string) {
    const action =
      dashboard?.actions.find((candidate) => candidate.action_id === "diagnostics-refresh")
      ?? null;
    setDiagnosticResult(await runSkillDiagnostic(url ?? action?.href ?? "/admin/app/skills/diagnostics/run"));
  }

  async function previewBinding() {
    const action = dashboard?.actions.find(
      (candidate) => candidate.action_id === "binding-preview",
    );
    if (!action) {
      return;
    }
    setBindingResult(
      await previewSkillBinding(action.href, {
        package_id: "package-daily-briefing-connectors",
        profile_id: "profile-briefing-runtime",
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
          title: "Skill lifecycle unavailable",
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
          summary: "Loading package, installation, readiness, binding, and audit summaries.",
          title: "Loading skill lifecycle",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="governance-page skill-lifecycle-page">
      <section className="patterns-hero governance-hero skill-hero">
        <p className="eyebrow">Skills</p>
        <h2>{dashboard.title}</h2>
        <p>{dashboard.description}</p>
      </section>
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <SkillLifecycleSectionNav
        activeSection={activeSection}
        onChange={setActiveSection}
        sections={dashboard.sections}
      />
      <section className="governance-panel setup-panel" aria-label="Skill setup summary">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Setup</p>
            <h2>Lifecycle readiness</h2>
          </div>
        </div>
        <ul>
          {dashboard.setup_summary.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      {dashboard.platform_publication ? (
        <>
          <PackagePublicationPanel
            candidateResult={candidateResult}
            onPublish={(url) => void publishCandidate(url)}
            onSaveCandidate={(url) => void saveCandidate(url)}
            onValidate={(url, ready) => void validateCandidate(url, ready)}
            publication={dashboard.platform_publication}
            publishResult={publishResult}
            validationResult={validationResult}
          />
          <PackageLifecyclePanel
            grantResult={grantResult}
            onLifecycleAction={(url) => void updateLifecycle(url)}
            onUpdateGrant={(url, grant) => void updateGrant(url, grant)}
            versions={dashboard.platform_publication.package_versions}
          />
        </>
      ) : null}
      <TenantSkillLifecyclePanel
        discovery={dashboard.tenant_discovery}
        installResult={installResult}
        installations={dashboard.installations}
        onInstall={(url, installation) => void installSkill(url, installation)}
      />
      <CredentialReadinessPanel
        credentialResult={credentialResult}
        installations={dashboard.installations}
        onConfigure={(url, installation, referenceId) =>
          void configureCredential(url, installation, referenceId)
        }
      />
      <SmokeTestPanel
        installations={dashboard.installations}
        onRefresh={(url, installation) => void refreshReadiness(url, installation)}
        readinessResult={readinessResult}
      />
      <ConnectorReadinessPanel
        connectors={dashboard.connector_diagnostics}
        diagnosticResult={diagnosticResult}
        onDiagnostic={(url) => void runDiagnostic(url)}
      />
      <BindingAndDiagnosticsPanel
        bindingResult={bindingResult}
        diagnostics={dashboard.skill_execution_diagnostics}
        onDiagnostic={() => void runDiagnostic()}
        onPreview={() => void previewBinding()}
        preview={dashboard.binding_preview}
      />
      <SkillLifecycleAuditPanel auditTimeline={dashboard.audit_timeline} />
    </div>
  );
}
