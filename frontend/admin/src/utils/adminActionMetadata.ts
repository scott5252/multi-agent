export interface GeneratedActionMetadata {
  idempotencyKey: string;
  requestId: string;
}

export function buildClientRequestId(prefix: string): string {
  return `${safePrefix(prefix)}-${randomSegment()}`;
}

export function buildIdempotencyKey(actionId: string): string {
  return buildClientRequestId(`idem-${actionId}`);
}

export function generatedActionMetadata(actionId: string): GeneratedActionMetadata {
  return {
    idempotencyKey: buildIdempotencyKey(actionId),
    requestId: buildClientRequestId(`req-${actionId}`),
  };
}

export function generatedRevisionMarker(actionId: string): string {
  return buildClientRequestId(`rev-${actionId}`);
}

function safePrefix(prefix: string): string {
  const normalized = prefix
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || "client-request";
}

function randomSegment(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}
