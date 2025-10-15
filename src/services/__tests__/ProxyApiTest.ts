/**
 * Proxy API Service Test
 * Run this in browser console to test all proxy endpoints
 */

import { proxyApi } from '../ProxyApiService';

export async function testProxyApi() {
  console.log('🧪 Starting Proxy API Tests...\n');

  const results: { [key: string]: boolean } = {};

  // Test 1: Health Check
  console.log('1️⃣ Testing Health Check...');
  try {
    const health = await proxyApi.healthCheck();
    console.log('✅ Health Check:', health);
    results.healthCheck = true;
  } catch (error) {
    console.error('❌ Health Check failed:', error);
    results.healthCheck = false;
  }

  // Test 2: Fear & Greed Index
  console.log('\n2️⃣ Testing Fear & Greed Index...');
  try {
    const fearGreed = await proxyApi.getFearGreedIndex();
    console.log('✅ Fear & Greed:', fearGreed[0]);
    results.fearGreed = true;
  } catch (error) {
    console.error('❌ Fear & Greed failed:', error);
    results.fearGreed = false;
  }

  // Test 3: CoinMarketCap Listings
  console.log('\n3️⃣ Testing CoinMarketCap Listings...');
  try {
    const listings = await proxyApi.getCMCListings(1, 5);
    console.log('✅ CMC Listings:', listings.data?.slice(0, 2));
    results.cmcListings = true;
  } catch (error) {
    console.error('❌ CMC Listings failed:', error);
    results.cmcListings = false;
  }

  // Test 4: CoinMarketCap Quotes
  console.log('\n4️⃣ Testing CoinMarketCap Quotes...');
  try {
    const quotes = await proxyApi.getCMCQuotes('BTC,ETH');
    console.log('✅ CMC Quotes:', quotes.data);
    results.cmcQuotes = true;
  } catch (error) {
    console.error('❌ CMC Quotes failed:', error);
    results.cmcQuotes = false;
  }

  // Test 5: CryptoCompare Price
  console.log('\n5️⃣ Testing CryptoCompare Price...');
  try {
    const price = await proxyApi.getCryptoComparePrice('BTC,ETH');
    console.log('✅ CryptoCompare Price:', price);
    results.cryptoComparePrice = true;
  } catch (error) {
    console.error('❌ CryptoCompare Price failed:', error);
    results.cryptoComparePrice = false;
  }

  // Test 6: Historical Data
  console.log('\n6️⃣ Testing Historical Data...');
  try {
    const historical = await proxyApi.getCryptoCompareHistorical('BTC', 'USD', 7);
    console.log('✅ Historical Data (last 7 days):', historical.slice(0, 3));
    results.historicalData = true;
  } catch (error) {
    console.error('❌ Historical Data failed:', error);
    results.historicalData = false;
  }

  // Test 7: CoinGecko Price
  console.log('\n7️⃣ Testing CoinGecko Price...');
  try {
    const coinGecko = await proxyApi.getCoinGeckoPrice('bitcoin,ethereum');
    console.log('✅ CoinGecko Price:', coinGecko);
    results.coinGeckoPrice = true;
  } catch (error) {
    console.error('❌ CoinGecko Price failed:', error);
    results.coinGeckoPrice = false;
  }

  // Test 8: News
  console.log('\n8️⃣ Testing News API...');
  try {
    const news = await proxyApi.getCryptoNews('bitcoin', 5);
    console.log('✅ News:', news.slice(0, 2));
    results.news = true;
  } catch (error) {
    console.error('❌ News failed:', error);
    results.news = false;
  }

  // Test 9: Whale Transactions
  console.log('\n9️⃣ Testing Whale Alert...');
  try {
    const whales = await proxyApi.getWhaleTransactions(1000000, 5);
    console.log('✅ Whale Transactions:', whales.slice(0, 2));
    results.whaleTransactions = true;
  } catch (error) {
    console.error('❌ Whale Transactions failed:', error);
    results.whaleTransactions = false;
  }

  // Test 10: Chart Data
  console.log('\n🔟 Testing Chart Data...');
  try {
    const chartData = await proxyApi.getChartData('BTC', 7);
    console.log('✅ Chart Data:', {
      dataPoints: chartData.prices.length,
      latestPrice: chartData.prices[chartData.prices.length - 1],
    });
    results.chartData = true;
  } catch (error) {
    console.error('❌ Chart Data failed:', error);
    results.chartData = false;
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));

  const passed = Object.values(results).filter((r) => r).length;
  const total = Object.keys(results).length;

  Object.entries(results).forEach(([test, passed]) => {
    console.log(`${passed ? '✅' : '❌'} ${test}`);
  });

  console.log('\n' + '='.repeat(60));
  console.log(`Result: ${passed}/${total} tests passed`);

  if (passed === total) {
    console.log('🎉 All tests passed! Proxy API is working correctly!');
  } else {
    console.log('⚠️  Some tests failed. Check the errors above.');
  }

  return results;
}

// Auto-run if in browser
if (typeof window !== 'undefined') {
  (window as any).testProxyApi = testProxyApi;
  console.log('💡 Run testProxyApi() in console to test all endpoints');
}
