(() => {
  const body = document.querySelector("[data-run-id]");
  if (!body) return;
  const runId = body.getAttribute("data-run-id");
  const endpoint = `/runs/${runId}/events`;
  if (!window.EventSource) return;
  const source = new EventSource(endpoint);
  source.addEventListener("run_completed", () => source.close());
  source.addEventListener("run_failed", () => source.close());
  source.addEventListener("run_canceled", () => source.close());
})();

