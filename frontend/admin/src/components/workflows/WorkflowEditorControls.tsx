import type { ReactNode } from "react";
import { ArrowDown, ArrowUp, Copy, Trash2 } from "lucide-react";

import { Badge, Button, IconButton } from "../primitives";

interface EditorPanelProps {
  badge?: ReactNode;
  children: ReactNode;
  id: string;
  summary: string;
  title: string;
}

export function EditorPanel({
  badge,
  children,
  id,
  summary,
  title,
}: EditorPanelProps) {
  return (
    <section className="workflow-editor-panel" id={id} aria-labelledby={`${id}-title`}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Editor</p>
          <h2 id={`${id}-title`}>{title}</h2>
          <p className="table-footer">{summary}</p>
        </div>
        {badge}
      </div>
      {children}
    </section>
  );
}

export function EditorToolbar({ children }: { children: ReactNode }) {
  return <div className="workflow-editor-toolbar">{children}</div>;
}

export function EditorItem({
  children,
  title,
  badge,
}: {
  badge?: ReactNode;
  children: ReactNode;
  title: string;
}) {
  return (
    <article className="workflow-editor-item">
      <div className="card-heading">
        <strong>{title}</strong>
        {badge}
      </div>
      {children}
    </article>
  );
}

export function EditorGrid({ children }: { children: ReactNode }) {
  return <div className="workflow-editor-grid">{children}</div>;
}

export function EditorField({
  children,
  label,
}: {
  children: ReactNode;
  label: string;
}) {
  return (
    <label className="form-field">
      <span className="label">{label}</span>
      {children}
    </label>
  );
}

export function EmptyEditorState({ children }: { children: ReactNode }) {
  return <p className="workflow-editor-empty">{children}</p>;
}

export function DependencyWarnings({ warnings }: { warnings: string[] }) {
  if (warnings.length === 0) {
    return null;
  }
  return (
    <div className="dependency-warning" role="status">
      <Badge tone="warning">References</Badge>
      <ul>
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </div>
  );
}

export function ItemActionRow({
  canMoveDown,
  canMoveUp,
  onDuplicate,
  onMoveDown,
  onMoveUp,
  onRemove,
}: {
  canMoveDown: boolean;
  canMoveUp: boolean;
  onDuplicate: () => void;
  onMoveDown: () => void;
  onMoveUp: () => void;
  onRemove: () => void;
}) {
  return (
    <div className="workflow-item-actions">
      <IconButton
        disabled={!canMoveUp}
        icon={<ArrowUp aria-hidden="true" size={16} />}
        label="Move up"
        onClick={onMoveUp}
        type="button"
        variant="ghost"
      />
      <IconButton
        disabled={!canMoveDown}
        icon={<ArrowDown aria-hidden="true" size={16} />}
        label="Move down"
        onClick={onMoveDown}
        type="button"
        variant="ghost"
      />
      <IconButton
        icon={<Copy aria-hidden="true" size={16} />}
        label="Duplicate"
        onClick={onDuplicate}
        type="button"
        variant="ghost"
      />
      <IconButton
        icon={<Trash2 aria-hidden="true" size={16} />}
        label="Delete"
        onClick={onRemove}
        type="button"
        variant="danger"
      />
    </div>
  );
}

export function AddButton({
  children,
  onClick,
}: {
  children: ReactNode;
  onClick: () => void;
}) {
  return (
    <Button onClick={onClick} type="button" variant="secondary">
      {children}
    </Button>
  );
}
