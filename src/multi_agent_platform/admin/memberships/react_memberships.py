from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.api.schemas.admin_membership_react import (
    AccessHistoryRecord,
    InvitationFormMetadata,
    InvitationSummary,
    MembershipAccessHistoryList,
    MembershipAuditList,
    MembershipAuditRecord,
    MembershipConfirmationRequest,
    MembershipDashboard,
    MembershipDirectoryFilters,
    MembershipFilterOption,
    MembershipInvitationSaveRequest,
    MembershipLifecycleStatus,
    MembershipMutationResult,
    MembershipScopeType,
    MembershipSection,
    MembershipStatusSummary,
    MembershipSummaryCard,
    PrincipalLinkRequest,
    PrincipalLinkSummary,
    RawIdentifierDetail,
    RoleChoice,
    RoleGrantFormMetadata,
    RoleGrantSaveRequest,
    RoleGrantSummary,
    TenantMembershipSummary,
    UserDirectoryEntry,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    ConfirmationRequirement,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
    ReactAdminShellState,
    ReactAdminShellStateKind,
)
from multi_agent_platform.auth.principal import PrincipalContext

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
ACME_LABEL = "Acme"
GLOBEX_LABEL = "Globex"
CURRENT_REVISION = "membership-rev-qa034-current"
STALE_REVISION = "membership-rev-qa034-stale"


@dataclass(frozen=True, slots=True)
class MembershipActor:
    platform_admin: bool
    tenant_admin: bool
    active_tenant_id: str | None
    active_tenant_label: str | None


def build_membership_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
    query: str | None = None,
) -> MembershipDashboard:
    actor = _actor(scope=scope, principal=principal)
    directory = _directory_entries(actor)
    filtered_directory = _filter_directory(directory, query)
    invitations = _invitations(actor)
    role_grants = tuple(
        grant for entry in filtered_directory for grant in entry.role_summaries
    )
    status_actions = tuple(
        membership
        for entry in filtered_directory
        for membership in _status_summaries(entry)
    )
    access_history = _access_history(actor)
    audit_timeline = _audit_timeline(actor)
    return MembershipDashboard(
        page_id="qa034-membership-administration",
        title="Membership Administration",
        description=(
            "Manage users, invitations, roles, status, and access evidence "
            "with backend-owned safeguards."
        ),
        scope=scope,
        summary_cards=(
            MembershipSummaryCard(
                card_id="directory",
                label="Directory",
                value=str(len(filtered_directory)),
                status=MembershipLifecycleStatus.READY,
                summary="Safe user rows are scoped to the active administrator.",
            ),
            MembershipSummaryCard(
                card_id="invites",
                label="Invitations",
                value=str(len(invitations)),
                status=MembershipLifecycleStatus.PENDING,
                summary="Replayed invitations return original audit evidence.",
            ),
            MembershipSummaryCard(
                card_id="history",
                label="Access history",
                value=str(len(access_history)),
                status=MembershipLifecycleStatus.PARTIAL,
                summary="Recent allow and deny records are bounded.",
            ),
        ),
        sections=(
            _section("overview", "Overview", "Scope and readiness summary"),
            _section("directory", "Directory", "Users and membership status"),
            _section("invitations", "Invitations", "Create or replay invites"),
            _section("roles", "Role grants", "Assign and revoke roles"),
            _section("status", "Status", "Suspend, reactivate, or remove"),
            _section("history", "Access history", "Recent decisions"),
            _section("audit", "Audit", "Safe audit records"),
        ),
        directory=filtered_directory,
        filters=_filters(actor, query=query),
        allowed_scope_options=allowed_scope_options or _default_scope_options(actor),
        invite_form=_invite_form(actor),
        role_grant_form=_role_form(actor),
        invitations=invitations,
        role_grants=role_grants,
        status_actions=status_actions,
        access_history=access_history,
        audit_timeline=audit_timeline,
        common_states=_common_states(actor),
    )


