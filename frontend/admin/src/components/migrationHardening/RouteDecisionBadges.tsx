import type {
  MigrationEvidenceStatus,
  MigrationOverallStatus,
  MigrationProblemSeverity,
  MigrationRouteDecision,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

type BadgeTone = "neutral" | "info" | "success" | "warning" | "critical";

const decisionLabels: Record<MigrationRouteDecision, string> = {
  alias: "Alias",
  blocked: "Blocked",
  react_primary: "React primary",
  redirect: "Redirect",
  retained_fallback: "Retained fallback",
  retirement_candidate: "Retirement candidate",
};

export function RouteDecisionBadge({
  decision,
}: {
  decision: MigrationRouteDecision;
}) {
  return <Badge tone={decisionTone(decision)}>{decisionLabels[decision]}</Badge>;
}

export function StatusBadge({
  label,
  status,
}: {
  label?: string;
  status: MigrationEvidenceStatus | MigrationOverallStatus | MigrationProblemSeverity;
}) {
  return <Badge tone={statusTone(status)}>{label ?? status.replaceAll("_", " ")}</Badge>;
}

function decisionTone(decision: MigrationRouteDecision): BadgeTone {
  if (decision === "blocked") {
    return "critical";
  }
  if (decision === "retained_fallback" || decision === "retirement_candidate") {
    return "warning";
  }
  if (decision === "react_primary" || decision === "redirect" || decision === "alias") {
    return "success";
  }
  return "neutral";
}

function statusTone(
  status: MigrationEvidenceStatus | MigrationOverallStatus | MigrationProblemSeverity,
): BadgeTone {
  if (status === "fail" || status === "blocked" || status === "blocking") {
    return "critical";
  }
  if (
    status === "warning" ||
    status === "partial" ||
    status === "rollback" ||
    status === "info"
  ) {
    return "warning";
  }
  if (status === "pass" || status === "ready") {
    return "success";
  }
  return "neutral";
}
