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

document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) {
    return;
  }
  delete form.dataset.dirty;
  form.dataset.submitting = "true";
});

window.addEventListener("beforeunload", (event) => {
  const dirty = document.querySelector(
    "form[data-dirty='true']:not([data-submitting='true'])",
  );
  if (!dirty) {
    return;
  }
  event.preventDefault();
  event.returnValue = "";
});
