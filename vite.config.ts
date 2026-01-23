import { defineConfig, type UserConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import runtimeErrorOverlay from '@replit/vite-plugin-runtime-error-modal';
import { metaImagesPlugin } from './vite-plugin-meta-images';

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
  ].join('; ');
}

export default defineConfig(async ({ mode }): Promise<UserConfig> => {
  const plugins = [
    react(),
    runtimeErrorOverlay(),
    tailwindcss(),
    metaImagesPlugin(),
  ];

  // Conditionally add development plugins
  if (
    process.env.NODE_ENV !== 'production' &&
    process.env.REPL_ID !== undefined
  ) {
    try {
      const [cartographerModule, devBannerModule] = await Promise.all([
        import('@replit/vite-plugin-cartographer'),
        import('@replit/vite-plugin-dev-banner'),
      ]);

      plugins.push(
        cartographerModule.cartographer(),
        devBannerModule.devBanner()
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.warn('Development plugins not available:', message);
    }
  }

  return {
    plugins,
    resolve: {
      alias: {
        '@': path.resolve(import.meta.dirname, 'client', 'src'),
        '@shared': path.resolve(import.meta.dirname, 'shared'),
        '@assets': path.resolve(import.meta.dirname, 'attached_assets'),
      },
    },
    css: {
      postcss: {
        plugins: [],
      },
    },
    root: path.resolve(import.meta.dirname, 'client'),
    build: {
      outDir: path.resolve(import.meta.dirname, 'dist/public'),
      emptyOutDir: true,
      chunkSizeWarningLimit: 800,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              if (id.includes('react-dom') || id.includes('react-router')) {
                return 'vendor-react';
              }
              if (id.includes('@radix-ui')) {
                return 'vendor-radix';
              }
              if (id.includes('recharts') || id.includes('d3-') || id.includes('recharts-scale') || id.includes('victory')) {
                return 'vendor-charts';
              }
              if (id.includes('framer-motion')) {
                return 'vendor-motion';
              }
              if (id.includes('@tanstack')) {
                return 'vendor-query';
              }
              if (id.includes('jspdf') || id.includes('html2canvas') || id.includes('canvg')) {
                return 'vendor-pdf';
              }
              if (id.includes('lucide-react')) {
                return 'vendor-icons';
              }
            }
          },
        },
      },
    },
    // Cache busting for development
    cacheDir: 'node_modules/.vite-cache-v2-update',
    server: {
      host: '0.0.0.0',
      open: true, // Automatically open the browser when starting the dev server
      allowedHosts: true,
      headers:
        mode !== 'production'
          ? {
              'Content-Security-Policy': buildDevCsp(),
            }
          : undefined,
      proxy: {
        '/api': {
          target: 'http://localhost:3000',
          changeOrigin: true,
          secure: false,
          ws: true,
          // Retry configuration to handle server startup timing
          configure: (proxy, options) => {
            proxy.on('error', (err, req, res) => {
              console.log(
                `[Vite Proxy] Connection error to ${options.target}, retrying...`
              );
            });
            proxy.on('proxyReq', (proxyReq, req, res) => {
              // Add timeout and retry logic
              proxyReq.setTimeout(5000, () => {
                console.log(
                  `[Vite Proxy] Timeout connecting to ${options.target}`
                );
              });
            });
          },
        },
      },
      fs: {
        strict: true,
        deny: ['**/.*'],
      },
    },
  };
});
