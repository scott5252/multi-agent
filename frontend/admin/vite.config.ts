import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/admin/static/react/",
  plugins: [react()],
  build: {
    outDir: "../../src/multi_agent_platform/web_admin/static/react",
    emptyOutDir: true,
    manifest: "manifest.json",
    rollupOptions: {
      input: "src/main.tsx",
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/admin": "http://127.0.0.1:8000",
      "/auth": "http://127.0.0.1:8000",
    },
  },
});
