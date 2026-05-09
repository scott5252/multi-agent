import type { WorkflowReferenceOption } from "../../api/generated/reactAdminApi";
import {
  makeUniqueKey,
  promptProfileReferenceKeys,
  replaceCollectionItem,
  type WorkflowEditorDocument,
  type WorkflowPromptProfileReferenceItem,
  type WorkflowRoleItem,
} from "./workflowDocumentEditor";

export type BindingKind = "prompt" | "profile";

export interface BindingReadiness {
  missingPrompts: number;
  missingProfiles: number;
  readyRoles: number;
  totalRoles: number;
}

export function summarizeBindingReadiness(
  document: WorkflowEditorDocument,
): BindingReadiness {
  const totalRoles = document.roles.length;
  let missingPrompts = 0;
  let missingProfiles = 0;
  let readyRoles = 0;
  document.roles.forEach((role) => {
    const hasPrompt = (role.prompt_reference_keys ?? []).length > 0;
    const hasProfile = Boolean(role.profile_reference_key);
    if (!hasPrompt) {
      missingPrompts += 1;
    }
    if (!hasProfile) {
      missingProfiles += 1;
    }
    if (hasPrompt && hasProfile) {
      readyRoles += 1;
    }
  });
  return { missingProfiles, missingPrompts, readyRoles, totalRoles };
}

export function bindingStatusForRole(role: WorkflowRoleItem): string {
  const hasPrompt = (role.prompt_reference_keys ?? []).length > 0;
  const hasProfile = Boolean(role.profile_reference_key);
  if (hasPrompt && hasProfile) {
    return "ready";
  }
  if (hasPrompt || hasProfile) {
    return "warning";
  }
  return "blocked";
}

export function safeCatalogLabel(
  option: WorkflowReferenceOption | null | undefined,
): string {
  if (!option) {
    return "No authorized record selected";
  }
  return `${option.label}${option.version_label ? ` ${option.version_label}` : ""}`;
}

export function buildReferenceFromCatalog({
  kind,
  option,
  role,
}: {
  kind: BindingKind;
  option: WorkflowReferenceOption;
  role: WorkflowRoleItem;
}): WorkflowPromptProfileReferenceItem {
  const referenceKey = safeReferenceKey(
    option.reference_id || `${role.role_key}-${kind}`,
  );
  return {
    agent_kind: role.role_kind ?? "agent",
    agent_key: role.role_key,
    prompt_reference_version_ids: [],
    prompt_version_ids: [],
    readiness_status:
      option.readiness_status === "ready" ? "ready" : option.readiness_status,
    reference_key: referenceKey,
    resolution_digest: `${kind}:${referenceKey}`,
    role_key: role.role_key,
    source_scope: option.tenant_eligible ? "tenant" : "platform",
  };
}

export function buildGeneratedReference({
  kind,
  label,
  role,
  usedKeys,
}: {
  kind: BindingKind;
  label: string;
  role: WorkflowRoleItem;
  usedKeys: Iterable<string>;
}): WorkflowPromptProfileReferenceItem {
  const referenceKey = makeUniqueKey(
    `${role.role_key}-${kind}`,
    usedKeys,
  );
  return {
    agent_kind: role.role_kind ?? "agent",
    agent_key: role.role_key,
    prompt_reference_version_ids: [],
    prompt_version_ids: [],
    readiness_status: "ready",
    reference_key: referenceKey,
    resolution_digest: `${kind}:${safeReferenceKey(label)}`,
    role_key: role.role_key,
    source_scope: "tenant",
  };
}

export function bindReferenceToRole({
  document,
  kind,
  reference,
  roleKey,
}: {
  document: WorkflowEditorDocument;
  kind: BindingKind;
  reference: WorkflowPromptProfileReferenceItem;
  roleKey: string;
}): WorkflowEditorDocument {
  const referenceIndex = document.prompt_profile_references.findIndex(
    (item) => item.reference_key === reference.reference_key,
  );
  const prompt_profile_references =
    referenceIndex >= 0
      ? replaceCollectionItem(
          document.prompt_profile_references,
          referenceIndex,
          reference,
        )
      : [...document.prompt_profile_references, reference];
  const roles = document.roles.map((role) => {
    if (role.role_key !== roleKey) {
      return role;
    }
    if (kind === "prompt") {
      const existing = new Set(role.prompt_reference_keys ?? []);
      existing.add(reference.reference_key);
      return {
        ...role,
        prompt_reference_keys: Array.from(existing),
      };
    }
    return {
      ...role,
      profile_reference_key: reference.reference_key,
    };
  });
  return {
    ...document,
    prompt_profile_references,
    roles,
  };
}

export function createGeneratedRoleReference({
  document,
  kind,
  label,
  role,
}: {
  document: WorkflowEditorDocument;
  kind: BindingKind;
  label: string;
  role: WorkflowRoleItem;
}): WorkflowEditorDocument {
  return bindReferenceToRole({
    document,
    kind,
    reference: buildGeneratedReference({
      kind,
      label,
      role,
      usedKeys: promptProfileReferenceKeys(document),
    }),
    roleKey: role.role_key,
  });
}

function safeReferenceKey(value: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || "prompt-profile-reference";
}
