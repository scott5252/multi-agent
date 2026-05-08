from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.admin.memberships.models import (
    MembershipAccessScope,
    MembershipConflictError,
    MembershipPermissionError,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.models import (
    MembershipScopeType as DomainMembershipScopeType,
)
from multi_agent_platform.admin.memberships.redaction import (
    mask_email,
    mask_identifier,
)
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
    MembershipSnapshot,
)
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
    SupportOverrideSummary,
    TenantMembershipSummary,
    UserDirectoryEntry,
)
from multi_agent_platform.api.schemas.admin_membership_react import (
    MembershipScopeType as SchemaMembershipScopeType,
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
    ReactAdminActionMetadata,
    ReactAdminActionMetadataSource,
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
    ReactAdminShellState,
    ReactAdminShellStateKind,
    ReactAdminSourceKind,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    PrincipalIdentity,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrant,
    RoleGrantStatus,
    RoleScopeType,
    SupportOverrideRequest,
    SupportOverrideStatus,
)
from multi_agent_platform.db.models.user_management import (
    MembershipAuditRecord as MembershipAuditModel,
)
from multi_agent_platform.db.models.user_management import (
    TenantMembership,
    UserInvitation,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository

CURRENT_REVISION_PREFIX = "membership-live-rev"


async def build_membership_dashboard(
    *,
    repository: MembershipRepository,
    service: MembershipAdministrationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
    query: str | None = None,
) -> MembershipDashboard:
    access_scope = _access_scope(scope=scope, principal=principal)
    snapshot = await service.snapshot(access_scope, query=query)
    support_overrides = await repository.list_support_overrides(
        tenant_id=access_scope.tenant_id,
        platform_scope=access_scope.scope_type is DomainMembershipScopeType.PLATFORM,
    )
    tenant_labels = await repository.tenant_labels_for_ids(
        _tenant_ids(snapshot=snapshot, support_overrides=support_overrides)
    )
    directory = _directory_entries(
        snapshot=snapshot,
        access_scope=access_scope,
        scope=scope,
        tenant_labels=tenant_labels,
    )
    invitations = tuple(
        _invitation_summary(invitation, tenant_labels=tenant_labels, replayed=False)
        for invitation in snapshot.invitations
    )
    role_grants = tuple(
        _role_grant_summary(
            grant,
            principals=snapshot.principals,
            tenant_labels=tenant_labels,
            access_scope=access_scope,
        )
        for grant in snapshot.role_grants
    )
    status_actions = tuple(
        _membership_status_summary(
            membership,
            tenant_labels=tenant_labels,
            access_scope=access_scope,
        )
        for membership in snapshot.memberships
    )
    access_history = _access_history_records(
        snapshot.access_history,
        principals=snapshot.principals,
        tenant_labels=tenant_labels,
    )
    audit_timeline = _audit_records(
        snapshot.audit_records,
        principals=snapshot.principals,
        tenant_labels=tenant_labels,
    )
    override_summaries = tuple(
        _support_override_summary(
            override,
            principals=snapshot.principals,
            tenant_labels=tenant_labels,
        )
        for override in support_overrides
    )
    empty_state = _empty_state(
        scope=scope,
        row_count=(
            len(directory)
            + len(invitations)
            + len(role_grants)
            + len(access_history)
            + len(audit_timeline)
            + len(override_summaries)
        ),
    )
    return MembershipDashboard(
        page_id="membership-administration-live",
        title="Membership Administration",
        description=(
            "Manage users, invitations, roles, status, and access evidence "
            "from live membership records."
        ),
        scope=scope,
        summary_cards=(
            MembershipSummaryCard(
                card_id="directory",
                label="Directory",
                value=str(len(directory)),
                status=_card_status(directory),
                summary="Principal rows are loaded from authorized membership state.",
            ),
            MembershipSummaryCard(
                card_id="invites",
                label="Invitations",
                value=str(len(invitations)),
                status=_card_status(
                    invitations, empty=MembershipLifecycleStatus.PENDING
                ),
                summary="Invitation rows are persisted and replay-safe.",
            ),
            MembershipSummaryCard(
                card_id="grants",
                label="Role grants",
                value=str(len(role_grants)),
                status=_card_status(role_grants),
                summary="Role grants reflect durable access assignments.",
            ),
            MembershipSummaryCard(
                card_id="history",
                label="Access history",
                value=str(len(access_history)),
                status=_card_status(
                    access_history,
                    empty=MembershipLifecycleStatus.UNAVAILABLE,
                ),
                summary="Recent access decisions are bounded and scoped.",
            ),
            MembershipSummaryCard(
                card_id="support-overrides",
                label="Support overrides",
                value=str(len(override_summaries)),
                status=_card_status(
                    override_summaries,
                    empty=MembershipLifecycleStatus.UNAVAILABLE,
                ),
                summary="Support override evidence is live when persisted.",
            ),
        ),
        sections=(
            _section("overview", "Overview", "Scope and live-data summary"),
            _section("directory", "Directory", "Users and membership status"),
            _section("invitations", "Invitations", "Create or replay invites"),
            _section("roles", "Role grants", "Assign and revoke roles"),
            _section("status", "Status", "Suspend, reactivate, or remove"),
            _section("history", "Access history", "Recent decisions"),
            _section("support", "Support overrides", "Temporary access evidence"),
            _section("audit", "Audit", "Safe audit records"),
        ),
        directory=directory,
        filters=_filters(
            access_scope=access_scope,
            scope=scope,
            tenant_labels=tenant_labels,
            query=query,
        ),
        allowed_scope_options=allowed_scope_options,
        invite_form=_invite_form(
            access_scope=access_scope,
            scope=scope,
            tenant_labels=tenant_labels,
        ),
        role_grant_form=_role_form(
            access_scope=access_scope,
            scope=scope,
            tenant_labels=tenant_labels,
        ),
        invitations=invitations,
        role_grants=role_grants,
        status_actions=status_actions,
        access_history=access_history,
        audit_timeline=audit_timeline,
        support_overrides=override_summaries,
        provenance=_live_provenance("Membership repository snapshot"),
        empty_state=empty_state,
        common_states=_common_states(access_scope=access_scope, scope=scope),
    )


async def build_invitation_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: MembershipInvitationSaveRequest,
) -> MembershipMutationResult:
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        requested_roles = _requested_roles(request.requested_roles)
        result = await service.create_invitation(
            access_scope=access_scope,
            email=request.email,
            requested_roles=requested_roles,
            tenant_id=_optional_uuid(request.tenant_id) or access_scope.tenant_id,
            idempotency_key=request.idempotency_key,
        )
    except (MembershipPermissionError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-invitation",
            summary="Invitation request was denied or invalid.",
            field="tenant_id",
            message=str(exc),
        )
    tenant_labels = await repository.tenant_labels_for_ids(
        {result.invitation.tenant_id} if result.invitation.tenant_id else set()
    )
    invitation = _invitation_summary(
        result.invitation,
        tenant_labels=tenant_labels,
        replayed=result.replayed,
    )
    return MembershipMutationResult(
        status=(
            AdminMutationStatus.REPLAYED
            if result.replayed
            else AdminMutationStatus.ACCEPTED
        ),
        summary=(
            "Invitation replayed from persisted membership state."
            if result.replayed
            else "Invitation created in persisted membership state."
        ),
        toast=_toast(
            title="Invitation ready",
            summary="The invitation is visible with masked identity details.",
        ),
        invitation=invitation,
        audit_reference_id=invitation.audit_reference_id,
        idempotency_replay=result.replayed,
        next_request_effect=(
            "Requested roles apply after the user's next protected request."
        ),
    )


