import type {
  ExportSnapshot,
  FilterProfile,
  FormFieldDescriptor,
  MutationResult,
  PaginationState,
  SortingState,
} from "../api/generated/reactAdminApi";

interface PatternsEnvelopeFixture {
  [key: string]: unknown;
  data: {
    [key: string]: unknown;
    export_snapshot: ExportSnapshot;
    form: {
      [key: string]: unknown;
      fields: FormFieldDescriptor[];
    };
    records: Array<{
      [key: string]: unknown;
      name: string;
      owner_scope: string;
      record_id: string;
      status: string;
      updated_label: string;
    }>;
  };
  filters: FilterProfile;
  pagination: PaginationState;
  sorting: SortingState;
}

export const patternsEnvelopeFixture: PatternsEnvelopeFixture = {
  actions: [
    {
      action_id: "sample-submit",
      action_token: null,
      confirmation: null,
      disabled_reason: null,
      enabled: true,
      href: "/admin/app/patterns/actions/sample",
      label: "Preview form result",
      method: "post",
      requires_confirmation: false,
      requires_idempotency_key: true,
      variant: "primary",
    },
    {
      action_id: "sample-export",
      action_token: null,
      confirmation: null,
      disabled_reason: null,
      enabled: true,
      href: "/admin/app/patterns/export",
      label: "Preview export",
      method: "post",
      requires_confirmation: false,
      requires_idempotency_key: false,
      variant: "secondary",
    },
  ],
  data: {
    details: [],
    export_snapshot: {
      artifact_reference_id: "artifact-ref-qa028-tenant",
      audit_reference_id: "audit-export-qa028-tenant",
      export_id: "sample-export-tenant",
      expires_at: null,
      progress_label: "Complete",
      status: "complete",
      summary: "Sample export snapshot is ready as a safe artifact reference.",
    },
    form: {
      default_values: {
        confirmed: false,
        outcome: "accepted",
        sample_name: "",
      },
      fields: [
        {
          field: "sample_name",
          help_text: "Use a harmless label for the sample action.",
          input_type: "text",
          label: "Sample name",
          required: true,
        },
        {
          field: "outcome",
          help_text: "Choose accepted, validation, stale, replay, or confirmation.",
          input_type: "text",
          label: "Outcome",
          required: true,
        },
      ],
      idempotency_key: "sample-idempotency-key",
      revision: "sample-revision-current",
    },
    records: [
      {
        name: "Workflow readiness review",
        owner_scope: "Acme",
        record_id: "sample-ready",
        revision: "sample-revision-current",
        status: "ready",
        updated_label: "Updated today",
      },
    ],
  },
  description: "Harmless sample contracts for future admin forms.",
  evidence: [],
  filters: {
    active_chips: [],
    criteria: [
      {
        key: "status",
        label: "Status",
        operator: "equals",
        options: [{ label: "Ready", value: "ready" }],
      },
    ],
    profile_id: "patterns-sample-filters",
    saved_filters: [],
  },
  page_id: "react-admin-patterns",
  pagination: {
    next_cursor: null,
    page_size: 10,
    page_size_options: [10, 25, 50],
    previous_cursor: null,
    total_items: 1,
    total_known: true,
  },
  refresh: { interval_seconds: null, mode: "manual" },
  scope: {
    label: "Acme",
    scope_type: "tenant",
    tenant_id: "11111111-1111-1111-1111-111111111111",
  },
  sorting: {
    active: { direction: "asc", key: "name", label: "Name" },
    allowed: [{ direction: "asc", key: "name", label: "Name" }],
  },
  state: null,
  title: "Forms and data patterns",
};

export const validationResultFixture: MutationResult = {
  audit_reference_id: "audit-react-patterns-tenant",
  confirmation: null,
  field_errors: [
    {
      code: "required",
      field: "sample_name",
      label: "Sample name",
      message: "Enter a sample name.",
    },
  ],
  idempotency: null,
  next_action: null,
  stale_conflict: null,
  status: "validation_error",
  summary: "Review the highlighted fields before submitting again.",
  toast: null,
};
