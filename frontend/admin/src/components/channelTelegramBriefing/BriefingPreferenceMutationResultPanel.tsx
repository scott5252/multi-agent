import type { BriefingPreferenceMutationResult } from "../../api/generated/reactAdminApi";

export function BriefingPreferenceMutationResultPanel({
  result,
}: {
  result: BriefingPreferenceMutationResult | null;
}) {
  if (!result) {
    return null;
  }
  return (
    <div className={`mutation-note mutation-note--${result.status}`}>
      <strong>{result.profile_summary}</strong>
      {result.artifact_reference ? <span>{result.artifact_reference}</span> : null}
      <small>{result.audit_reference}</small>
    </div>
  );
}