async def build_principal_link_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: PrincipalLinkRequest,
) -> MembershipMutationResult:
    access_scope = _access_scope(scope=scope, principal=principal)
    existing = await repository.get_principal_by_subject(request.external_subject)
    if existing is not None and not request.overwrite_confirmed:
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
                existing,
                conflict_summary="Existing identity summary requires review.",
            ),
            audit_reference_id=_audit_reference(
                "principal-link-confirm", existing.principal_identity_id
            ),
            next_request_effect=(
                "Linked identity changes apply on the next protected request."
            ),
        )
    try:
        record = await service.link_auth0_principal(
            access_scope=access_scope,
            auth0_subject=request.external_subject,
            email=request.email,
            display_name=request.display_name,
            principal_identity_id=_optional_uuid(request.principal_identity_id),
        )
    except MembershipConflictError as exc:
        return _conflict_result(
            submitted_revision="principal-link",
            current_revision="existing-principal-link",
            message=str(exc),
            audit_reference_id="membership-live-principal-link-conflict",
        )
    except (MembershipPermissionError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-principal-link",
            summary="Principal link was denied or invalid.",
            field="external_subject",
            message=str(exc),
        )
    link = _principal_link_summary(record, conflict_summary=None)
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Principal identity linked with persisted audit evidence.",
        toast=_toast(
            title="Principal linked",
            summary="The new identity is available in the live directory.",
        ),
        principal_link=link,
        audit_reference_id=link.audit_reference_id,
        next_request_effect=(
            "Linked identity changes apply on the next protected request."
        ),
    )


async def build_role_grant_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: RoleGrantSaveRequest,
) -> MembershipMutationResult:
    if not request.confirmed:
        return _confirmation_result(
            title="Confirm role grant",
            summary=(
                "The selected role changes access after the next protected request."
            ),
            label="Grant role",
            audit_reference_id="membership-live-role-confirm",
        )
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        grant = await service.create_role_grant(
            access_scope=access_scope,
            principal_identity_id=UUID(request.principal_identity_id),
            scope_type=RoleScopeType(request.scope_type.value),
            role_code=RoleCode(request.role_code),
            tenant_id=_optional_uuid(request.tenant_id),
        )
    except (MembershipPermissionError, LookupError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-role-grant",
            summary="Role grant was denied or invalid.",
            field="role_code",
            message=str(exc),
        )
    tenant_labels = await repository.tenant_labels_for_ids(
        {grant.tenant_id} if grant.tenant_id else set()
    )
    principal_record = await repository.get_principal(grant.principal_identity_id)
    role_grant = _role_grant_summary(
        grant,
        principals=(principal_record,) if principal_record is not None else (),
        tenant_labels=tenant_labels,
        access_scope=access_scope,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Role grant saved with backend eligibility evidence.",
        toast=_toast(
            title="Role grant saved",
            summary="The changed role set is reflected on the next protected request.",
        ),
        role_grant=role_grant,
        audit_reference_id=role_grant.audit_reference_id,
        next_request_effect=role_grant.next_request_effect,
    )


