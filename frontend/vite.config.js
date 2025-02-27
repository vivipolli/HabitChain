import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { nodePolyfills } from "vite-plugin-node-polyfills";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      // Para incluir polyfills específicos
      include: ["process", "stream", "util", "buffer", "events"],
      // Ou para incluir todos os polyfills
      // include: true,
      globals: {
        process: true,
        Buffer: true,
      },
    }),
  ],
  define: {
    "process.env": {},
    global: "globalThis",
  },
  resolve: {
    alias: {
      // Evite usar path relativos como 'process/'
      process: "process/browser",
      stream: "stream-browserify",
      util: "util",
    },
  },
});
