import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import { ErrorBoundary } from './components/ErrorBoundary';
import './index.css';

// Load API test utilities in development mode
if (import.meta.env.DEV) {
  Promise.all([
    import('./utils/apiTestHelper'),
    import('./utils/universalAPITester')
  ]).then(() => {
    console.log('🧪 Development mode: All test utilities loaded');
    console.log('');
    console.log('Available Commands:');
    console.log('  📊 Original APIs:');
    console.log('     - qt()  // Quick test');
    console.log('     - qm()  // Quick metrics');
    console.log('     - qd()  // Quick diagnostics');
    console.log('     - troubleshoot.help()');
    console.log('');
    console.log('  🌐 Universal APIs (NEW):');
    console.log('     - universalAPITester.quickTest()');
    console.log('     - universalAPITester.runAllTests()');
    console.log('     - universalAPITester.testMarketData()');
    console.log('     - universalAPITester.testSentiment()');
    console.log('     - universalAPITester.testNews()');
    console.log('');
  });
}

// Register Service Worker (PRODUCTION ONLY)
// This prevents SW from interfering with Vite HMR and dev server in development
if (import.meta.env.PROD) {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('✅ Service Worker registered successfully:', registration.scope);
          
          // Check for updates periodically
          setInterval(() => {
            registration.update();
          }, 60000); // Check every minute
          
          // Listen for new service worker updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // New service worker available, prompt user to refresh
                  console.log('🔄 New version available! Please refresh the page.');
                  // You could show a notification here
                }
              });
            }
          });
        })
        .catch((error) => {
          console.warn('⚠️ Service Worker registration failed:', error);
        });
    });
  } else {
    console.log('ℹ️ Service Workers are not supported in this browser');
  }
} else {
  console.log('🔧 Development mode: Service Worker registration skipped');
  console.log('💡 SW only runs in production to avoid conflicts with Vite HMR');
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);
