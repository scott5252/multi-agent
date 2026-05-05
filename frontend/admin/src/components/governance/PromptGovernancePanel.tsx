import { Eye, Save } from "lucide-react";

import type {
  GovernanceMutationResult,
  PromptLibrarySummary,
  SafePromptPreview,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import { SafePromptPreviewPanel } from "./SafePromptPreviewPanel";

interface PromptGovernancePanelProps {
  mutationResult: GovernanceMutationResult | null;
  onPreview: (previewUrl: string, unsafe: boolean) => void;
  onSave: (saveUrl: string) => void;
  preview: SafePromptPreview;
  prompts: PromptLibrarySummary[];
}

export function PromptGovernancePanel({
  mutationResult,
  onPreview,
  onSave,
  preview,
  prompts,
}: PromptGovernancePanelProps) {
  return (
    <section className="governance-panel" aria-labelledby="prompts-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Prompts</p>
          <h2 id="prompts-title">Versions and safe previews</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {prompts.map((prompt) => {
          const previewAction = prompt.authorized_actions.find(
            (action) => action.action_id === "prompt-preview",
          );
          const saveAction = prompt.authorized_actions.find(
            (action) => action.action_id === "prompt-save",
          );
          return (
            <article className="governance-card" key={prompt.prompt_lineage_id}>
              <div className="card-heading">
                <strong>{prompt.name}</strong>
                <Badge tone="success">{prompt.status}</Badge>
              </div>
              <p>{prompt.safe_change_summary}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Published</dt>
                  <dd>{prompt.published_version ?? "none"}</dd>
                </div>
                <div>
                  <dt>Draft</dt>
                  <dd>{prompt.draft_version ?? "none"}</dd>
                </div>
                <div>
                  <dt>Render tests</dt>
                  <dd>{prompt.render_test_status}</dd>
                </div>
              </dl>
              <div className="history-list">
                {prompt.history.map((version) => (
                  <small key={version.version_id}>
                    {version.label}: {version.safe_change_summary}
                  </small>
                ))}
              </div>
              <div className="action-row">
                {saveAction ? (
                  <Button onClick={() => onSave(saveAction.href)} type="button">
                    <Save aria-hidden="true" size={16} />
                    Save summary
                  </Button>
                ) : null}
                {previewAction ? (
                  <>
                    <Button
                      onClick={() => onPreview(previewAction.href, false)}
                      type="button"
                    >
                      <Eye aria-hidden="true" size={16} />
                      Preview safe
                    </Button>
                    <Button
                      onClick={() => onPreview(previewAction.href, true)}
                      type="button"
                      variant="secondary"
                    >
                      <Eye aria-hidden="true" size={16} />
                      Preview unsafe fixture
                    </Button>
                  </>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
      <SafePromptPreviewPanel preview={preview} />
      {mutationResult ? (
        <section className="mutation-result accepted">
          <p className="eyebrow">Prompt result</p>
          <h2>{mutationResult.status}</h2>
          <p>{mutationResult.summary}</p>
        </section>
      ) : null}
    </section>
  );
}