async def build_grant_revoke_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    role_grant_id: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    if not request.confirmed:
        return _confirmation_result(
            title="Confirm grant revoke",
            summary=(
                "Revoking the grant changes access after the next protected request."
            ),
            label="Revoke grant",
            audit_reference_id="membership-live-revoke-confirm",
        )
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        revoked = await service.revoke_role_grant(
            access_scope=access_scope,
            role_grant_id=UUID(role_grant_id),
        )
    except (MembershipPermissionError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-role-revoke",
            summary="Grant revoke was denied or invalid.",
            field="role_grant_id",
            message=str(exc),
        )
    if revoked is None:
        return _unavailable_result(
            audit_reference_id="membership-live-role-revoke-missing",
            summary="Role grant was not found in the authorized live scope.",
        )
    tenant_labels = await repository.tenant_labels_for_ids(
        {revoked.tenant_id} if revoked.tenant_id else set()
    )
    principal_record = await repository.get_principal(revoked.principal_identity_id)
    grant = _role_grant_summary(
        revoked,
        principals=(principal_record,) if principal_record is not None else (),
        tenant_labels=tenant_labels,
        access_scope=access_scope,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Role grant revoked with safe audit evidence.",
        toast=_toast(title="Grant revoked", summary="The role is no longer active."),
        role_grant=grant,
        audit_reference_id=grant.audit_reference_id,
        next_request_effect=grant.next_request_effect,
    )


async def build_principal_status_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    principal_identity_id: str,
    status_action: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    if not request.confirmed:
        return _confirmation_result(
            title=f"Confirm {status_action}",
            summary="Principal status changes affect future protected requests.",
            label=status_action.title(),
            audit_reference_id="membership-live-principal-status-confirm",
        )
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        principal_uuid = UUID(principal_identity_id)
        current = await repository.get_principal(principal_uuid)
        if current is not None and _is_stale(
            request.revision, _revision(current.updated_at)
        ):
            return _stale_result(
                submitted_revision=request.revision,
                current_revision=_revision(current.updated_at),
            )
        record = (
            await service.suspend_principal(
                access_scope=access_scope,
                principal_identity_id=principal_uuid,
            )
            if status_action == "suspend"
            else await service.reactivate_principal(
                access_scope=access_scope,
                principal_identity_id=principal_uuid,
            )
        )
    except (MembershipPermissionError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-principal-status",
            summary="Principal status change was denied or invalid.",
            field="principal_identity_id",
            message=str(exc),
        )
    if record is None:
        return _unavailable_result(
            audit_reference_id="membership-live-principal-status-missing",
            summary="Principal identity was not found in the live repository.",
        )
    directory_entry = _directory_entry(
        record,
        memberships=(),
        grants=(),
        access_history=(),
        tenant_labels={},
        access_scope=access_scope,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary=f"Principal {status_action} action saved with audit evidence.",
        toast=_toast(
            title="Principal status saved",
            summary="The status is reflected on the next protected request.",
        ),
        directory_entry=directory_entry,
        audit_reference_id=_audit_reference(
            f"principal-{status_action}", record.principal_identity_id
        ),
        next_request_effect=(
            "Principal status is evaluated on the next protected request."
        ),
    )


async def build_membership_status_result(
    *,
    service: MembershipAdministrationService,
    repository: MembershipRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    tenant_membership_id: str,
    membership_status: str,
    request: MembershipConfirmationRequest,
) -> MembershipMutationResult:
    if not request.confirmed:
        return _confirmation_result(
            title=f"Confirm {membership_status}",
            summary="Tenant membership changes affect future protected requests.",
            label="Save status",
            audit_reference_id="membership-live-membership-status-confirm",
        )
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        membership_uuid = UUID(tenant_membership_id)
        target_status = TenantMembershipStatus(membership_status)
    except ValueError as exc:
        return _denied_result(
            audit_reference_id="membership-live-membership-status-invalid",
            summary="Membership status change was invalid.",
            field="tenant_membership_id",
            message=str(exc),
        )
    record = await repository.get_membership(membership_uuid)
    if record is None:
        return _unavailable_result(
            audit_reference_id="membership-live-membership-status-missing",
            summary="Tenant membership was not found in the live repository.",
        )
    if _is_stale(request.revision, record.revision_token):
        return _stale_result(
            submitted_revision=request.revision,
            current_revision=record.revision_token,
        )
    mutation_scope = MembershipAccessScope(
        scope_type=DomainMembershipScopeType.TENANT,
        principal_id=access_scope.principal_id,
        tenant_id=record.tenant_id,
        platform_admin=access_scope.platform_admin,
        trace_id=access_scope.trace_id,
    )
    try:
        updated = await service.update_membership_status(
            access_scope=mutation_scope,
            tenant_membership_id=membership_uuid,
            status=target_status,
        )
    except (MembershipPermissionError, ValueError) as exc:
        return _denied_result(
            audit_reference_id="membership-live-denied-membership-status",
            summary="Membership status change was denied or invalid.",
            field="tenant_membership_id",
            message=str(exc),
        )
    if updated is None:
        return _unavailable_result(
            audit_reference_id="membership-live-membership-status-unavailable",
            summary="Tenant membership was not available in the authorized scope.",
        )
    tenant_labels = await repository.tenant_labels_for_ids({updated.tenant_id})
    summary = _membership_status_summary(
        updated,
        tenant_labels=tenant_labels,
        access_scope=mutation_scope,
    )
    return MembershipMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Tenant membership status saved with audit evidence.",
        toast=_toast(
            title="Membership status saved",
            summary="The status is reflected on the next protected request.",
        ),
        membership_status=summary,
        audit_reference_id=_audit_reference(
            "membership-status", updated.tenant_membership_id
        ),
        next_request_effect=(
            "Membership status is evaluated on the next protected request."
        ),
    )


