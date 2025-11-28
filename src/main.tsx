import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Version marker for deployment verification
console.log('%c🚀 QARIQA v2.0 - BUILD: 2025-01-28 15:30 UTC', 'background: #4CAF50; color: white; font-size: 16px; font-weight: bold; padding: 8px;');
console.log('%c✨ NEW: Odoo Authentication via Netlify Functions (No CORS!)', 'background: #2196F3; color: white; font-size: 14px; padding: 4px;');
console.log('%cIf you see this message, you are running the LATEST version with NEW auth system', 'color: #4CAF50; font-weight: bold;');
console.log('');
console.log('%c📊 Environment Configuration', 'background: #9C27B0; color: white; font-weight: bold; padding: 4px;');
console.log(`  API Base URL: ${import.meta.env.VITE_API_BASE_URL || 'https://qariqa-staging.qariqa.com (default)'}`);
console.log(`  Odoo Database: ${import.meta.env.VITE_ODOO_DATABASE || 'main (default)'} ${import.meta.env.VITE_ODOO_DATABASE ? '✅' : '⚠️ ENV VAR NOT SET - using fallback!'}`);
console.log('');

createRoot(document.getElementById("root")!).render(<App />);
