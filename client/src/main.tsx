import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// Bridge Vite-only env vars into shared code without requiring `import.meta`
// in shared modules (which breaks Jest/ts-jest compilation in CommonJS mode).
if (typeof globalThis !== 'undefined') {
  (globalThis as any).__METAEXTRACT_DEV_FULL_ACCESS__ =
    import.meta.env?.VITE_DEV_FULL_ACCESS;
}

createRoot(document.getElementById('root')!).render(<App />);