async def build_membership_access_history(
    *,
    service: MembershipAdministrationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> MembershipAccessHistoryList:
    access_scope = _access_scope(scope=scope, principal=principal)
    snapshot = await service.snapshot(access_scope)
    return MembershipAccessHistoryList(
        scope=scope,
        records=_access_history_records(
            snapshot.access_history,
            principals=snapshot.principals,
            tenant_labels={},
        ),
        partial=not access_scope.platform_admin,
        safe_summary="Recent access decisions are loaded from live access records.",
    )


async def build_membership_audit(
    *,
    service: MembershipAdministrationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> MembershipAuditList:
    access_scope = _access_scope(scope=scope, principal=principal)
    snapshot = await service.snapshot(access_scope)
    return MembershipAuditList(
        scope=scope,
        records=_audit_records(
            snapshot.audit_records,
            principals=snapshot.principals,
            tenant_labels={},
        ),
        unavailable=False,
        safe_summary="Membership audit records are loaded from live audit rows.",
    )


def _access_scope(
    *, scope: ReactAdminScope, principal: PrincipalContext
) -> MembershipAccessScope:
    platform_admin = "platform_admin" in set(principal.role_codes)
    tenant_id = scope.tenant_id or principal.tenant_id
    if scope.scope_type == ReactAdminScopeType.PLATFORM:
        scope_type = DomainMembershipScopeType.PLATFORM
        tenant_id = None
    else:
        scope_type = DomainMembershipScopeType.TENANT
    return MembershipAccessScope(
        scope_type=scope_type,
        principal_id=principal.principal_id,
        tenant_id=tenant_id,
        platform_admin=platform_admin,
        trace_id=principal.trace_id or "membership-react-live-data",
    )


def _tenant_ids(
    *,
    snapshot: MembershipSnapshot,
    support_overrides: Iterable[SupportOverrideRequest],
) -> set[UUID]:
    tenant_ids: set[UUID] = set()
    for invitation in snapshot.invitations:
        if invitation.tenant_id:
            tenant_ids.add(invitation.tenant_id)
    for membership in snapshot.memberships:
        tenant_ids.add(membership.tenant_id)
    for grant in snapshot.role_grants:
        if grant.tenant_id:
            tenant_ids.add(grant.tenant_id)
    for decision in snapshot.access_history:
        if decision.tenant_id:
            tenant_ids.add(decision.tenant_id)
    for audit in snapshot.audit_records:
        if audit.tenant_id:
            tenant_ids.add(audit.tenant_id)
    for override in support_overrides:
        tenant_ids.add(override.target_tenant_id)
    return tenant_ids


def _directory_entries(
    *,
    snapshot: MembershipSnapshot,
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope,
    tenant_labels: Mapping[UUID, str],
) -> tuple[UserDirectoryEntry, ...]:
    memberships_by_principal: dict[UUID, list[TenantMembership]] = {}
    for membership in snapshot.memberships:
        memberships_by_principal.setdefault(
            membership.principal_identity_id, []
        ).append(membership)
    grants_by_principal: dict[UUID, list[RoleGrant]] = {}
    for grant in snapshot.role_grants:
        grants_by_principal.setdefault(grant.principal_identity_id, []).append(grant)
    access_by_principal: dict[UUID, list[AccessDecisionRecord]] = {}
    for record in snapshot.access_history:
        if record.principal_identity_id is not None:
            access_by_principal.setdefault(record.principal_identity_id, []).append(
                record
            )
    return tuple(
        _directory_entry(
            principal,
            memberships=memberships_by_principal.get(
                principal.principal_identity_id, []
            ),
            grants=grants_by_principal.get(principal.principal_identity_id, []),
            access_history=access_by_principal.get(principal.principal_identity_id, []),
            tenant_labels=tenant_labels,
            access_scope=access_scope,
            scope=scope,
        )
        for principal in snapshot.principals
    )


def _directory_entry(
    principal: PrincipalIdentity,
    *,
    memberships: Iterable[TenantMembership],
    grants: Iterable[RoleGrant],
    access_history: Iterable[AccessDecisionRecord],
    tenant_labels: Mapping[UUID, str],
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope | None = None,
) -> UserDirectoryEntry:
    memberships_tuple = tuple(
        _tenant_membership_summary(
            membership,
            tenant_labels=tenant_labels,
            access_scope=access_scope,
        )
        for membership in memberships
    )
    grants_tuple = tuple(
        _role_grant_summary(
            grant,
            principals=(principal,),
            tenant_labels=tenant_labels,
            access_scope=access_scope,
        )
        for grant in grants
    )
    access_tuple = tuple(access_history)
    return UserDirectoryEntry(
        principal_identity_id=str(principal.principal_identity_id),
        display_name=_principal_label(principal),
        masked_email=mask_email(principal.email)
        if principal.email
        else "email unavailable",
        safe_subject_suffix=mask_identifier(principal.external_subject),
        principal_status=_principal_status(principal.status),
        tenant_memberships=memberships_tuple,
        role_summaries=grants_tuple,
        last_access_summary=_last_access_summary(access_tuple),
        raw_identifier_detail=_raw_identifier_detail(principal)
        if access_scope.platform_admin and scope is not None
        else None,
        authorized_actions=_principal_actions(principal, access_scope=access_scope),
    )


def _tenant_membership_summary(
    membership: TenantMembership,
    *,
    tenant_labels: Mapping[UUID, str],
    access_scope: MembershipAccessScope,
) -> TenantMembershipSummary:
    return TenantMembershipSummary(
        tenant_membership_id=str(membership.tenant_membership_id),
        tenant_id=str(membership.tenant_id),
        tenant_label=_tenant_label(membership.tenant_id, tenant_labels),
        membership_status=_membership_status(membership.status),
        revision=membership.revision_token,
        membership_source=_source_label(membership.membership_source),
        status_reason="Status is persisted and audit-visible.",
        authorized_actions=_membership_actions(membership, access_scope=access_scope),
    )


def _membership_status_summary(
    membership: TenantMembership,
    *,
    tenant_labels: Mapping[UUID, str],
    access_scope: MembershipAccessScope,
) -> MembershipStatusSummary:
    return MembershipStatusSummary(
        tenant_membership_id=str(membership.tenant_membership_id),
        principal_identity_id=str(membership.principal_identity_id),
        tenant_id=str(membership.tenant_id),
        tenant_label=_tenant_label(membership.tenant_id, tenant_labels),
        membership_status=_membership_status(membership.status),
        revision=membership.revision_token,
        membership_source=_source_label(membership.membership_source),
        status_reason="Status is persisted and audit-visible.",
        authorized_actions=_membership_actions(membership, access_scope=access_scope),
    )


def _role_grant_summary(
    grant: RoleGrant,
    *,
    principals: Iterable[PrincipalIdentity],
    tenant_labels: Mapping[UUID, str],
    access_scope: MembershipAccessScope,
) -> RoleGrantSummary:
    principal = next(
        (
            item
            for item in principals
            if item.principal_identity_id == grant.principal_identity_id
        ),
        None,
    )
    status = _grant_status(grant.status)
    return RoleGrantSummary(
        role_grant_id=str(grant.role_grant_id),
        principal_identity_id=str(grant.principal_identity_id),
        principal_label=_principal_label(principal) if principal else "Principal",
        scope_type=SchemaMembershipScopeType(_value(grant.scope_type)),
        tenant_id=str(grant.tenant_id) if grant.tenant_id else None,
        tenant_label=_tenant_label(grant.tenant_id, tenant_labels)
        if grant.tenant_id
        else None,
        role_code=_value(grant.role_code),
        role_label=_role_label(_value(grant.role_code)),
        grant_status=status,
        effective_label=_time_label(grant.effective_at),
        revoked_label=_time_label(grant.revoked_at) if grant.revoked_at else None,
        next_request_effect="Role set is recalculated on the next protected request.",
        audit_reference_id=_audit_reference("role-grant", grant.role_grant_id),
        authorized_actions=_grant_actions(
            grant, status=status, access_scope=access_scope
        ),
    )


def _invitation_summary(
    invitation: UserInvitation,
    *,
    tenant_labels: Mapping[UUID, str],
    replayed: bool,
) -> InvitationSummary:
    status = (
        MembershipLifecycleStatus.REPLAYED
        if replayed
        else _invitation_status(invitation.status)
    )
    return InvitationSummary(
        invitation_id=str(invitation.user_invitation_id),
        tenant_id=str(invitation.tenant_id) if invitation.tenant_id else None,
        tenant_label=_tenant_label(invitation.tenant_id, tenant_labels)
        if invitation.tenant_id
        else "Platform",
        masked_email=invitation.masked_email,
        email_hash_label=f"email hash {invitation.invited_email_hash[:16]}",
        requested_roles=tuple(sorted(invitation.requested_roles or [])),
        status=status,
        expires_label=_time_label(invitation.expires_at)
        if invitation.expires_at
        else "No expiration recorded",
        replayed=replayed,
        next_request_effect="Requested roles apply after the next protected request.",
        audit_reference_id=_audit_reference(
            "invitation", invitation.user_invitation_id
        ),
        authorized_actions=(),
    )


def _principal_link_summary(
    principal: PrincipalIdentity,
    *,
    conflict_summary: str | None,
) -> PrincipalLinkSummary:
    return PrincipalLinkSummary(
        principal_identity_id=str(principal.principal_identity_id),
        display_name=_principal_label(principal),
        masked_email=mask_email(principal.email) if principal.email else None,
        safe_subject_suffix=mask_identifier(principal.external_subject),
        link_status=_principal_status(principal.status),
        conflict_summary=conflict_summary,
        audit_reference_id=_audit_reference(
            "principal-link", principal.principal_identity_id
        ),
    )


def _access_history_records(
    records: Iterable[AccessDecisionRecord],
    *,
    principals: Iterable[PrincipalIdentity],
    tenant_labels: Mapping[UUID, str],
) -> tuple[AccessHistoryRecord, ...]:
    principal_map = {item.principal_identity_id: item for item in principals}
    return tuple(
        AccessHistoryRecord(
            access_history_id=str(record.access_decision_record_id),
            principal_label=_principal_label(
                principal_map.get(record.principal_identity_id)
            )
            if record.principal_identity_id
            else "Unauthenticated principal",
            tenant_label=_tenant_label(record.tenant_id, tenant_labels)
            if record.tenant_id
            else "Platform",
            surface_key=record.surface_key,
            requested_action=record.requested_action,
            decision=_value(record.decision),
            reason_category=_value(record.reason_code),
            role_source_summary=_required_role_summary(record.required_roles),
            timestamp_label=_time_label(record.occurred_at),
            trace_id=record.trace_id,
            audit_reference_id=_audit_reference(
                "access-decision",
                record.access_decision_record_id,
            ),
        )
        for record in records
    )


def _audit_records(
    records: Iterable[MembershipAuditModel],
    *,
    principals: Iterable[PrincipalIdentity],
    tenant_labels: Mapping[UUID, str],
) -> tuple[MembershipAuditRecord, ...]:
    principal_map = {item.principal_identity_id: item for item in principals}
    return tuple(
        MembershipAuditRecord(
            audit_reference_id=str(record.membership_audit_record_id),
            domain="memberships",
            actor_label=mask_identifier(record.actor_principal_id),
            target_label=_principal_label(
                principal_map.get(record.target_principal_identity_id)
            )
            if record.target_principal_identity_id
            else "Membership resource",
            tenant_scope_label=_tenant_label(record.tenant_id, tenant_labels)
            if record.tenant_id
            else "Platform",
            action=record.action,
            outcome=record.decision,
            safe_diff_summary=record.summary,
            timestamp_label=_time_label(record.created_at),
            redaction_class="safe-summary",
        )
        for record in records
    )


def _support_override_summary(
    override: SupportOverrideRequest,
    *,
    principals: Iterable[PrincipalIdentity],
    tenant_labels: Mapping[UUID, str],
) -> SupportOverrideSummary:
    principal_map = {item.principal_identity_id: item for item in principals}
    requester = principal_map.get(override.requester_principal_id)
    approver = (
        principal_map.get(override.approver_principal_id)
        if override.approver_principal_id
        else None
    )
    return SupportOverrideSummary(
        support_override_id=str(override.support_override_request_id),
        tenant_id=str(override.target_tenant_id),
        tenant_label=_tenant_label(override.target_tenant_id, tenant_labels),
        requester_label=_principal_label(requester)
        if requester
        else mask_identifier(str(override.requester_principal_id)),
        approver_label=_principal_label(approver) if approver else None,
        status=_support_override_status(override.status),
        expires_label=_time_label(override.expires_at)
        if override.expires_at
        else "No expiration recorded",
        audit_reference_id=_audit_reference(
            "support-override",
            override.support_override_request_id,
        ),
        safe_summary="Support override evidence is persisted and scoped.",
    )


def _filters(
    *,
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope,
    tenant_labels: Mapping[UUID, str],
    query: str | None,
) -> MembershipDirectoryFilters:
    tenant_options = tuple(
        _option(
            f"tenant-{tenant_id}",
            label,
            str(tenant_id),
            scope.tenant_id == tenant_id,
        )
        for tenant_id, label in sorted(
            tenant_labels.items(),
            key=lambda item: item[1].lower(),
        )
    )
    if not tenant_options and access_scope.tenant_id:
        tenant_options = (
            _option(
                f"tenant-{access_scope.tenant_id}",
                scope.label,
                str(access_scope.tenant_id),
                True,
            ),
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
            if access_scope.platform_admin
            else ()
        ),
        status_options=(
            _option("status-active", "Active", "active", True),
            _option("status-suspended", "Suspended", "suspended", False),
            _option("status-removed", "Removed", "removed", False),
        ),
        invitation_state_options=(
            _option("invite-pending", "Pending", "pending", False),
            _option("invite-accepted", "Accepted", "accepted", False),
            _option("invite-revoked", "Revoked", "revoked", False),
            _option("invite-expired", "Expired", "expired", False),
        ),
        access_decision_options=(
            _option("decision-allow", "Allowed", "allow", False),
            _option("decision-deny", "Denied", "deny", False),
            _option("decision-error", "Error", "error", False),
        ),
    )


def _invite_form(
    *,
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope,
    tenant_labels: Mapping[UUID, str],
) -> InvitationFormMetadata:
    filters = _filters(
        access_scope=access_scope,
        scope=scope,
        tenant_labels=tenant_labels,
        query=None,
    )
    default_tenant_id = (
        str(access_scope.tenant_id)
        if access_scope.tenant_id
        else filters.tenant_options[0].value
        if filters.tenant_options
        else None
    )
    return InvitationFormMetadata(
        default_tenant_id=default_tenant_id,
        tenant_options=filters.tenant_options,
        role_choices=_role_choices(
            access_scope=access_scope,
            default_tenant_id=default_tenant_id,
            tenant_labels=tenant_labels,
            scope_label=scope.label,
        ),
        default_expiry_label="7 days",
        idempotency_hint=(
            "Repeating the same active invitation returns the original live row."
        ),
    )


def _role_form(
    *,
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope,
    tenant_labels: Mapping[UUID, str],
) -> RoleGrantFormMetadata:
    default_tenant_id = str(access_scope.tenant_id) if access_scope.tenant_id else None
    return RoleGrantFormMetadata(
        role_choices=_role_choices(
            access_scope=access_scope,
            default_tenant_id=default_tenant_id,
            tenant_labels=tenant_labels,
            scope_label=scope.label,
        ),
        confirmation_copy="Role changes require confirmation and audit evidence.",
        stale_recovery_copy=(
            "Reload the directory when a revision conflict is reported."
        ),
    )


def _role_choices(
    *,
    access_scope: MembershipAccessScope,
    default_tenant_id: str | None,
    tenant_labels: Mapping[UUID, str],
    scope_label: str,
) -> tuple[RoleChoice, ...]:
    tenant_label = (
        _tenant_label(UUID(default_tenant_id), tenant_labels)
        if default_tenant_id
        else scope_label
    )
    choices: tuple[RoleChoice, ...] = ()
    if default_tenant_id is not None:
        choices += (
            RoleChoice(
                role_code="tenant_user",
                role_label="Tenant user",
                scope_type=SchemaMembershipScopeType.TENANT,
                tenant_id=default_tenant_id,
                tenant_label=tenant_label,
            ),
            RoleChoice(
                role_code="tenant_admin",
                role_label="Tenant admin",
                scope_type=SchemaMembershipScopeType.TENANT,
                tenant_id=default_tenant_id,
                tenant_label=tenant_label,
            ),
        )
    if access_scope.platform_admin:
        choices += (
            RoleChoice(
                role_code="platform_admin",
                role_label="Platform admin",
                scope_type=SchemaMembershipScopeType.PLATFORM,
                tenant_id=None,
                tenant_label=None,
            ),
        )
    return choices


def _principal_actions(
    principal: PrincipalIdentity,
    *,
    access_scope: MembershipAccessScope,
) -> tuple[AdminAction, ...]:
    if not access_scope.platform_admin:
        return ()
    status = _value(principal.status)
    if status == PrincipalIdentityStatus.SUSPENDED.value:
        return (
            _post_action(
                "reactivate-principal",
                f"/admin/app/memberships/principals/{principal.principal_identity_id}/reactivate",
                "Reactivate",
                confirmation="Reactivate principal",
                revision=_revision(principal.updated_at),
            ),
        )
    return (
        _post_action(
            "suspend-principal",
            f"/admin/app/memberships/principals/{principal.principal_identity_id}/suspend",
            "Suspend",
            confirmation="Suspend principal",
            variant=ReactAdminPageActionVariant.DANGER,
            revision=_revision(principal.updated_at),
        ),
    )


def _membership_actions(
    membership: TenantMembership,
    *,
    access_scope: MembershipAccessScope,
) -> tuple[AdminAction, ...]:
    if (
        not access_scope.platform_admin
        and access_scope.tenant_id != membership.tenant_id
    ):
        return ()
    base = f"/admin/app/memberships/memberships/{membership.tenant_membership_id}"
    status = _value(membership.status)
    actions: list[AdminAction] = []
    if status != TenantMembershipStatus.ACTIVE.value:
        actions.append(
            _post_action(
                "restore-membership",
                f"{base}/active",
                "Restore membership",
                confirmation="Restore membership",
                revision=membership.revision_token,
            )
        )
    if status != TenantMembershipStatus.SUSPENDED.value:
        actions.append(
            _post_action(
                "suspend-membership",
                f"{base}/suspended",
                "Suspend membership",
                confirmation="Suspend membership",
                revision=membership.revision_token,
            )
        )
    if status != TenantMembershipStatus.REMOVED.value:
        actions.append(
            _post_action(
                "remove-membership",
                f"{base}/removed",
                "Remove membership",
                confirmation="Remove membership",
                variant=ReactAdminPageActionVariant.DANGER,
                revision=membership.revision_token,
            )
        )
    return tuple(actions)


def _grant_actions(
    grant: RoleGrant,
    *,
    status: MembershipLifecycleStatus,
    access_scope: MembershipAccessScope,
) -> tuple[AdminAction, ...]:
    if status != MembershipLifecycleStatus.ACTIVE:
        return ()
    if not access_scope.platform_admin and (
        grant.scope_type is not RoleScopeType.TENANT
        or grant.tenant_id != access_scope.tenant_id
    ):
        return ()
    return (
        _post_action(
            "revoke-grant",
            f"/admin/app/memberships/role-grants/{grant.role_grant_id}/revoke",
            "Revoke",
            confirmation="Revoke role grant",
            variant=ReactAdminPageActionVariant.DANGER,
            revision=_revision(grant.updated_at),
        ),
    )


def _raw_identifier_detail(principal: PrincipalIdentity) -> RawIdentifierDetail:
    return RawIdentifierDetail(
        authorized=True,
        principal_identity_id=str(principal.principal_identity_id),
        external_subject=mask_identifier(principal.external_subject),
        invitation_id=None,
        copy_label="Copy support identifiers",
        reason="Platform support review is authorized for this masked detail panel.",
    )


def _common_states(
    *,
    access_scope: MembershipAccessScope,
    scope: ReactAdminScope,
) -> tuple[ReactAdminShellState, ...]:
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
            title="No live membership rows",
            summary=(
                "This scope has no persisted users, invitations, grants, access "
                "decisions, support overrides, or audit records yet."
            ),
            action=None,
            trace_id=None,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DENIED,
            title="Membership action denied",
            summary=(
                "This action is outside the permitted membership scope."
                if not access_scope.platform_admin
                else "The action could not be authorized."
            ),
            action=None,
            trace_id=f"membership-live-denied-{scope.scope_type.value}",
        ),
    )


