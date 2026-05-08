import type { ChangeEvent, FormEvent } from "react";

import type {
  FormFieldDescriptor,
  ValidationFieldError,
} from "../../api/generated/reactAdminApi";
import { Button, TextInput } from "../primitives";

export type AdminFormValues = Record<string, string | boolean>;

interface AdminFormProps {
  dirty: boolean;
  errors: Record<string, ValidationFieldError>;
  fields: FormFieldDescriptor[];
  onChange: (field: string, value: string | boolean) => void;
  onSubmit: () => void;
  submitting: boolean;
  values: AdminFormValues;
}

export function AdminForm({
  dirty,
  errors,
  fields,
  onChange,
  onSubmit,
  submitting,
  values,
}: AdminFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="admin-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <div>
          <p className="eyebrow">Forms</p>
          <h2>Sample action</h2>
        </div>
        {dirty ? <span className="dirty-state">Unsaved changes</span> : null}
      </div>
      {fields.map((field) => (
        <label className="form-field" key={field.field}>
          <span>
            {field.label}
            {field.required ? <strong aria-label="required"> *</strong> : null}
          </span>
          <TextInput
            aria-describedby={`${field.field}-help ${field.field}-error`}
            aria-invalid={Boolean(errors[field.field])}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              onChange(field.field, event.currentTarget.value)
            }
            value={String(values[field.field] ?? "")}
          />
          {field.help_text ? (
            <small id={`${field.field}-help`}>{field.help_text}</small>
          ) : null}
          {errors[field.field] ? (
            <small className="field-error" id={`${field.field}-error`}>
              {errors[field.field].message}
            </small>
          ) : null}
        </label>
      ))}
      <label className="form-field checkbox-field">
        <input
          checked={Boolean(values.confirmed)}
          onChange={(event) => onChange("confirmed", event.currentTarget.checked)}
          type="checkbox"
        />
        Confirm sample action
      </label>
      <div className="form-actions">
        <Button disabled={submitting} type="submit" variant="primary">
          {submitting ? "Submitting" : "Preview result"}
        </Button>
      </div>
    </form>
  );
}
