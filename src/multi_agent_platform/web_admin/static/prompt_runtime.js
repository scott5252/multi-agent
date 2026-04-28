document.addEventListener("input", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const form = target.closest("form");
  if (form) {
    form.dataset.dirty = "true";
  }
});

window.addEventListener("beforeunload", (event) => {
  const dirty = document.querySelector("form[data-dirty='true']");
  if (!dirty) {
    return;
  }
  event.preventDefault();
});
