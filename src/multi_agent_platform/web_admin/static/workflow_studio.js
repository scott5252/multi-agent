(() => {
  const modal = document.getElementById("field-help-modal");
  const payload = document.getElementById("field-help-data");

  let metadata = {};
  if (payload) {
    try {
      metadata = JSON.parse(payload.textContent || "{}");
    } catch (error) {
      console.error("Unable to parse workflow field help metadata.", error);
    }
  }
  const help = metadata.field_help || {};
  const title = document.getElementById("field-help-title");
  const explanation = document.getElementById("field-help-explanation");
  const impact = document.getElementById("field-help-impact");
  const example = document.getElementById("field-help-example");
  const validation = document.getElementById("field-help-validation");

  if (modal && title && explanation && impact && example && validation) {
    document.querySelectorAll("[data-help-key]").forEach((button) => {
      button.addEventListener("click", () => {
        const key = button.getAttribute("data-help-key");
        const definition = key ? help[key] : null;
        if (!definition) {
          return;
        }
        title.textContent = definition.title;
        explanation.textContent = definition.explanation;
        impact.textContent = definition.runtime_impact;
        example.textContent = definition.example || "";
        validation.textContent = definition.validation_hint || "";
        modal.showModal();
      });
    });

    document.querySelector("[data-close-help]")?.addEventListener("click", () => {
      modal.close();
    });

    modal.addEventListener("cancel", (event) => {
      event.preventDefault();
      modal.close();
    });
  }

  document.querySelector("[data-create-draft]")?.addEventListener("click", () => {
    window.alert(
      "POST /admin/workflows with scope_type, workflow_kind, slug, display_name, and a document payload."
    );
  });

  const registryFilters = document.querySelector("[data-registry-filters]");
  if (registryFilters) {
    registryFilters.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", () => {
        registryFilters.requestSubmit();
      });
    });
  }

  let dirty = false;
  const dirtyFields = document.querySelectorAll(
    "form:not([data-no-dirty-check]) input, " +
      "form:not([data-no-dirty-check]) textarea, " +
      "form:not([data-no-dirty-check]) select"
  );
  dirtyFields.forEach((field) => {
    if (field.hasAttribute("readonly")) {
      return;
    }
    field.addEventListener("input", () => {
      dirty = true;
    });
  });

  window.addEventListener("beforeunload", (event) => {
    if (!dirty) {
      return;
    }
    event.preventDefault();
    event.returnValue = "";
  });

  document.querySelectorAll("[data-graph-element]").forEach((element) => {
    element.addEventListener("click", () => {
      const fieldPath = element.getAttribute("data-field-path");
      document.querySelectorAll("[data-graph-element]").forEach((candidate) => {
        candidate.classList.toggle("is-selected", candidate === element);
      });
      if (!fieldPath) {
        return;
      }
      const inspector = document.getElementById("document-json");
      if (inspector) {
        inspector.dataset.selectedFieldPath = fieldPath;
      }
    });
  });
})();
