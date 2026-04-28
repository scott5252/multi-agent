(function () {
  const forms = document.querySelectorAll("[data-provider-action]");
  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const output = form.querySelector("[data-action-output]");
      const button = form.querySelector("button");
      if (button) {
        button.disabled = true;
      }
      try {
        const response = await fetch(form.action, { method: "POST" });
        const body = await response.text();
        if (output) {
          output.textContent = body;
        }
      } finally {
        if (button) {
          button.disabled = false;
        }
      }
    });
  });

  const addModel = document.querySelector("[data-add-model-row]");
  const modelRows = document.querySelector("[data-model-rows]");
  if (addModel && modelRows) {
    addModel.addEventListener("click", () => {
      modelRows.value = `${modelRows.value}${modelRows.value ? ", " : ""}model-id`;
      modelRows.focus();
    });
  }
})();
