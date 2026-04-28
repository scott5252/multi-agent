(() => {
  const scopeForm = document.querySelector(".admin-scope-form");
  if (scopeForm instanceof HTMLFormElement) {
    const select = scopeForm.querySelector("select");
    if (select instanceof HTMLSelectElement) {
      select.addEventListener("change", () => scopeForm.requestSubmit());
    }
  }

  document.querySelectorAll("form[data-confirm-delete]").forEach((form) => {
    if (form instanceof HTMLFormElement) {
      form.addEventListener("submit", (event) => {
        if (!window.confirm("Delete this saved filter?")) {
          event.preventDefault();
        }
      });
    }
  });
})();
