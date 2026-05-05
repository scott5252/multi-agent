import type { UserDirectoryEntry } from "../../api/generated/reactAdminApi";

export function RawIdentifierDetailPanel({
  entry,
  onClose,
}: {
  entry: UserDirectoryEntry | null;
  onClose: () => void;
}) {
  if (!entry?.raw_identifier_detail?.authorized) {
    return null;
  }
  const detail = entry.raw_identifier_detail;
  return (
    <section className="governance-panel membership-panel raw-detail-panel" aria-label="Authorized identifier detail">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Authorized detail</p>
          <h2>{entry.display_name}</h2>
        </div>
        <button className="ghost-button compact-button" onClick={onClose} type="button">
          Close
        </button>
      </div>
      <dl className="compact-dl">
        <div>
          <dt>{detail.copy_label}</dt>
          <dd>{detail.principal_identity_id}</dd>
        </div>
        <div>
          <dt>Subject suffix</dt>
          <dd>{detail.external_subject}</dd>
        </div>
        <div>
          <dt>Reason</dt>
          <dd>{detail.reason}</dd>
        </div>
      </dl>
    </section>
  );
}
