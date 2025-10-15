import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
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

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
