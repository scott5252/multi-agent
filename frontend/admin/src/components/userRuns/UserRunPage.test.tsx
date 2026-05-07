import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { UserRunPage } from "./UserRunPage";

const runId = "00000000-0000-0000-0000-000000000046";
const promptId = "11111111-1111-1111-1111-111111111046";
const artifactId = "22222222-2222-2222-2222-222222222046";

const status = {
  artifact_availability: "available",
  latest_timeline_cursor: "2",
  permitted_actions: ["cancel"],
  progress_summary: "Collecting safe workflow context.",
  result_availability: "available",
  run_id: runId,
  state: "waiting-for-input",
  subscribed: false,
  terminal_outcome: "none",
  trace_id: "trace-qa046",
  waiting_prompt: {
    allowed_actions: ["approve", "reject", "resume", "cancel"],
    context: { safe_summary: "masked context only" },
    deadline_at: null,
    prompt_id: promptId,
    prompt_type: "approval",
    prompt_version: 1,
    summary: "Review safe approval request.",
  },
};

const timeline = {
  items: [
    {
      event_id: "33333333-3333-3333-3333-333333333046",
      event_type: "run_queued",
      occurred_at: "2026-05-07T12:00:00Z",
      sequence: 1,
      severity: "info",
      state: "queued",
      summary: "Run accepted through channel facade.",
      trace_id: "trace-qa046",
    },
    {
      event_id: "44444444-4444-4444-4444-444444444046",
      event_type: "waiting_prompt_created",
      occurred_at: "2026-05-07T12:01:00Z",
      sequence: 2,
      severity: "warning",
      state: "waiting-for-input",
      summary: "Safe approval needed.",
      trace_id: "trace-qa046",
    },
  ],
  next_cursor: null,
};

const result = {
  availability: "available",
  run_id: runId,
  state: "completed",
  structured_result: { safe_summary: "ready" },
  summary: "Safe result summary.",
  trace_id: "trace-qa046",
};

const artifacts = {
  items: [
    {
      artifact_id: artifactId,
      download_url_available: true,
      name: "safe-summary.json",
      size_bytes: 2048,
      status: "ready",
      user_facing_type: "summary",
    },
  ],
  run_id: runId,
};

describe("UserRunPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe run status, timeline, result, artifacts, and prompt actions", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: true, json: async () => status })
        .mockResolvedValueOnce({ ok: true, json: async () => timeline })
        .mockResolvedValueOnce({ ok: true, json: async () => result })
        .mockResolvedValueOnce({ ok: true, json: async () => artifacts }),
    );

    render(<UserRunPage runId={runId} />);

    await screen.findByRole("heading", { name: "Run workspace" });
    expect(screen.getByText("Collecting safe workflow context.")).toBeInTheDocument();
    expect(screen.getByText("Safe approval needed.")).toBeInTheDocument();
    expect(screen.getByText("Safe result summary.")).toBeInTheDocument();
    expect(screen.getByText("safe-summary.json")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve" })).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt|raw payload|callback secret/i)).not.toBeInTheDocument();
  });

  it("starts a run and moves the browser to the React run detail route", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          events_url: `/runs/${runId}/events`,
          run_id: runId,
          state: "queued",
          status_url: `/runs/${runId}/status`,
          timeline_url: `/runs/${runId}/timeline`,
          trace_id: "trace-qa046-start",
        }),
      });
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/admin/app/channels/runs");

    render(<UserRunPage />);

    await userEvent.click(screen.getByRole("button", { name: "Start Run" }));

    await waitFor(() => {
      expect(window.location.pathname).toBe(`/admin/app/channels/runs/${runId}`);
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runs",
      expect.objectContaining({
        headers: expect.objectContaining({ "X-Idempotency-Key": "react-run-start-daily-briefing-demo" }),
        method: "POST",
      }),
    );
  });

  it("keeps action results safe when subscribing and creating artifact grants", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => status })
      .mockResolvedValueOnce({ ok: true, json: async () => timeline })
      .mockResolvedValueOnce({ ok: true, json: async () => result })
      .mockResolvedValueOnce({ ok: true, json: async () => artifacts })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: "active",
          subscription_id: "55555555-5555-5555-5555-555555555046",
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => status })
      .mockResolvedValueOnce({ ok: true, json: async () => timeline })
      .mockResolvedValueOnce({ ok: true, json: async () => result })
      .mockResolvedValueOnce({ ok: true, json: async () => artifacts })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          artifact_id: artifactId,
          download_url: "https://storage.example.test/signed",
          expires_at: "2026-05-07T12:15:00Z",
          trace_id: "trace-qa046-grant",
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<UserRunPage runId={runId} />);

    await screen.findByText("safe-summary.json");
    await userEvent.click(screen.getByRole("button", { name: "Subscribe" }));
    await screen.findByText("Status active");
    await userEvent.click(screen.getByRole("button", { name: "Create Grant" }));
    await screen.findByText("Artifact grant created until 2026-05-07T12:15:00Z");
    expect(screen.queryByText("https://storage.example.test/signed")).not.toBeInTheDocument();
  });
});