def _empty_state(
    *,
    scope: ReactAdminScope,
    row_count: int,
) -> ReactAdminEmptyStateMetadata | None:
    if row_count > 0:
        return None
    return ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title="No live membership rows",
        summary=(
            "No persisted users, invitations, grants, access decisions, support "
            "overrides, or audit records exist for this authorized scope."
        ),
        setup_hint="Run the membership QA seed helper to create local-principal rows.",
        provenance=ReactAdminPageProvenance(
            source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
            source_label="Empty membership repository",
            source_detail=f"Scope {scope.scope_type.value} returned zero live rows.",
            last_verified_at=datetime.now(UTC),
        ),
    )


def _live_provenance(source_label: str) -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=ReactAdminSourceKind.LIVE_REPOSITORY,
        source_label=source_label,
        source_detail=(
            "Membership projections are composed from persisted repository rows."
        ),
        last_verified_at=datetime.now(UTC),
    )


def _section(section_id: str, label: str, summary: str) -> MembershipSection:
    return MembershipSection(
        section_id=section_id,
        label=label,
        status=MembershipLifecycleStatus.READY,
        summary=summary,
    )


def _option(
    option_id: str,
    label: str,
    value: str,
    selected: bool,
) -> MembershipFilterOption:
    return MembershipFilterOption(
        option_id=option_id,
        label=label,
        value=value,
        selected=selected,
    )


