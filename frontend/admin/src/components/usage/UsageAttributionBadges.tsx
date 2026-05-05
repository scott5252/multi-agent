import type { UsageReactEventRow, UsageReactRollupRow } from "../../api/generated/reactAdminApi";

interface UsageAttributionBadgesProps {
  row?: UsageReactRollupRow;
  event?: UsageReactEventRow;
}

export function UsageAttributionBadges({ row, event }: UsageAttributionBadgesProps) {
  const badges = [
    row?.attempt_summary ?? event?.gateway_operation_label,
    event?.physical_attempt_label,
    row?.tool_summary ?? event?.tool_label,
    event?.graph_node_label,
  ].filter((value): value is string => Boolean(value));

  if (!badges.length) {
    return <span className="usage-muted">Standard attribution</span>;
  }

  return (
    <span className="usage-badge-row">
      {badges.slice(0, 3).map((badge) => (
        <span className="usage-badge" key={badge}>
          {badge}
        </span>
      ))}
    </span>
  );
}
