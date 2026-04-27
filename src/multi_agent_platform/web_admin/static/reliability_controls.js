(() => {
  const panels = document.querySelectorAll("[data-reliability-panel]");

  for (const panel of panels) {
    panel.dataset.state = "ready";
  }
})();
