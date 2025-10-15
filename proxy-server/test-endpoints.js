/**
 * Test Proxy Server Endpoints
 * Run this after starting the proxy server to verify all endpoints
 */

const axios = require('axios');

const PROXY_URL = 'http://localhost:3002';

async function testEndpoint(name, url) {
  try {
    console.log(`\n🔄 Testing ${name}...`);
    const response = await axios.get(url, { timeout: 10000 });
    console.log(`✅ ${name}: SUCCESS`);
    console.log(`   Response keys: ${Object.keys(response.data).join(', ')}`);
    return true;
  } catch (error) {
    console.log(`❌ ${name}: FAILED`);
    console.log(`   Error: ${error.message}`);
    return false;
  }
}

async function runAllTests() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('  🧪 PROXY SERVER ENDPOINT TESTS');
  console.log('═══════════════════════════════════════════════════════════\n');

  const tests = [
    { name: 'Health Check', url: `${PROXY_URL}/health` },
    { name: 'CoinMarketCap', url: `${PROXY_URL}/api/coinmarketcap/quotes?symbols=BTC,ETH` },
    { name: 'CoinGecko', url: `${PROXY_URL}/api/coingecko/price?ids=bitcoin,ethereum` },
    { name: 'CryptoCompare', url: `${PROXY_URL}/api/cryptocompare/price?fsyms=BTC,ETH` },
    { name: 'Fear & Greed', url: `${PROXY_URL}/api/feargreed` },
    { name: 'News', url: `${PROXY_URL}/api/news/crypto?q=bitcoin` },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    const result = await testEndpoint(test.name, test.url);
    if (result) passed++;
    else failed++;
    
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('\n═══════════════════════════════════════════════════════════');
  console.log(`📊 TEST RESULTS: ${passed}/${tests.length} passed`);
  console.log('═══════════════════════════════════════════════════════════\n');

  if (passed === tests.length) {
    console.log('🎉 ALL TESTS PASSED! Proxy server is working correctly.\n');
  } else {
    console.log(`⚠️  ${failed} test(s) failed. Check API keys and network connection.\n`);
  }
}

runAllTests().catch(console.error);
