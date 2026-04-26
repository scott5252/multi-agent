(function () {
  const forms = document.querySelectorAll("[data-model-skill-preview]");
  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const output = form.querySelector("[data-preview-output]");
      if (!output) {
        return;
      }
      const payload = {};
      new FormData(form).forEach((value, key) => {
        if (value !== "") {
          payload[key] = value;
        }
      });
      output.textContent = "Previewing...";
      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const body = await response.json();
        output.textContent = JSON.stringify(body, null, 2);
      } catch (error) {
        output.textContent = "Preview failed";
      }
    });
  });
})();

