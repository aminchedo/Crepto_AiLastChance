/**
 * Service Worker Unregister Utility
 * 
 * Use this script to unregister all service workers from your browser.
 * This is useful for debugging or recovering from problematic service workers.
 * 
 * Usage:
 * 1. Open DevTools Console (F12)
 * 2. Copy and paste this entire script
 * 3. Press Enter
 * 4. Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
 * 
 * Or use the shorter version below:
 */

(async function unregisterAllServiceWorkers() {
  if (!('serviceWorker' in navigator)) {
    console.log('❌ Service Workers not supported in this browser');
    return;
  }

  try {
    console.log('🔍 Checking for registered service workers...');
    
    const registrations = await navigator.serviceWorker.getRegistrations();
    
    if (registrations.length === 0) {
      console.log('✅ No service workers found - nothing to unregister');
      return;
    }

    console.log(`📋 Found ${registrations.length} service worker(s)`);
    
    for (const registration of registrations) {
      console.log(`🗑️  Unregistering: ${registration.scope}`);
      const success = await registration.unregister();
      
      if (success) {
        console.log(`✅ Successfully unregistered: ${registration.scope}`);
      } else {
        console.warn(`⚠️  Failed to unregister: ${registration.scope}`);
      }
    }

    // Clear all caches associated with service workers
    console.log('🧹 Cleaning up caches...');
    const cacheNames = await caches.keys();
    
    if (cacheNames.length > 0) {
      console.log(`📦 Found ${cacheNames.length} cache(s) to delete`);
      
      for (const cacheName of cacheNames) {
        console.log(`🗑️  Deleting cache: ${cacheName}`);
        await caches.delete(cacheName);
      }
      
      console.log('✅ All caches cleared');
    } else {
      console.log('✅ No caches to clear');
    }

    console.log('');
    console.log('🎉 Service Worker cleanup complete!');
    console.log('');
    console.log('📋 Next steps:');
    console.log('   1. Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)');
    console.log('   2. Or close and reopen this tab');
    console.log('');
    
  } catch (error) {
    console.error('❌ Error during unregistration:', error);
  }
})();

// Optional: Add this to window for easy access
window.unregisterSW = async function() {
  const registrations = await navigator.serviceWorker.getRegistrations();
  for (const reg of registrations) {
    await reg.unregister();
  }
  const cacheNames = await caches.keys();
  for (const name of cacheNames) {
    await caches.delete(name);
  }
  console.log('✅ Service workers and caches cleared. Please refresh the page.');
};

console.log('💡 Utility function available: window.unregisterSW()');
