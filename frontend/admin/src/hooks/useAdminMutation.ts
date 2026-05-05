import { useState } from "react";

import { submitSampleAction } from "../api/client";
import type {
  MutationResult,
  SampleActionRequest,
  ValidationFieldError,
} from "../api/generated/reactAdminApi";

export function errorsByField(
  errors: ValidationFieldError[],
): Record<string, ValidationFieldError> {
  return Object.fromEntries(errors.map((error) => [error.field, error]));
}

export function useAdminMutation(actionUrl: string) {
  const [result, setResult] = useState<MutationResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(payload: SampleActionRequest) {
    setSubmitting(true);
    setError(null);
    try {
      const nextResult = await submitSampleAction(actionUrl, payload);
      setResult(nextResult);
      return nextResult;
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Action unavailable";
      setError(message);
      throw caught;
    } finally {
      setSubmitting(false);
    }
  }

  return {
    error,
    fieldErrors: errorsByField(result?.field_errors ?? []),
    result,
    submit,
    submitting,
  };
}