def _post_action(
    action_id: str,
    href: str,
    label: str,
    *,
    confirmation: str | None = None,
    variant: ReactAdminPageActionVariant = ReactAdminPageActionVariant.SECONDARY,
    revision: str | None = None,
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
        action_metadata=ReactAdminActionMetadata(
            revision=revision,
            revision_source=(
                ReactAdminActionMetadataSource.BACKEND
                if revision
                else ReactAdminActionMetadataSource.NOT_REQUIRED
            ),
            idempotency_key=None,
            idempotency_source=ReactAdminActionMetadataSource.GENERATED_CLIENT_STATE,
            request_id=None,
            request_id_source=ReactAdminActionMetadataSource.NOT_REQUIRED,
        ),
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


def _unavailable_result(
    *,
    audit_reference_id: str,
    summary: str,
) -> MembershipMutationResult:
    return MembershipMutationResult(
        status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
        summary=summary,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.WARNING,
            title="Membership state unavailable",
            summary="No persisted row was available for this action.",
        ),
        audit_reference_id=audit_reference_id,
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


def _conflict_result(
    *,
    submitted_revision: str,
    current_revision: str,
    message: str,
    audit_reference_id: str,
) -> MembershipMutationResult:
    return MembershipMutationResult(
        status=AdminMutationStatus.STALE_CONFLICT,
        summary="Membership revision changed before the action completed.",
        stale_conflict=RevisionConflict(
            submitted_revision=submitted_revision,
            current_revision=current_revision,
            message=message,
            reload_href="/admin/app/memberships/bootstrap.json",
        ),
        audit_reference_id=audit_reference_id,
        next_request_effect="No access state changed.",
    )


def _stale_result(
    *,
    submitted_revision: str | None,
    current_revision: str,
) -> MembershipMutationResult:
    return _conflict_result(
        submitted_revision=submitted_revision or "missing-revision",
        current_revision=current_revision,
        message="Reload the directory and retry with the current revision.",
        audit_reference_id="membership-live-stale-conflict",
    )


def _is_stale(submitted_revision: str | None, current_revision: str) -> bool:
    return submitted_revision is not None and submitted_revision != current_revision


def _requested_roles(values: Iterable[str]) -> tuple[RoleCode, ...]:
    roles = tuple(RoleCode(value) for value in values)
    return roles or (RoleCode.TENANT_USER,)


def _optional_uuid(value: str | UUID | None) -> UUID | None:
    if value in (None, ""):
        return None
    if isinstance(value, UUID):
        return value
    return UUID(value)


def _principal_label(principal: PrincipalIdentity | None) -> str:
    if principal is None:
        return "Principal"
    return (
        principal.display_name
        or f"Principal {str(principal.principal_identity_id)[:8]}"
    )


def _tenant_label(tenant_id: UUID | None, tenant_labels: Mapping[UUID, str]) -> str:
    if tenant_id is None:
        return "Platform"
    return tenant_labels.get(tenant_id) or f"Tenant {str(tenant_id)[:8]}"


def _role_label(role_code: str) -> str:
    return {
        "platform_admin": "Platform admin",
        "tenant_admin": "Tenant admin",
        "tenant_user": "Tenant user",
    }.get(role_code, "Tenant role")


def _source_label(source: object) -> str:
    return _value(source).replace("_", " ").title()


def _value(value: object) -> str:
    enum_value = getattr(value, "value", None)
    return str(enum_value if enum_value is not None else value)


def _principal_status(status: object) -> MembershipLifecycleStatus:
    return (
        MembershipLifecycleStatus.SUSPENDED
        if _value(status) == PrincipalIdentityStatus.SUSPENDED.value
        else MembershipLifecycleStatus.ACTIVE
    )


def _membership_status(status: object) -> MembershipLifecycleStatus:
    value = _value(status)
    if value in {item.value for item in MembershipLifecycleStatus}:
        return MembershipLifecycleStatus(value)
    return MembershipLifecycleStatus.UNAVAILABLE


def _grant_status(status: object) -> MembershipLifecycleStatus:
    value = _value(status)
    return {
        RoleGrantStatus.ACTIVE.value: MembershipLifecycleStatus.ACTIVE,
        RoleGrantStatus.REVOKED.value: MembershipLifecycleStatus.REVOKED,
        RoleGrantStatus.EXPIRED.value: MembershipLifecycleStatus.EXPIRED,
    }.get(value, MembershipLifecycleStatus.UNAVAILABLE)


def _invitation_status(status: object) -> MembershipLifecycleStatus:
    value = _value(status)
    if value in {item.value for item in MembershipLifecycleStatus}:
        return MembershipLifecycleStatus(value)
    return MembershipLifecycleStatus.UNAVAILABLE


def _support_override_status(status: object) -> MembershipLifecycleStatus:
    value = _value(status)
    return {
        SupportOverrideStatus.PENDING.value: MembershipLifecycleStatus.PENDING,
        SupportOverrideStatus.APPROVED.value: MembershipLifecycleStatus.ACTIVE,
        SupportOverrideStatus.REJECTED.value: MembershipLifecycleStatus.DENIED,
        SupportOverrideStatus.EXPIRED.value: MembershipLifecycleStatus.EXPIRED,
        SupportOverrideStatus.REVOKED.value: MembershipLifecycleStatus.REVOKED,
    }.get(value, MembershipLifecycleStatus.UNAVAILABLE)


def _last_access_summary(records: Iterable[AccessDecisionRecord]) -> str:
    records_tuple = tuple(records)
    if not records_tuple:
        return "No access decisions recorded."
    latest = max(records_tuple, key=lambda record: record.occurred_at)
    return f"Last decision {_value(latest.decision)} for {latest.requested_action}."


def _required_role_summary(required_roles: list[str]) -> str:
    if not required_roles:
        return "No role requirements recorded."
    return "Required roles: " + ", ".join(sorted(required_roles)[:5])


def _time_label(value: datetime | None) -> str:
    if value is None:
        return "Not recorded"
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _revision(value: datetime | None) -> str:
    if value is None:
        return f"{CURRENT_REVISION_PREFIX}-missing"
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return f"{CURRENT_REVISION_PREFIX}-{int(value.timestamp())}"


def _audit_reference(prefix: str, identifier: UUID) -> str:
    return f"{prefix}-{identifier}"


def _card_status(
    rows: Iterable[object],
    *,
    empty: MembershipLifecycleStatus = MembershipLifecycleStatus.READY,
) -> MembershipLifecycleStatus:
    return MembershipLifecycleStatus.READY if tuple(rows) else empty
