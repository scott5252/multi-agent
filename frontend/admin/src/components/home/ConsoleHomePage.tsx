import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  Bell,
  Boxes,
  CircleGauge,
  ClipboardCheck,
  Coins,
  KeyRound,
  Network,
  RefreshCw,
  Route,
  ShieldCheck,
  UserCog,
  Wrench,
} from "lucide-react";

import { fetchConsoleHome } from "../../api/client";
import type {
  ConsoleHomeEnvelope,
  ConsoleHomeMetric,
  ConsoleHomeQuickAction,
  ConsoleHomeWorkspace,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import { CommonState } from "../states/CommonState";

export function ConsoleHomePage({
  homeUrl = withSearch("/admin/app/home.json"),
}: {
  homeUrl?: string;
}) {
  const [home, setHome] = useState<ConsoleHomeEnvelope | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchConsoleHome(homeUrl)
      .then((payload) => {
        if (alive) {
          setHome(payload);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Console Home unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [homeUrl]);

  async function refresh() {
    const payload = await fetchConsoleHome(homeUrl);
    setHome(payload);
    setLoadError(null);
  }

  if (loadError && !home) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Console Home unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!home) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading scope, workspaces, and current notices.",
          title: "Loading Console Home",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="console-home">
      <section className="home-hero" aria-labelledby="console-home-title">
        <div>
          <p className="eyebrow">{home.scope.label}</p>
          <h1 id="console-home-title">{home.title}</h1>
          <p>{home.description}</p>
        </div>
        <div className="home-hero-side">
          <Button className="icon-text-button" onClick={() => void refresh()} type="button">
            <RefreshCw aria-hidden="true" size={16} />
            Refresh
          </Button>
          <small>Updated {formatDateTime(home.updated_at)}</small>
        </div>
        <dl className="home-metric-grid" aria-label="Console Home summary">
          {home.metrics.map((metric) => (
            <MetricItem key={metric.metric_id} metric={metric} />
          ))}
        </dl>
      </section>

      {loadError ? <p className="safe-error">{loadError}</p> : null}

      <section className="home-section" aria-labelledby="home-attention-title">
        <div className="home-section-heading">
          <div>
            <p className="eyebrow">Attention</p>
            <h2 id="home-attention-title">Current notices</h2>
          </div>
          <Bell aria-hidden="true" size={20} />
        </div>
        <div className="home-attention-list">
          {home.attention_items.map((item) => (
            <article className="home-attention-item" key={item.item_id}>
              <Badge tone={item.tone}>{item.title}</Badge>
              <p>{item.summary}</p>
              {item.href ? (
                <a className="secondary-link" href={item.href}>
                  Open
                  <ArrowRight aria-hidden="true" size={14} />
                </a>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      <section className="home-section" aria-labelledby="home-actions-title">
        <div className="home-section-heading">
          <div>
            <p className="eyebrow">Quick Actions</p>
            <h2 id="home-actions-title">Start here</h2>
          </div>
          <CircleGauge aria-hidden="true" size={20} />
        </div>
        <div className="home-action-grid">
          {home.quick_actions.map((action) => (
            <QuickAction key={action.action_id} action={action} />
          ))}
        </div>
      </section>

      <section className="home-section" aria-labelledby="home-workspaces-title">
        <div className="home-section-heading">
          <div>
            <p className="eyebrow">Workspaces</p>
            <h2 id="home-workspaces-title">Authorized destinations</h2>
          </div>
          <Boxes aria-hidden="true" size={20} />
        </div>
        <div className="home-workspace-grid">
          {home.workspaces.map((workspace) => (
            <WorkspaceItem key={workspace.workspace_id} workspace={workspace} />
          ))}
        </div>
      </section>
    </div>
  );
}

function MetricItem({ metric }: { metric: ConsoleHomeMetric }) {
  return (
    <div>
      <dt>{metric.label}</dt>
      <dd>{metric.value}</dd>
      {metric.summary ? <p>{metric.summary}</p> : null}
    </div>
  );
}

function QuickAction({ action }: { action: ConsoleHomeQuickAction }) {
  const Icon = iconForAction(action.action_id);
  return (
    <a className="home-action" href={action.href}>
      <span className="home-action-icon">
        <Icon aria-hidden="true" size={18} />
      </span>
      <span>
        <strong>{action.label}</strong>
        <small>{action.summary}</small>
      </span>
      <ArrowRight aria-hidden="true" size={16} />
    </a>
  );
}

function WorkspaceItem({ workspace }: { workspace: ConsoleHomeWorkspace }) {
  const Icon = iconForAction(workspace.workspace_id);
  return (
    <article className="home-workspace">
      <div className="home-workspace-top">
        <span className="home-action-icon">
          <Icon aria-hidden="true" size={18} />
        </span>
        <Badge tone={workspace.status_tone}>{workspace.status_label}</Badge>
      </div>
      <h3>{workspace.label}</h3>
      <p>{workspace.summary}</p>
      <a className="secondary-link" href={workspace.href}>
        Open {workspace.label}
        <ArrowRight aria-hidden="true" size={14} />
      </a>
    </article>
  );
}

function iconForAction(actionId: string) {
  if (actionId.includes("workflow")) {
    return Route;
  }
  if (
    actionId.includes("operation") ||
    actionId.includes("run") ||
    actionId.includes("reliability")
  ) {
    return Activity;
  }
  if (
    actionId.includes("provider") ||
    actionId.includes("routing") ||
    actionId.includes("config")
  ) {
    return Network;
  }
  if (actionId.includes("skill")) {
    return Wrench;
  }
  if (actionId.includes("test")) {
    return ClipboardCheck;
  }
  if (actionId.includes("membership")) {
    return UserCog;
  }
  if (actionId.includes("usage")) {
    return Coins;
  }
  if (actionId.includes("telegram") || actionId.includes("briefing")) {
    return Bell;
  }
  if (actionId.includes("prompt") || actionId.includes("profile")) {
    return KeyRound;
  }
  return ShieldCheck;
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function withSearch(url: string): string {
  if (!window.location.search || url.includes("?")) {
    return url;
  }
  return `${url}${window.location.search}`;
}
