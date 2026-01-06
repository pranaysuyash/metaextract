import { defineConfig, type UserConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";
import { metaImagesPlugin } from "./vite-plugin-meta-images";

function buildDevCsp(): string {
  // Dev CSP must allow Vite HMR + React refresh + Google Fonts.
  // Intentionally permissive for localhost only.
  return [
    "default-src 'self' blob: data:",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:",
    "script-src-elem 'self' 'unsafe-inline' 'unsafe-eval' blob:",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: blob: https:",
    "font-src 'self' data: https://fonts.gstatic.com",
    "connect-src 'self' ws: wss: http://localhost:* http://127.0.0.1:*",
    "worker-src 'self' blob:",
    "frame-ancestors 'none'",
  ].join("; ");
}

export default defineConfig(async ({ mode }): Promise<UserConfig> => {
  const plugins = [
    react(),
    runtimeErrorOverlay(),
    tailwindcss(),
    metaImagesPlugin(),
  ];

  // Conditionally add development plugins
  if (process.env.NODE_ENV !== "production" && process.env.REPL_ID !== undefined) {
    try {
      const [cartographerModule, devBannerModule] = await Promise.all([
        import("@replit/vite-plugin-cartographer"),
        import("@replit/vite-plugin-dev-banner")
      ]);

      plugins.push(
        cartographerModule.cartographer(),
        devBannerModule.devBanner()
      );
    } catch (error) {
      console.warn('Development plugins not available:', error instanceof Error ? error.message : String(error));
    }
  }

  return {
    plugins,
    resolve: {
      alias: {
        "@": path.resolve(import.meta.dirname, "client", "src"),
        "@shared": path.resolve(import.meta.dirname, "shared"),
        "@assets": path.resolve(import.meta.dirname, "attached_assets"),
      },
    },
    css: {
      postcss: {
        plugins: [],
      },
    },
    root: path.resolve(import.meta.dirname, "client"),
    build: {
      outDir: path.resolve(import.meta.dirname, "dist/public"),
      emptyOutDir: true,
    },
    // Cache busting for development
    cacheDir: 'node_modules/.vite-cache-v2-update',
    server: {
      host: "0.0.0.0",
      open: true,  // Automatically open the browser when starting the dev server
      allowedHosts: true,
      headers:
        mode !== "production"
          ? {
              "Content-Security-Policy": buildDevCsp(),
            }
          : undefined,
      proxy: {
        "/api": {
          target: "http://localhost:3000",
          changeOrigin: true,
          secure: false,
          ws: true,
        },
      },
      fs: {
        strict: true,
        deny: ["**/.*"],
      },
    },
  };
});
