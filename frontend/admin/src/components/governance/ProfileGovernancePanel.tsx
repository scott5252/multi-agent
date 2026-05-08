import { Route, Save } from "lucide-react";

import type {
  GovernanceMutationResult,
  ProfileResolutionPreview,
  RuntimeProfileGovernanceSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import { ProfileResolutionPanel } from "./ProfileResolutionPanel";

interface ProfileGovernancePanelProps {
  mutationResult: GovernanceMutationResult | null;
  onResolve: (resolveUrl: string) => void;
  onSave: (saveUrl: string, profile: RuntimeProfileGovernanceSummary) => void;
  profiles: RuntimeProfileGovernanceSummary[];
  resolution: ProfileResolutionPreview | null;
}

export function ProfileGovernancePanel({
  mutationResult,
  onResolve,
  onSave,
  profiles,
  resolution,
}: ProfileGovernancePanelProps) {
  return (
    <section className="governance-panel" aria-labelledby="profiles-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Profiles</p>
          <h2 id="profiles-title">Runtime configuration</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {profiles.length === 0 ? (
          <article className="governance-card">
            <strong>No runtime profiles found</strong>
            <p>No authorized live runtime profile records exist for this scope.</p>
          </article>
        ) : null}
        {profiles.map((profile) => {
          const saveAction = profile.authorized_actions.find(
            (action) => action.action_id.startsWith("profile-save"),
          );
          const resolveAction = profile.authorized_actions.find(
            (action) => action.action_id.startsWith("profile-resolve"),
          );
          return (
            <article className="governance-card" key={profile.profile_id}>
              <div className="card-heading">
                <strong>{profile.name}</strong>
                <Badge tone="success">{profile.resolver_status}</Badge>
              </div>
              <p>{profile.model_binding}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Provider</dt>
                  <dd>{profile.provider_binding}</dd>
                </div>
                <div>
                  <dt>Prompt</dt>
                  <dd>{profile.prompt_binding}</dd>
                </div>
                <div>
                  <dt>Published</dt>
                  <dd>{profile.published_version}</dd>
                </div>
              </dl>
              <div className="chip-row">
                {profile.skill_requirements.map((skill) => (
                  <span className="filter-chip" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
              <div className="action-row">
                {saveAction ? (
                  <Button
                    onClick={() => onSave(saveAction.href, profile)}
                    type="button"
                  >
                    <Save aria-hidden="true" size={16} />
                    Save profile
                  </Button>
                ) : null}
                {resolveAction ? (
                  <Button
                    onClick={() => onResolve(resolveAction.href)}
                    type="button"
                  >
                    <Route aria-hidden="true" size={16} />
                    Resolve
                  </Button>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
      {resolution ? (
        <ProfileResolutionPanel resolution={resolution} />
      ) : (
        <section className="resolution-panel" aria-label="Profile resolution preview">
          <strong>Profile resolution unavailable</strong>
          <p>No active runtime profile version is available for this scope.</p>
        </section>
      )}
      {mutationResult ? (
        <section className="mutation-result accepted">
          <p className="eyebrow">Profile result</p>
          <h2>{mutationResult.status}</h2>
          <p>{mutationResult.summary}</p>
        </section>
      ) : null}
    </section>
  );
}