def build_invitation_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: MembershipInvitationSaveRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    requested_roles = set(request.requested_roles or ("tenant_user",))
    target_tenant = request.tenant_id or actor.active_tenant_id
    if not _tenant_allowed(actor, target_tenant):
        return _denied_result(
            audit_reference_id="audit-membership-qa034-cross-tenant-denied",
            summary="Invitation scope was denied.",
            field="tenant_id",
            message="The selected tenant is not available for this administrator.",
        )
    if not actor.platform_admin and any(
        role.startswith("platform") for role in requested_roles
    ):
        return _denied_result(
            audit_reference_id="audit-membership-qa034-platform-role-denied",
            summary="Invitation role request was denied.",
            field="requested_roles",
            message="Tenant administrators can assign permitted tenant roles only.",
        )
    replayed = request.idempotency_key.endswith("replay") or "replay" in str(
        request.email
    )
    invitation = _invitation_summary(
        invitation_id="invite-qa034-acme-active",
        tenant_id=target_tenant,
        tenant_label=_tenant_label(target_tenant),
        replayed=replayed,
        requested_roles=tuple(sorted(requested_roles)),
    )
    return MembershipMutationResult(
        status=(
            AdminMutationStatus.REPLAYED if replayed else AdminMutationStatus.ACCEPTED
        ),
        summary=(
            "Invitation replayed with original audit evidence."
            if replayed
            else "Invitation created with safe delivery evidence."
        ),
        toast=_toast(
            title="Invitation ready",
            summary="The invitation is visible with masked identity details.",
        ),
        invitation=invitation,
        audit_reference_id=invitation.audit_reference_id,
        idempotency_replay=replayed,
        next_request_effect=(
            "Requested tenant roles apply after the user's next protected request."
        ),
    )


def build_principal_link_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: PrincipalLinkRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.platform_admin:
        return _denied_result(
            audit_reference_id="audit-membership-qa034-principal-link-denied",
            summary="Principal link was denied.",
            field="external_subject",
            message="Platform authority is required to link external identities.",
        )
    if "existing" in request.external_subject and not request.overwrite_confirmed:
        return MembershipMutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Principal link requires overwrite confirmation.",
            confirmation=ConfirmationRequirement(
                title="Confirm principal link",
                summary=(
                    "The subject suffix is already associated with a safe "
                    "identity summary."
                ),
                confirm_label="Confirm link",
            ),
            principal_link=_principal_link_summary(
                display_name=request.display_name,
                status=MembershipLifecycleStatus.STALE,
                conflict_summary="Existing identity summary requires review.",
            ),
            audit_reference_id="audit-membership-qa034-principal-link-confirm",
            next_request_effect=(
                "Linked identity changes apply on the next protected request."
            ),
        )
    link = _principal_link_summary(
        display_name=request.display_name,
        status=MembershipLifecycleStatus.ACTIVE,
        conflict_summary=None,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Principal identity linked with safe subject evidence.",
        toast=_toast(
            title="Principal linked",
            summary="The new identity is available in the directory.",
        ),
        principal_link=link,
        audit_reference_id=link.audit_reference_id,
        next_request_effect=(
            "Linked identity changes apply on the next protected request."
        ),
    )


def build_role_grant_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: RoleGrantSaveRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not request.confirmed:
        return MembershipMutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Role grant requires confirmation.",
            confirmation=ConfirmationRequirement(
                title="Confirm role grant",
                summary=(
                    "The selected role changes access after the next protected request."
                ),
                confirm_label="Grant role",
            ),
            audit_reference_id="audit-membership-qa034-role-confirm",
            next_request_effect="Role changes apply after the next protected request.",
        )
    if not _role_allowed(
        actor, request.scope_type.value, request.tenant_id, request.role_code
    ):
        return _denied_result(
            audit_reference_id="audit-membership-qa034-role-denied",
            summary="Role grant was denied.",
            field="role_code",
            message="The selected role is outside the permitted scope.",
        )
    grant = _role_grant(
        role_grant_id="grant-qa034-new",
        principal_id=request.principal_identity_id,
        principal_label="Maya Chen",
        scope_type=request.scope_type.value,
        tenant_id=request.tenant_id,
        tenant_label=_tenant_label(request.tenant_id),
        role_code=request.role_code,
        status=MembershipLifecycleStatus.ACTIVE,
        audit_reference_id="audit-membership-qa034-role-granted",
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Role grant saved with backend eligibility evidence.",
        toast=_toast(
            title="Role grant saved",
            summary="The changed role set is reflected on the next protected request.",
        ),
        role_grant=grant,
        audit_reference_id=grant.audit_reference_id,
        next_request_effect=grant.next_request_effect,
    )


