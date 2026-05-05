import type {
  ChannelMutationResult,
  TelegramAliasRecord,
} from "../../api/generated/reactAdminApi";

export function AliasManagementPanel({
  aliases,
  result,
  onCreate,
  onAction,
}: {
  aliases: TelegramAliasRecord[];
  result: ChannelMutationResult | null;
  onCreate: () => void;
  onAction: (alias: TelegramAliasRecord, action: string) => void;
}) {
  return (
    <section aria-labelledby="alias-management-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="alias-management-heading">Aliases</h2>
        <button type="button" onClick={onCreate}>
          Create Alias
        </button>
      </div>
      <div className="channel-table">
        {aliases.map((alias) => (
          <article className="channel-row" key={alias.alias_id}>
            <div>
              <strong>{alias.alias_text}</strong>
              <span>{alias.target_summary}</span>
            </div>
            <div>
              <span>{alias.protected_readiness}</span>
              <span>{alias.status}</span>
            </div>
            <div>
              <span>{alias.revision}</span>
              <span>{alias.audit_reference}</span>
            </div>
            <div className="button-row button-row--inline">
              {alias.actions.map((action) => (
                <button
                  key={action.action_id}
                  type="button"
                  onClick={() => onAction(alias, action.action_id)}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
      {result ? <p className="mutation-note">{result.summary}</p> : null}
    </section>
  );
}
