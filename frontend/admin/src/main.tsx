import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "./App";
import "./styles/admin.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Admin root element is missing");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App bootstrapUrl={rootElement.dataset.bootstrapUrl ?? "/admin/app/bootstrap.json"} />
  </React.StrictMode>,
);