def build_grant_revoke_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    role_grant_id: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not request.confirmed:
        return _confirmation_result(
            title="Confirm grant revoke",
            summary=(
                "Revoking the grant changes access after the next protected request."
            ),
            label="Revoke grant",
            audit_reference_id="audit-membership-qa034-revoke-confirm",
        )
    if not actor.platform_admin and "globex" in role_grant_id:
        return _denied_result(
            audit_reference_id="audit-membership-qa034-revoke-denied",
            summary="Grant revoke was denied.",
            field="role_grant_id",
            message="The selected grant is not available in this tenant scope.",
        )
    grant = _role_grant(
        role_grant_id=role_grant_id,
        principal_id="principal-qa034-maya",
        principal_label="Maya Chen",
        scope_type="tenant",
        tenant_id=actor.active_tenant_id or ACME_TENANT_ID,
        tenant_label=actor.active_tenant_label or ACME_LABEL,
        role_code="tenant_admin",
        status=MembershipLifecycleStatus.REVOKED,
        audit_reference_id="audit-membership-qa034-role-revoked",
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Role grant revoked with safe audit evidence.",
        toast=_toast(title="Grant revoked", summary="The role is no longer active."),
        role_grant=grant,
        audit_reference_id=grant.audit_reference_id,
        next_request_effect=grant.next_request_effect,
    )


def build_principal_status_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    principal_identity_id: str,
    status_action: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.platform_admin:
        return _denied_result(
            audit_reference_id="audit-membership-qa034-principal-status-denied",
            summary="Principal status change was denied.",
            field="principal_identity_id",
            message="Platform authority is required for principal status changes.",
        )
    if request.revision == STALE_REVISION:
        return _stale_result()
    if not request.confirmed:
        return _confirmation_result(
            title=f"Confirm {status_action}",
            summary="Principal status changes affect future protected requests.",
            label=status_action.title(),
            audit_reference_id="audit-membership-qa034-principal-status-confirm",
        )
    status = (
        MembershipLifecycleStatus.SUSPENDED
        if status_action == "suspend"
        else MembershipLifecycleStatus.ACTIVE
    )
    directory_entry = _directory_entry(
        principal_id=principal_identity_id,
        display_name="Maya Chen",
        tenant_ids=(ACME_TENANT_ID, GLOBEX_TENANT_ID),
        status=status,
        include_raw_detail=True,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary=f"Principal {status_action} action saved with audit evidence.",
        toast=_toast(
            title="Principal status saved",
            summary="The status is reflected on the next protected request.",
        ),
        directory_entry=directory_entry,
        audit_reference_id=f"audit-membership-qa034-principal-{status_action}",
        next_request_effect=(
            "Principal status is evaluated on the next protected request."
        ),
    )


def build_membership_status_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    tenant_membership_id: str,
    membership_status: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.platform_admin and "globex" in tenant_membership_id:
        return _denied_result(
            audit_reference_id="audit-membership-qa034-membership-status-denied",
            summary="Membership status change was denied.",
            field="tenant_membership_id",
            message="The selected membership is not available in this tenant scope.",
        )
    if request.revision == STALE_REVISION:
        return _stale_result()
    if not request.confirmed:
        return _confirmation_result(
            title=f"Confirm {membership_status}",
            summary="Tenant membership changes affect future protected requests.",
            label="Save status",
            audit_reference_id="audit-membership-qa034-membership-status-confirm",
        )
    summary = _membership_status(
        tenant_membership_id=tenant_membership_id,
        principal_id="principal-qa034-maya",
        tenant_id=actor.active_tenant_id or ACME_TENANT_ID,
        tenant_label=actor.active_tenant_label or ACME_LABEL,
        status=MembershipLifecycleStatus(membership_status),
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Tenant membership status saved with audit evidence.",
        toast=_toast(
            title="Membership status saved",
            summary="The status is reflected on the next protected request.",
        ),
        membership_status=summary,
        audit_reference_id="audit-membership-qa034-membership-status",
        next_request_effect=(
            "Membership status is evaluated on the next protected request."
        ),
    )


