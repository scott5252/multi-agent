import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import { useEffect, useRef, useState } from "react";

type Tone = "neutral" | "info" | "success" | "warning" | "critical";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
}

export function Button({
  className = "",
  variant = "secondary",
  ...props
}: ButtonProps) {
  return <button className={`ui-button ${variant} ${className}`} {...props} />;
}

interface IconButtonProps extends ButtonProps {
  label: string;
  icon: ReactNode;
}

export function IconButton({ label, icon, ...props }: IconButtonProps) {
  return (
    <Button aria-label={label} title={label} {...props}>
      {icon}
      <VisuallyHidden>{label}</VisuallyHidden>
    </Button>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return <span className={`ui-badge ${tone}`}>{children}</span>;
}

export function Panel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`ui-panel ${className}`}>{children}</section>;
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className="ui-input" {...props} />;
}

export function VisuallyHidden({ children }: { children: ReactNode }) {
  return <span className="visually-hidden">{children}</span>;
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: Array<{ id: string; label: string }>;
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="ui-tabs" role="tablist">
      {tabs.map((tab) => (
        <button
          aria-selected={tab.id === active}
          className="ui-tab"
          key={tab.id}
          onClick={() => onChange(tab.id)}
          role="tab"
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export function Drawer({
  children,
  labelledBy,
  onClose,
  open,
}: {
  children: ReactNode;
  labelledBy: string;
  onClose: () => void;
  open: boolean;
}) {
  return (
    <div className={open ? "drawer open" : "drawer"} hidden={!open}>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside
        aria-labelledby={labelledBy}
        aria-modal="true"
        className="drawer-panel"
        role="dialog"
      >
        {children}
      </aside>
    </div>
  );
}

export function Modal({
  children,
  labelledBy,
  onClose,
  open,
}: {
  children: ReactNode;
  labelledBy: string;
  onClose: () => void;
  open: boolean;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (open) {
      ref.current?.focus();
    }
  }, [open]);
  if (!open) {
    return null;
  }
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        aria-labelledby={labelledBy}
        aria-modal="true"
        className="modal-panel"
        onClick={(event) => event.stopPropagation()}
        ref={ref}
        role="dialog"
        tabIndex={-1}
      >
        {children}
      </div>
    </div>
  );
}

export function ToastRegion({
  messages,
}: {
  messages: Array<{ id: string; tone: Tone; title: string; summary: string }>;
}) {
  return (
    <section aria-label="Notifications" aria-live="polite" className="toasts">
      {messages.map((message) => (
        <article className={`toast ${message.tone}`} key={message.id}>
          <strong>{message.title}</strong>
          <p>{message.summary}</p>
        </article>
      ))}
    </section>
  );
}

export function useDisclosure(initial = false) {
  const [open, setOpen] = useState(initial);
  return {
    close: () => setOpen(false),
    open,
    openPanel: () => setOpen(true),
    setOpen,
    toggle: () => setOpen((current) => !current),
  };
}
