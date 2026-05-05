from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_membership_react import (
    MembershipInvitationSaveRequest,
    MembershipLifecycleStatus,
    MembershipMutationResult,
    MembershipSummaryCard,
    RawIdentifierDetail,
    UserDirectoryEntry,
)
from multi_agent_platform.api.schemas.admin_patterns import AdminMutationStatus


def test_membership_summary_rejects_unsafe_markers() -> None:
    with pytest.raises(ValidationError):
        MembershipSummaryCard(
            card_id="unsafe",
            label="Directory",
            value="qa034-secret-value",
            status=MembershipLifecycleStatus.READY,
            summary="Unsafe fixture",
        )


def test_directory_entry_masks_identity_and_gates_raw_detail() -> None:
    entry = UserDirectoryEntry(
        principal_identity_id="principal-qa034-maya",
        display_name="Maya Chen",
        masked_email="m***@example.test",
        safe_subject_suffix="subject ...maya",
        principal_status=MembershipLifecycleStatus.ACTIVE,
        tenant_memberships=(),
        role_summaries=(),
        last_access_summary="Allowed today from current role grants.",
        raw_identifier_detail=RawIdentifierDetail(
            authorized=True,
            principal_identity_id="principal-qa034-maya",
            external_subject="auth0-subject-suffix-maya",
            invitation_id=None,
            copy_label="Copy support identifiers",
            reason="Platform support review is authorized.",
        ),
        authorized_actions=(),
    )

    assert entry.masked_email == "m***@example.test"
    assert entry.raw_identifier_detail is not None
    assert entry.raw_identifier_detail.authorized is True


def test_invitation_request_normalizes_email_without_extra_dependency() -> None:
    request = MembershipInvitationSaveRequest(
        email=" Invite.Replay@Example.Test ",
        requested_roles=("tenant_user",),
        idempotency_key="invite-replay-key",
    )

    assert request.email == "invite.replay@example.test"


def test_mutation_result_carries_audit_and_next_request_effect() -> None:
    result = MembershipMutationResult(
        status=AdminMutationStatus.REPLAYED,
        summary="Invitation replayed with original audit evidence.",
        audit_reference_id="audit-membership-qa034-invite-replayed",
        next_request_effect="Requested roles apply after the next protected request.",
        idempotency_replay=True,
    )

    assert result.audit_reference_id == "audit-membership-qa034-invite-replayed"
    assert result.idempotency_replay is True