def build_membership_access_history(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> MembershipAccessHistoryList:
    actor = _actor(scope=scope, principal=principal)
    return MembershipAccessHistoryList(
        scope=scope,
        records=_access_history(actor),
        partial=not actor.platform_admin,
        safe_summary="Recent access decisions are bounded and scoped.",
    )


def build_membership_audit(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> MembershipAuditList:
    actor = _actor(scope=scope, principal=principal)
    return MembershipAuditList(
        scope=scope,
        records=_audit_timeline(actor),
        unavailable=False,
        safe_summary="Membership audit records are safe for review.",
    )


def _actor(*, scope: ReactAdminScope, principal: PrincipalContext) -> MembershipActor:
    platform_admin = "platform_admin" in principal.role_codes
    tenant_admin = "tenant_admin" in principal.role_codes
    return MembershipActor(
        platform_admin=platform_admin,
        tenant_admin=tenant_admin,
        active_tenant_id=str(scope.tenant_id) if scope.tenant_id else None,
        active_tenant_label=scope.label if scope.scope_type == "tenant" else None,
    )


def _section(section_id: str, label: str, summary: str) -> MembershipSection:
    return MembershipSection(
        section_id=section_id,
        label=label,
        status=MembershipLifecycleStatus.READY,
        summary=summary,
    )


def _directory_entries(actor: MembershipActor) -> tuple[UserDirectoryEntry, ...]:
    if actor.platform_admin:
        return (
            _directory_entry(
                principal_id="principal-qa034-maya",
                display_name="Maya Chen",
                tenant_ids=(ACME_TENANT_ID, GLOBEX_TENANT_ID),
                include_raw_detail=True,
            ),
            _directory_entry(
                principal_id="principal-qa034-jordan",
                display_name="Jordan Lee",
                tenant_ids=(ACME_TENANT_ID,),
                include_raw_detail=True,
            ),
        )
    return (
        _directory_entry(
            principal_id="principal-qa034-maya",
            display_name="Maya Chen",
            tenant_ids=(actor.active_tenant_id or ACME_TENANT_ID,),
            include_raw_detail=False,
        ),
        _directory_entry(
            principal_id="principal-qa034-jordan",
            display_name="Jordan Lee",
            tenant_ids=(actor.active_tenant_id or ACME_TENANT_ID,),
            include_raw_detail=False,
        ),
    )


def _filter_directory(
    directory: tuple[UserDirectoryEntry, ...], query: str | None
) -> tuple[UserDirectoryEntry, ...]:
    if not query:
        return directory
    normalized = query.casefold()
    return tuple(
        entry
        for entry in directory
        if normalized in entry.display_name.casefold()
        or normalized in entry.masked_email.casefold()
        or normalized in entry.safe_subject_suffix.casefold()
    )


def _directory_entry(
    *,
    principal_id: str,
    display_name: str,
    tenant_ids: tuple[str, ...],
    status: MembershipLifecycleStatus = MembershipLifecycleStatus.ACTIVE,
    include_raw_detail: bool,
) -> UserDirectoryEntry:
    memberships = tuple(
        _tenant_membership(
            principal_id=principal_id,
            tenant_id=tenant_id,
            tenant_label=_tenant_label(tenant_id) or "Active tenant",
        )
        for tenant_id in tenant_ids
    )
    role_summaries = tuple(
        _role_grant(
            role_grant_id=f"grant-qa034-{_tenant_slug(tenant_id)}-{principal_id.split('-')[-1]}",
            principal_id=principal_id,
            principal_label=display_name,
            scope_type="tenant",
            tenant_id=tenant_id,
            tenant_label=_tenant_label(tenant_id),
            role_code="tenant_admin"
            if display_name.startswith("Maya")
            else "tenant_user",
            status=MembershipLifecycleStatus.ACTIVE,
            audit_reference_id=f"audit-membership-qa034-role-{_tenant_slug(tenant_id)}",
        )
        for tenant_id in tenant_ids
    )
    raw_detail = (
        RawIdentifierDetail(
            authorized=True,
            principal_identity_id=principal_id,
            external_subject=f"auth0-subject-suffix-{principal_id[-4:]}",
            invitation_id=None,
            copy_label="Copy support identifiers",
            reason="Platform support review is authorized for this detail panel.",
        )
        if include_raw_detail
        else None
    )
    return UserDirectoryEntry(
        principal_identity_id=principal_id,
        display_name=display_name,
        masked_email="m***@example.test"
        if display_name.startswith("Maya")
        else "j***@example.test",
        safe_subject_suffix=f"subject ...{principal_id[-4:]}",
        principal_status=status,
        tenant_memberships=memberships,
        role_summaries=role_summaries,
        last_access_summary="Allowed today from current role grants.",
        raw_identifier_detail=raw_detail,
        authorized_actions=(
            _post_action(
                "suspend-principal",
                f"/admin/app/memberships/principals/{principal_id}/suspend",
                "Suspend",
                confirmation="Suspend principal",
                variant=ReactAdminPageActionVariant.DANGER,
            ),
            _post_action(
                "reactivate-principal",
                f"/admin/app/memberships/principals/{principal_id}/reactivate",
                "Reactivate",
                confirmation="Reactivate principal",
            ),
        ),
    )


def _tenant_membership(
    *, principal_id: str, tenant_id: str, tenant_label: str
) -> TenantMembershipSummary:
    tenant_slug = _tenant_slug(tenant_id)
    return TenantMembershipSummary(
        tenant_membership_id=f"membership-qa034-{tenant_slug}-{principal_id.split('-')[-1]}",
        tenant_id=tenant_id,
        tenant_label=tenant_label,
        membership_status=MembershipLifecycleStatus.ACTIVE,
        revision=CURRENT_REVISION,
        membership_source="Admin assignment",
        status_reason="Active membership is available to authorized administrators.",
        authorized_actions=(
            _post_action(
                "remove-membership",
                f"/admin/app/memberships/memberships/membership-qa034-{tenant_slug}-{principal_id.split('-')[-1]}/removed",
                "Remove membership",
                confirmation="Remove membership",
                variant=ReactAdminPageActionVariant.DANGER,
            ),
            _post_action(
                "suspend-membership",
                f"/admin/app/memberships/memberships/membership-qa034-{tenant_slug}-{principal_id.split('-')[-1]}/suspended",
                "Suspend membership",
                confirmation="Suspend membership",
            ),
        ),
    )


def _membership_status(
    *,
    tenant_membership_id: str,
    principal_id: str,
    tenant_id: str,
    tenant_label: str,
    status: MembershipLifecycleStatus,
    authorized_actions: tuple[AdminAction, ...] = (),
) -> MembershipStatusSummary:
    return MembershipStatusSummary(
        tenant_membership_id=tenant_membership_id,
        principal_identity_id=principal_id,
        tenant_id=tenant_id,
        tenant_label=tenant_label,
        membership_status=status,
        revision=CURRENT_REVISION,
        membership_source="Admin assignment",
        status_reason="Status is persisted and audit-visible.",
        authorized_actions=authorized_actions,
    )


def _status_summaries(entry: UserDirectoryEntry) -> tuple[MembershipStatusSummary, ...]:
    return tuple(
        _membership_status(
            tenant_membership_id=membership.tenant_membership_id,
            principal_id=entry.principal_identity_id,
            tenant_id=membership.tenant_id,
            tenant_label=membership.tenant_label,
            status=membership.membership_status,
            authorized_actions=membership.authorized_actions,
        )
        for membership in entry.tenant_memberships
    )


def _role_grant(
    *,
    role_grant_id: str,
    principal_id: str,
    principal_label: str,
    scope_type: str,
    tenant_id: str | None,
    tenant_label: str | None,
    role_code: str,
    status: MembershipLifecycleStatus,
    audit_reference_id: str,
) -> RoleGrantSummary:
    return RoleGrantSummary(
        role_grant_id=role_grant_id,
        principal_identity_id=principal_id,
        principal_label=principal_label,
        scope_type=MembershipScopeType(scope_type),
        tenant_id=tenant_id,
        tenant_label=tenant_label,
        role_code=role_code,
        role_label=_role_label(role_code),
        grant_status=status,
        effective_label="Next protected request",
        revoked_label="Revoked today"
        if status == MembershipLifecycleStatus.REVOKED
        else None,
        next_request_effect="Role set is recalculated on the next protected request.",
        audit_reference_id=audit_reference_id,
        authorized_actions=(
            _post_action(
                "revoke-grant",
                f"/admin/app/memberships/role-grants/{role_grant_id}/revoke",
                "Revoke",
                confirmation="Revoke role grant",
                variant=ReactAdminPageActionVariant.DANGER,
            ),
        ),
    )


def _invitations(actor: MembershipActor) -> tuple[InvitationSummary, ...]:
    tenant_id = actor.active_tenant_id or ACME_TENANT_ID
    invitations: tuple[InvitationSummary, ...] = (
        _invitation_summary(
            invitation_id="invite-qa034-acme-active",
            tenant_id=tenant_id,
            tenant_label=actor.active_tenant_label or _tenant_label(tenant_id),
            replayed=True,
            requested_roles=("tenant_user",),
        ),
    )
    if actor.platform_admin:
        invitations += (
            _invitation_summary(
                invitation_id="invite-qa034-globex-pending",
                tenant_id=GLOBEX_TENANT_ID,
                tenant_label=GLOBEX_LABEL,
                replayed=False,
                requested_roles=("tenant_user",),
            ),
        )
    return invitations


def _invitation_summary(
    *,
    invitation_id: str,
    tenant_id: str | None,
    tenant_label: str | None,
    replayed: bool,
    requested_roles: tuple[str, ...],
) -> InvitationSummary:
    return InvitationSummary(
        invitation_id=invitation_id,
        tenant_id=tenant_id,
        tenant_label=tenant_label,
        masked_email="i***@example.test",
        email_hash_label="email hash qa034-df28",
        requested_roles=requested_roles,
        status=(
            MembershipLifecycleStatus.REPLAYED
            if replayed
            else MembershipLifecycleStatus.PENDING
        ),
        expires_label="7 days",
        replayed=replayed,
        next_request_effect="Requested roles apply after the next protected request.",
        audit_reference_id=(
            "audit-membership-qa034-invite-replayed"
            if replayed
            else "audit-membership-qa034-invite-created"
        ),
        authorized_actions=(),
    )


def _principal_link_summary(
    *,
    display_name: str,
    status: MembershipLifecycleStatus,
    conflict_summary: str | None,
) -> PrincipalLinkSummary:
    return PrincipalLinkSummary(
        principal_identity_id="principal-qa034-linked",
        display_name=display_name,
        masked_email="l***@example.test",
        safe_subject_suffix="subject ...7788",
        link_status=status,
        conflict_summary=conflict_summary,
        audit_reference_id="audit-membership-qa034-principal-linked",
    )


def _filters(
    actor: MembershipActor, *, query: str | None
) -> MembershipDirectoryFilters:
    tenant_options = (
        (
            _option("tenant-acme", ACME_LABEL, ACME_TENANT_ID, True),
            _option("tenant-globex", GLOBEX_LABEL, GLOBEX_TENANT_ID, False),
        )
        if actor.platform_admin
        else (
            _option(
                "tenant-active",
                actor.active_tenant_label or ACME_LABEL,
                actor.active_tenant_id or ACME_TENANT_ID,
                True,
            ),
        )
    )
    return MembershipDirectoryFilters(
        query=query,
        tenant_options=tenant_options,
        role_options=(
            _option("role-tenant-admin", "Tenant admin", "tenant_admin", False),
            _option("role-tenant-user", "Tenant user", "tenant_user", False),
        )
        + (
            (_option("role-platform-admin", "Platform admin", "platform_admin", False),)
            if actor.platform_admin
            else ()
        ),
        status_options=(
            _option("status-active", "Active", "active", True),
            _option("status-suspended", "Suspended", "suspended", False),
            _option("status-removed", "Removed", "removed", False),
        ),
        invitation_state_options=(
            _option("invite-pending", "Pending", "pending", False),
            _option("invite-replayed", "Replayed", "replayed", False),
        ),
        access_decision_options=(
            _option("decision-allow", "Allowed", "allow", False),
            _option("decision-deny", "Denied", "deny", False),
        ),
    )


def _invite_form(actor: MembershipActor) -> InvitationFormMetadata:
    return InvitationFormMetadata(
        default_tenant_id=actor.active_tenant_id
        if not actor.platform_admin
        else ACME_TENANT_ID,
        tenant_options=_filters(actor, query=None).tenant_options,
        role_choices=_role_choices(actor),
        default_expiry_label="7 days",
        idempotency_hint=(
            "Repeating the same invite returns the original active invitation."
        ),
    )


def _role_form(actor: MembershipActor) -> RoleGrantFormMetadata:
    return RoleGrantFormMetadata(
        role_choices=_role_choices(actor),
        confirmation_copy="Role changes require confirmation and audit evidence.",
        stale_recovery_copy=(
            "Reload the directory when a revision conflict is reported."
        ),
    )


def _role_choices(actor: MembershipActor) -> tuple[RoleChoice, ...]:
    choices: tuple[RoleChoice, ...] = (
        RoleChoice(
            role_code="tenant_user",
            role_label="Tenant user",
            scope_type=MembershipScopeType.TENANT,
            tenant_id=actor.active_tenant_id or ACME_TENANT_ID,
            tenant_label=actor.active_tenant_label or ACME_LABEL,
        ),
        RoleChoice(
            role_code="tenant_admin",
            role_label="Tenant admin",
            scope_type=MembershipScopeType.TENANT,
            tenant_id=actor.active_tenant_id or ACME_TENANT_ID,
            tenant_label=actor.active_tenant_label or ACME_LABEL,
        ),
    )
    if actor.platform_admin:
        choices += (
            RoleChoice(
                role_code="platform_admin",
                role_label="Platform admin",
                scope_type=MembershipScopeType.PLATFORM,
                tenant_id=None,
                tenant_label=None,
            ),
        )
    return choices


def _access_history(actor: MembershipActor) -> tuple[AccessHistoryRecord, ...]:
    records: tuple[AccessHistoryRecord, ...] = (
        AccessHistoryRecord(
            access_history_id="access-qa034-allowed",
            principal_label="Maya Chen",
            tenant_label=actor.active_tenant_label or ACME_LABEL,
            surface_key="GET:/admin/app/memberships/bootstrap.json",
            requested_action="Open membership workspace",
            decision="allow",
            reason_category="role_grant_active",
            role_source_summary="Tenant admin role from persisted grant.",
            timestamp_label="Today",
            trace_id="trace-membership-qa034-allow",
            audit_reference_id="audit-membership-qa034-access-allow",
        ),
        AccessHistoryRecord(
            access_history_id="access-qa034-denied",
            principal_label="Tenant Admin",
            tenant_label=actor.active_tenant_label or ACME_LABEL,
            surface_key="POST:/admin/app/memberships/role-grants",
            requested_action="Assign platform role",
            decision="deny",
            reason_category="role_scope_denied",
            role_source_summary=(
                "Tenant administrator role cannot grant platform access."
            ),
            timestamp_label="Today",
            trace_id="trace-membership-qa034-deny",
            audit_reference_id="audit-membership-qa034-access-deny",
        ),
    )
    if actor.platform_admin:
        records += (
            AccessHistoryRecord(
                access_history_id="access-qa034-globex",
                principal_label="Maya Chen",
                tenant_label=GLOBEX_LABEL,
                surface_key="GET:/admin/app/memberships/bootstrap.json",
                requested_action="Review authorized tenant membership",
                decision="allow",
                reason_category="platform_admin",
                role_source_summary="Platform admin role grants authorized review.",
                timestamp_label="Today",
                trace_id="trace-membership-qa034-globex",
                audit_reference_id="audit-membership-qa034-access-globex",
            ),
        )
    return records


def _audit_timeline(actor: MembershipActor) -> tuple[MembershipAuditRecord, ...]:
    records: tuple[MembershipAuditRecord, ...] = (
        MembershipAuditRecord(
            audit_reference_id="audit-membership-qa034-invite-replayed",
            domain="memberships",
            actor_label="Platform Admin" if actor.platform_admin else "Tenant Admin",
            target_label="Invite i***@example.test",
            tenant_scope_label=actor.active_tenant_label or ACME_LABEL,
            action="invitation_replayed",
            outcome="allow",
            safe_diff_summary="Original invitation returned without duplicate row.",
            timestamp_label="Today",
            redaction_class="safe-summary",
        ),
        MembershipAuditRecord(
            audit_reference_id="audit-membership-qa034-role-revoked",
            domain="memberships",
            actor_label="Platform Admin" if actor.platform_admin else "Tenant Admin",
            target_label="Maya Chen",
            tenant_scope_label=actor.active_tenant_label or ACME_LABEL,
            action="role_grant_revoked",
            outcome="allow",
            safe_diff_summary="Grant marked revoked and remains history-visible.",
            timestamp_label="Today",
            redaction_class="safe-summary",
        ),
    )
    if not actor.platform_admin:
        records += (
            MembershipAuditRecord(
                audit_reference_id="audit-membership-qa034-cross-tenant-denied",
                domain="memberships",
                actor_label="Tenant Admin",
                target_label="Unavailable resource",
                tenant_scope_label=actor.active_tenant_label or ACME_LABEL,
                action="cross_tenant_denied",
                outcome="deny",
                safe_diff_summary=(
                    "Denied without confirming external tenant resource details."
                ),
                timestamp_label="Today",
                redaction_class="safe-denial",
            ),
        )
    return records


def _common_states(actor: MembershipActor) -> tuple[ReactAdminShellState, ...]:
    return (
        ReactAdminShellState(
            state=ReactAdminShellStateKind.LOADING,
            title="Loading memberships",
            summary=(
                "Loading directory, invitations, roles, history, and audit evidence."
            ),
            action=None,
            trace_id=None,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.EMPTY,
            title="No users match the current scope",
            summary="Try a different safe search or scope filter.",
            action=None,
            trace_id=None,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DENIED,
            title="Membership action denied",
            summary=(
                "This action is outside the permitted membership scope."
                if actor.tenant_admin
                else "The action could not be authorized."
            ),
            action=None,
            trace_id="trace-membership-qa034-denied",
        ),
    )


def _default_scope_options(
    actor: MembershipActor,
) -> tuple[ReactAdminScopeOption, ...]:
    if actor.platform_admin:
        return (
            ReactAdminScopeOption(
                scope=ReactAdminScope(
                    scope_type=ReactAdminScopeType.PLATFORM,
                    tenant_id=None,
                    label="Platform",
                ),
                label="Platform",
                href="/admin/app/memberships",
                selected=actor.active_tenant_id is None,
            ),
            ReactAdminScopeOption(
                scope=ReactAdminScope(
                    scope_type=ReactAdminScopeType.TENANT,
                    tenant_id=UUID(ACME_TENANT_ID),
                    label=ACME_LABEL,
                ),
                label=ACME_LABEL,
                href=f"/admin/app/memberships?tenant_id={ACME_TENANT_ID}",
                selected=actor.active_tenant_id == ACME_TENANT_ID,
            ),
        )
    return (
        ReactAdminScopeOption(
            scope=ReactAdminScope(
                scope_type=ReactAdminScopeType.TENANT,
                tenant_id=UUID(actor.active_tenant_id or ACME_TENANT_ID),
                label=actor.active_tenant_label or ACME_LABEL,
            ),
            label=actor.active_tenant_label or ACME_LABEL,
            href=(
                "/admin/app/memberships"
                f"?tenant_id={actor.active_tenant_id or ACME_TENANT_ID}"
            ),
            selected=True,
        ),
    )


def _option(
    option_id: str, label: str, value: str, selected: bool
) -> MembershipFilterOption:
    return MembershipFilterOption(
        option_id=option_id,
        label=label,
        value=value,
        selected=selected,
    )


def _tenant_allowed(actor: MembershipActor, tenant_id: str | None) -> bool:
    return actor.platform_admin or tenant_id == actor.active_tenant_id


def _role_allowed(
    actor: MembershipActor, scope_type: str, tenant_id: str | None, role_code: str
) -> bool:
    if actor.platform_admin:
        if scope_type == "platform":
            return role_code == "platform_admin"
        return tenant_id is not None and role_code in {"tenant_admin", "tenant_user"}
    return (
        scope_type == "tenant"
        and tenant_id == actor.active_tenant_id
        and role_code in {"tenant_admin", "tenant_user"}
    )


def _tenant_label(tenant_id: str | None) -> str | None:
    if tenant_id == GLOBEX_TENANT_ID:
        return GLOBEX_LABEL
    if tenant_id == ACME_TENANT_ID:
        return ACME_LABEL
    return "Active tenant" if tenant_id else None


def _tenant_slug(tenant_id: str) -> str:
    return "globex" if tenant_id == GLOBEX_TENANT_ID else "acme"


def _role_label(role_code: str) -> str:
    return {
        "platform_admin": "Platform admin",
        "tenant_admin": "Tenant admin",
        "tenant_user": "Tenant user",
    }.get(role_code, "Tenant role")


def _post_action(
    action_id: str,
    href: str,
    label: str,
    *,
    confirmation: str | None = None,
    variant: ReactAdminPageActionVariant = ReactAdminPageActionVariant.SECONDARY,
) -> AdminAction:
    return AdminAction(
        action_id=action_id,
        label=label,
        method=AdminActionMethod.POST,
        href=href,
        variant=variant,
        requires_confirmation=confirmation is not None,
        confirmation=ConfirmationRequirement(
            title=confirmation or label,
            summary="Confirm this membership change before it is persisted.",
            confirm_label=label,
        )
        if confirmation
        else None,
        requires_idempotency_key=True,
    )


def _toast(title: str, summary: str) -> ToastHint:
    return ToastHint(
        tone=ReactAdminNotificationTone.SUCCESS,
        title=title,
        summary=summary,
    )


def _denied_result(
    *,
    audit_reference_id: str,
    summary: str,
    field: str,
    message: str,
) -> MembershipMutationResult:
    return MembershipMutationResult(
        status=AdminMutationStatus.VALIDATION_ERROR,
        summary=summary,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.WARNING,
            title="Action denied",
            summary="The backend returned a scoped denial.",
        ),
        audit_reference_id=audit_reference_id,
        field_errors=(
            ValidationFieldError(
                field=field,
                label="Scope",
                message=message,
                code="scope_denied",
            ),
        ),
        next_request_effect="No access state changed.",
    )


def _confirmation_result(
    *,
    title: str,
    summary: str,
    label: str,
    audit_reference_id: str,
) -> MembershipMutationResult:
    return MembershipMutationResult(
        status=AdminMutationStatus.CONFIRMATION_REQUIRED,
        summary=summary,
        confirmation=ConfirmationRequirement(
            title=title,
            summary=summary,
            confirm_label=label,
        ),
        audit_reference_id=audit_reference_id,
        next_request_effect="No access state changes until confirmation is submitted.",
    )


def _stale_result() -> MembershipMutationResult:
    return MembershipMutationResult(
        status=AdminMutationStatus.STALE_CONFLICT,
        summary="Membership revision changed before the action completed.",
        stale_conflict=RevisionConflict(
            submitted_revision=STALE_REVISION,
            current_revision=CURRENT_REVISION,
            message="Reload the directory and retry with the current revision.",
            reload_href="/admin/app/memberships/bootstrap.json",
        ),
        audit_reference_id="audit-membership-qa034-stale-conflict",
        next_request_effect="No access state changed.",
    )
