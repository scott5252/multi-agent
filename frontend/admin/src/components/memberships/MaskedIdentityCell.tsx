import type { UserDirectoryEntry } from "../../api/generated/reactAdminApi";

interface MaskedIdentityCellProps {
  entry: UserDirectoryEntry;
  onOpenDetail: (entry: UserDirectoryEntry) => void;
}

export function MaskedIdentityCell({ entry, onOpenDetail }: MaskedIdentityCellProps) {
  return (
    <div className="masked-identity">
      <strong>{entry.display_name}</strong>
      <span>{entry.masked_email}</span>
      <small>{entry.safe_subject_suffix}</small>
      {entry.raw_identifier_detail?.authorized ? (
        <button className="ghost-button compact-button" onClick={() => onOpenDetail(entry)} type="button">
          Details
        </button>
      ) : null}
    </div>
  );
}
