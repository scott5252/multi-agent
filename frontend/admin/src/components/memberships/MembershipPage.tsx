import { useEffect, useState } from "react";

import {
  fetchMembershipDashboard,
  linkMembershipPrincipal,
  revokeMembershipRoleGrant,
  saveMembershipInvitation,
  saveMembershipRoleGrant,
  updateMembershipPrincipalStatus,
  updateTenantMembershipStatus,
} from "../../api/client";
import type {
  MembershipDashboard,
  MembershipMutationResult,
  UserDirectoryEntry,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { AccessHistoryPanel } from "./AccessHistoryPanel";
import { InvitationPanel } from "./InvitationPanel";
import { MembershipAuditPanel } from "./MembershipAuditPanel";
import { MembershipOverviewPanel } from "./MembershipOverviewPanel";
import { MembershipSectionNav } from "./MembershipSectionNav";
import { PrincipalLinkPanel } from "./PrincipalLinkPanel";
import { RawIdentifierDetailPanel } from "./RawIdentifierDetailPanel";
import { RoleGrantPanel } from "./RoleGrantPanel";
import { StatusActionsPanel } from "./StatusActionsPanel";
import { UserDirectoryPanel } from "./UserDirectoryPanel";

export function MembershipPage({ membershipsUrl }: { membershipsUrl: string }) {
  const [dashboard, setDashboard] = useState<MembershipDashboard | null>(null);
  const [activeSection, setActiveSection] = useState("overview");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [inviteResult, setInviteResult] =
    useState<MembershipMutationResult | null>(null);
  const [linkResult, setLinkResult] =
    useState<MembershipMutationResult | null>(null);
  const [roleResult, setRoleResult] =
    useState<MembershipMutationResult | null>(null);
  const [statusResult, setStatusResult] =
    useState<MembershipMutationResult | null>(null);
  const [rawDetailEntry, setRawDetailEntry] = useState<UserDirectoryEntry | null>(
    null,
  );

  useEffect(() => {
    let alive = true;
    fetchMembershipDashboard(membershipsUrl)
      .then((payload) => {
        if (alive) {
          setDashboard(payload);
          setActiveSection(payload.sections[0]?.section_id ?? "overview");
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Memberships unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [membershipsUrl]);

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Memberships unavailable",
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
          summary: "Loading directory, invitations, roles, history, and audit evidence.",
          title: "Loading memberships",
          trace_id: null,
        }}
      />
    );
  }

  async function submitInvitation(
    url: string,
    payload: Parameters<typeof saveMembershipInvitation>[1],
  ) {
    setInviteResult(await saveMembershipInvitation(withSearch(url), payload));
  }

  async function submitPrincipalLink(
    url: string,
    payload: Parameters<typeof linkMembershipPrincipal>[1],
  ) {
    setLinkResult(await linkMembershipPrincipal(withSearch(url), payload));
  }

  async function submitRoleGrant(
    url: string,
    payload: Parameters<typeof saveMembershipRoleGrant>[1],
  ) {
    setRoleResult(await saveMembershipRoleGrant(withSearch(url), payload));
  }

  async function submitGrantRevoke(url: string) {
    setRoleResult(
      await revokeMembershipRoleGrant(withSearch(url), {
        confirmed: true,
        idempotency_key: "role-revoke-ui-qa034",
        reason: "Admin review",
        revision: "membership-rev-qa034-current",
      }),
    );
  }

  async function submitPrincipalStatus(url: string) {
    setStatusResult(
      await updateMembershipPrincipalStatus(withSearch(url), {
        confirmed: true,
        idempotency_key: "principal-status-ui-qa034",
        reason: "Admin review",
        revision: "membership-rev-qa034-current",
      }),
    );
  }

  async function submitMembershipStatus(url: string) {
    setStatusResult(
      await updateTenantMembershipStatus(withSearch(url), {
        confirmed: true,
        idempotency_key: "membership-status-ui-qa034",
        reason: "Admin review",
        revision: "membership-rev-qa034-current",
      }),
    );
  }

  return (
    <div className="governance-page membership-page">
      <section className="patterns-hero governance-hero membership-hero">
        <p className="eyebrow">Memberships</p>
        <h2>{dashboard.title}</h2>
        <p>{dashboard.description}</p>
      </section>
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <MembershipSectionNav
        activeSection={activeSection}
        onChange={setActiveSection}
        sections={dashboard.sections}
      />
      <MembershipOverviewPanel
        cards={dashboard.summary_cards}
        scope={dashboard.scope}
        scopes={dashboard.allowed_scope_options}
      />
      <UserDirectoryPanel
        directory={dashboard.directory}
        filters={dashboard.filters}
        onOpenDetail={setRawDetailEntry}
      />
      <RawIdentifierDetailPanel
        entry={rawDetailEntry}
        onClose={() => setRawDetailEntry(null)}
      />
      <InvitationPanel
        form={dashboard.invite_form}
        invitations={dashboard.invitations}
        mutationResult={inviteResult}
        onInvite={(url, payload) => void submitInvitation(url, payload)}
      />
      <PrincipalLinkPanel
        mutationResult={linkResult}
        onLink={(url, payload) => void submitPrincipalLink(url, payload)}
      />
      <RoleGrantPanel
        directory={dashboard.directory}
        form={dashboard.role_grant_form}
        grants={dashboard.role_grants}
        mutationResult={roleResult}
        onGrant={(url, payload) => void submitRoleGrant(url, payload)}
        onRevoke={(url) => void submitGrantRevoke(url)}
      />
      <StatusActionsPanel
        directory={dashboard.directory}
        membershipStatuses={dashboard.status_actions}
        mutationResult={statusResult}
        onMembershipStatus={(url) => void submitMembershipStatus(url)}
        onPrincipalStatus={(url) => void submitPrincipalStatus(url)}
      />
      <AccessHistoryPanel records={dashboard.access_history} />
      <MembershipAuditPanel records={dashboard.audit_timeline} />
    </div>
  );
}

function withSearch(url: string): string {
  if (!window.location.search || url.includes("?")) {
    return url;
  }
  return `${url}${window.location.search}`;
}
