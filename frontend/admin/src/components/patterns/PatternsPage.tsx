import { useEffect, useMemo, useState } from "react";

import { fetchPatternsEnvelope, requestSampleExport } from "../../api/client";
import type {
  AdminPageEnvelope,
  ExportSnapshot,
  SampleActionRequest,
} from "../../api/generated/reactAdminApi";
import { AdminDataTable } from "../data/AdminDataTable";
import { AdminForm } from "../forms/AdminForm";
import { Button, Panel } from "../primitives";
import { CommonState } from "../states/CommonState";
import { useAdminMutation } from "../../hooks/useAdminMutation";

export function PatternsPage({ patternsUrl }: { patternsUrl: string }) {
  const [envelope, setEnvelope] = useState<AdminPageEnvelope | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [exportSnapshot, setExportSnapshot] = useState<ExportSnapshot | null>(null);
  const [values, setValues] = useState<SampleActionRequest>({
    confirmed: false,
    idempotency_key: "sample-idempotency-key",
    outcome: "accepted",
    revision: "sample-revision-current",
    sample_name: "",
  });
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    let alive = true;
    fetchPatternsEnvelope(patternsUrl)
      .then((payload) => {
        if (alive) {
          setEnvelope(payload);
          setExportSnapshot(payload.data.export_snapshot);
          setValues((current) => ({
            ...current,
            idempotency_key: payload.data.form.idempotency_key,
            revision: payload.data.form.revision,
          }));
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(caught instanceof Error ? caught.message : "Patterns unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [patternsUrl]);

  const sampleAction = envelope?.actions.find(
    (action) => action.action_id === "sample-submit",
  );
  const exportAction = envelope?.actions.find(
    (action) => action.action_id === "sample-export",
  );
  const mutation = useAdminMutation(sampleAction?.href ?? "/admin/app/patterns/actions/sample");
  const fields = useMemo(() => envelope?.data.form.fields ?? [], [envelope]);

  function updateValue(field: string, value: string | boolean) {
    setValues((current) => ({ ...current, [field]: value }));
    setDirty(true);
  }

  async function submit() {
    const result = await mutation.submit(values);
    if (result.status === "accepted" || result.status === "replayed") {
      setDirty(false);
    }
  }

  async function previewExport() {
    if (!exportAction) {
      return;
    }
    const snapshot = await requestSampleExport(exportAction.href);
    setExportSnapshot(snapshot);
  }

  if (loadError) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Patterns unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!envelope) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading shared data and form patterns.",
          title: "Loading patterns",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="patterns-page">
      <section className="patterns-hero">
        <p className="eyebrow">Contracts</p>
        <h2>{envelope.title}</h2>
        <p>{envelope.description}</p>
      </section>
      <AdminDataTable
        exportSnapshot={exportSnapshot ?? envelope.data.export_snapshot}
        filters={envelope.filters}
        onExport={previewExport}
        pagination={envelope.pagination}
        records={envelope.data.records}
        sorting={envelope.sorting}
      />
      <Panel className="form-pattern-panel">
        <AdminForm
          dirty={dirty}
          errors={mutation.fieldErrors}
          fields={fields}
          onChange={updateValue}
          onSubmit={submit}
          submitting={mutation.submitting}
          values={values}
        />
        {mutation.error ? <p className="safe-error">{mutation.error}</p> : null}
        {mutation.result ? (
          <section className={`mutation-result ${mutation.result.status}`}>
            <p className="eyebrow">Mutation result</p>
            <h2>{mutation.result.status.replace("_", " ")}</h2>
            <p>{mutation.result.summary}</p>
            {mutation.result.confirmation ? (
              <div className="confirmation-box">
                <strong>{mutation.result.confirmation.title}</strong>
                <p>{mutation.result.confirmation.summary}</p>
                <Button
                  onClick={() => {
                    setValues((current) => ({ ...current, confirmed: true }));
                  }}
                  type="button"
                  variant="secondary"
                >
                  {mutation.result.confirmation.confirm_label}
                </Button>
              </div>
            ) : null}
            {mutation.result.stale_conflict ? (
              <p>{mutation.result.stale_conflict.message}</p>
            ) : null}
            {mutation.result.idempotency ? (
              <p>{mutation.result.idempotency.summary}</p>
            ) : null}
            {mutation.result.audit_reference_id ? (
              <small>{mutation.result.audit_reference_id}</small>
            ) : null}
          </section>
        ) : null}
      </Panel>
      {envelope.state ? <CommonState state={envelope.state} /> : null}
    </div>
  );
}
