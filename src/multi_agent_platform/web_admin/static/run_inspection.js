const runId = document.body.dataset.runId;

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    return null;
  }
  return response.json();
}

function addItems(selector, items, formatter) {
  const list = document.querySelector(selector);
  if (!list) {
    return;
  }
  list.innerHTML = "";
  for (const item of items) {
    const row = document.createElement("li");
    row.textContent = formatter(item);
    list.appendChild(row);
  }
}

async function hydrateAuditRun() {
  if (!runId) {
    return;
  }
  const timeline = await loadJson(`/admin/runs/${runId}/timeline`);
  if (timeline) {
    addItems(
      "[data-audit-timeline]",
      timeline.events || [],
      (event) => `${event.sequence}. ${event.event_category}: ${event.safe_summary}`,
    );
  }
  const replay = await loadJson(`/admin/runs/${runId}/replay`);
  if (replay) {
    addItems(
      "[data-audit-replay]",
      replay.events || [],
      (event) => `${event.sequence}. ${event.event_category} -> ${event.status_after}`,
    );
  }
}

document.querySelectorAll("[data-export-run]").forEach((button) => {
  button.addEventListener("click", async () => {
    const targetRunId = button.getAttribute("data-export-run");
    const response = await fetch(`/admin/runs/${targetRunId}/exports`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        recipient_scope: "tenant_auditor",
        lineage_scope: "authorized_children",
        included_sections: ["timeline", "trace", "lineage", "bundle"],
        excluded_sections: [],
        reason: "admin review",
      }),
    });
    button.textContent = response.ok ? "Export Requested" : "Export Failed";
  });
});

hydrateAuditRun();
