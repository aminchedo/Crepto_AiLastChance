# 🚀 Proxy API Quick Start Guide

**Status:** ✅ Complete proxy solution implemented  
**Time to setup:** 2 minutes

---

## 📋 What Was Implemented

### ✅ Files Created

1. **`src/services/ProxyApiService.ts`** (9.5 KB)
   - Complete TypeScript service for all proxy endpoints
   - Automatic fallback between standalone and FastAPI proxy
   - Type-safe interfaces
   - Error handling

2. **`src/services/__tests__/ProxyApiTest.ts`** (4.2 KB)
   - Comprehensive test suite
   - Tests all 10 endpoints
   - Browser console friendly

3. **`src/examples/ProxyApiExample.tsx`** (5.8 KB)
   - Example React component
   - Shows proper integration
   - Styled and ready to use

4. **`backend/api/proxy.py`** (14 KB)
   - FastAPI proxy endpoints
   - Health checks
   - Error handling with fallbacks

### ✅ Files Modified

1. **`backend/main.py`** - Added proxy router
2. **`backend/api/__init__.py`** - Exported proxy module
3. **`vite.config.ts`** - Added proxy configuration

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Start Servers (30 seconds)

```batch
# Start everything at once
start-app.bat
```

This starts:
- ✅ Frontend: `http://localhost:5173`
- ✅ Backend (FastAPI): `http://localhost:8000`
- ✅ Backend Proxy: `http://localhost:8000/api/proxy/*`

**Optional:** Start standalone proxy for auto-fallback:
```batch
# In a new terminal
fix-proxy-now.bat
```

### Step 2: Test the Proxy (30 seconds)

**Option A: Browser Test Page**
```
Open: http://localhost:5173/test-cors-solutions.html
Click: "Test All Solutions"
```

**Option B: Browser Console**
```javascript
// Paste in browser console (F12)
import { testProxyApi } from './src/services/__tests__/ProxyApiTest';
testProxyApi();
```

**Option C: Quick fetch test**
```javascript
// In browser console
fetch('/api/proxy/health').then(r => r.json()).then(console.log)
```

### Step 3: Use in Your Code (60 seconds)

Replace your old API calls with the proxy service:

**❌ OLD WAY (CORS errors):**
```typescript
// Direct API call - causes CORS errors
const response = await fetch('https://api.alternative.me/fng/');
const data = await response.json();
```

**✅ NEW WAY (No CORS):**
```typescript
import { proxyApi } from './services/ProxyApiService';

// Through proxy - no CORS issues!
const data = await proxyApi.getFearGreedIndex();
console.log(data[0]); // { value: "65", value_classification: "Greed", ... }
```

---

## 📚 API Reference

### Import the Service

```typescript
import { proxyApi } from './services/ProxyApiService';
```

### Fear & Greed Index

```typescript
const fearGreed = await proxyApi.getFearGreedIndex(1);
console.log(fearGreed[0].value); // "65"
console.log(fearGreed[0].value_classification); // "Greed"
```

### Market Data (CoinMarketCap)

```typescript
// Top cryptocurrencies
const listings = await proxyApi.getCMCListings(1, 20);
console.log(listings.data); // Array of top 20 coins

// Specific coins
const quotes = await proxyApi.getCMCQuotes('BTC,ETH,BNB');
console.log(quotes.data.BTC.quote.USD.price); // Bitcoin price
```

### Historical Price Data

```typescript
// Get 30 days of historical data
const historical = await proxyApi.getCryptoCompareHistorical('BTC', 'USD', 30);
console.log(historical); // Array of {time, close, high, low, ...}

// Get formatted chart data
const chartData = await proxyApi.getChartData('BTC', 30);
console.log(chartData.labels); // ["Jan 1", "Jan 2", ...]
console.log(chartData.prices); // [45000, 45500, ...]
```

### News Articles

```typescript
const news = await proxyApi.getCryptoNews('bitcoin', 20);
console.log(news); // Array of news articles
```

### Whale Transactions

```typescript
const whales = await proxyApi.getWhaleTransactions(1000000, 10);
console.log(whales); // Array of large transactions
```

### Multiple Prices at Once

```typescript
const prices = await proxyApi.getMultiplePrices(['BTC', 'ETH', 'BNB']);
console.log(prices.get('BTC')); 
// { symbol: "BTC", price: 45000, change24h: 2.5, ... }
```

### Market Overview (All data at once)

```typescript
const overview = await proxyApi.getMarketOverview();
console.log(overview.fearGreed); // Fear & Greed data
console.log(overview.topCoins); // Top 10 cryptocurrencies
console.log(overview.news); // Latest 10 news articles
```

---

## 🎯 Common Use Cases

### 1. Dashboard with Real-Time Data

```typescript
import { useState, useEffect } from 'react';
import { proxyApi } from './services/ProxyApiService';

export const Dashboard = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      const overview = await proxyApi.getMarketOverview();
      setData(overview);
    };

    loadData();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Fear & Greed: {data?.fearGreed.value_classification}</h1>
      {/* ... rest of dashboard */}
    </div>
  );
};
```

### 2. Price Chart Component

```typescript
import { useEffect, useState } from 'react';
import { proxyApi } from './services/ProxyApiService';

export const PriceChart = ({ symbol = 'BTC', days = 30 }) => {
  const [chartData, setChartData] = useState({ labels: [], prices: [] });

  useEffect(() => {
    const loadChart = async () => {
      const data = await proxyApi.getChartData(symbol, days);
      setChartData(data);
    };
    loadChart();
  }, [symbol, days]);

  return (
    <div>
      {/* Use chartData.labels and chartData.prices with your chart library */}
      <LineChart data={chartData.prices} labels={chartData.labels} />
    </div>
  );
};
```

### 3. News Feed Component

```typescript
import { useEffect, useState } from 'react';
import { proxyApi } from './services/ProxyApiService';

export const NewsFeed = () => {
  const [news, setNews] = useState([]);

  useEffect(() => {
    const loadNews = async () => {
      const articles = await proxyApi.getCryptoNews('cryptocurrency', 20);
      setNews(articles);
    };
    loadNews();
  }, []);

  return (
    <div>
      {news.map((article, i) => (
        <div key={i}>
          <h3>{article.title}</h3>
          <p>{article.description}</p>
          <a href={article.url}>Read more</a>
        </div>
      ))}
    </div>
  );
};
```

### 4. Market Sentiment Widget

```typescript
import { useEffect, useState } from 'react';
import { proxyApi } from './services/ProxyApiService';

export const SentimentWidget = () => {
  const [sentiment, setSentiment] = useState(null);

  useEffect(() => {
    const loadSentiment = async () => {
      const data = await proxyApi.getFearGreedIndex();
      setSentiment(data[0]);
    };
    loadSentiment();
  }, []);

  if (!sentiment) return <div>Loading...</div>;

  return (
    <div className={`sentiment-${sentiment.value_classification.toLowerCase()}`}>
      <div className="value">{sentiment.value}/100</div>
      <div className="label">{sentiment.value_classification}</div>
    </div>
  );
};
```

---

## 🧪 Testing

### Test All Endpoints

```javascript
// In browser console (F12)
import('./src/services/__tests__/ProxyApiTest').then(({ testProxyApi }) => {
  testProxyApi();
});
```

### Test Individual Endpoints

```javascript
import { proxyApi } from './services/ProxyApiService';

// Test Fear & Greed
proxyApi.getFearGreedIndex().then(console.log);

// Test Market Data
proxyApi.getCMCListings(1, 10).then(console.log);

// Test News
proxyApi.getCryptoNews('bitcoin', 5).then(console.log);

// Test Historical Data
proxyApi.getCryptoCompareHistorical('BTC', 'USD', 7).then(console.log);

// Test Chart Data
proxyApi.getChartData('BTC', 30).then(console.log);
```

### Check Proxy Health

```javascript
proxyApi.healthCheck().then(console.log);
// Shows status of standalone proxy and FastAPI proxy
```

---

## 🔧 Troubleshooting

### Issue: "Failed to fetch"

**Cause:** Proxy server not running

**Solution:**
```batch
# Start backend (includes FastAPI proxy)
start-app.bat

# Or start standalone proxy
fix-proxy-now.bat
```

### Issue: "No proxy servers available"

**Cause:** Both proxies are down

**Solution:**
```batch
# Check backend
cd backend
venv\Scripts\activate
python main.py

# Check standalone proxy
cd proxy-server
npm start
```

### Issue: Empty data / NaN values

**Cause:** API rate limit or invalid API key

**Solution:**
1. Check proxy logs for errors
2. Try alternative endpoint (CoinGecko instead of CoinMarketCap)
3. Wait a few minutes if rate limited

### Issue: TypeScript errors

**Cause:** Missing types

**Solution:**
```bash
# The ProxyApiService includes all TypeScript types
# Just import them:
import type { FearGreedData, CryptoPrice, NewsArticle } from './services/ProxyApiService';
```

---

## 📊 Available Endpoints

| Method | Description | Example |
|--------|-------------|---------|
| `getFearGreedIndex()` | Market sentiment (0-100) | `proxyApi.getFearGreedIndex()` |
| `getCMCListings()` | Top cryptocurrencies | `proxyApi.getCMCListings(1, 20)` |
| `getCMCQuotes()` | Specific coin quotes | `proxyApi.getCMCQuotes('BTC,ETH')` |
| `getCryptoComparePrice()` | Current prices | `proxyApi.getCryptoComparePrice('BTC,ETH')` |
| `getCryptoCompareHistorical()` | Historical data | `proxyApi.getCryptoCompareHistorical('BTC', 'USD', 30)` |
| `getCoinGeckoPrice()` | CoinGecko prices | `proxyApi.getCoinGeckoPrice('bitcoin,ethereum')` |
| `getCoinGeckoMarkets()` | Market data | `proxyApi.getCoinGeckoMarkets('usd', 20)` |
| `getCryptoNews()` | News articles | `proxyApi.getCryptoNews('bitcoin', 20)` |
| `getWhaleTransactions()` | Large transactions | `proxyApi.getWhaleTransactions(1000000, 10)` |
| `getChartData()` | Formatted chart data | `proxyApi.getChartData('BTC', 30)` |
| `getMarketOverview()` | Everything at once | `proxyApi.getMarketOverview()` |
| `getMultiplePrices()` | Multiple coins | `proxyApi.getMultiplePrices(['BTC', 'ETH'])` |
| `healthCheck()` | Proxy status | `proxyApi.healthCheck()` |

---

## 🎯 Next Steps

### 1. Replace Existing API Calls

Search your codebase for direct API calls and replace them:

```bash
# Find direct API calls
grep -r "fetch('http" src/
grep -r "axios.get('http" src/
```

Replace with proxy calls using the examples above.

### 2. Add Error Boundaries

```typescript
try {
  const data = await proxyApi.getFearGreedIndex();
  // Use data
} catch (error) {
  console.error('Failed to load data:', error);
  // Show fallback UI
}
```

### 3. Implement Caching

```typescript
const cache = new Map();

async function getCachedData(key, fetcher, ttl = 60000) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }
  
  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now() });
  return data;
}

// Usage
const fearGreed = await getCachedData(
  'fear-greed',
  () => proxyApi.getFearGreedIndex(),
  60000 // Cache for 1 minute
);
```

### 4. Add Loading States

```typescript
const [loading, setLoading] = useState(true);
const [data, setData] = useState(null);
const [error, setError] = useState(null);

useEffect(() => {
  async function load() {
    try {
      setLoading(true);
      setError(null);
      const result = await proxyApi.getMarketOverview();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  load();
}, []);
```

---

## ✅ Checklist

Before using in production:

- [ ] Both proxies tested and working
- [ ] All API calls migrated to proxy service
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] Caching layer added
- [ ] Rate limiting considered
- [ ] API keys secured (environment variables)
- [ ] CORS configured for production domain
- [ ] Monitoring/logging in place

---

## 📚 Full Documentation

- **Complete Guide:** `COMPLETE_CORS_SOLUTIONS.md`
- **Quick Reference:** `CORS_QUICK_REFERENCE.md`
- **Example Component:** `src/examples/ProxyApiExample.tsx`
- **Test Suite:** `src/services/__tests__/ProxyApiTest.ts`

---

## 🎊 Summary

**What you have now:**
- ✅ Complete TypeScript service with all API endpoints
- ✅ Type-safe interfaces
- ✅ Automatic fallback between proxies
- ✅ Comprehensive error handling
- ✅ Test suite
- ✅ Example components
- ✅ Full documentation

**How to use:**
```typescript
import { proxyApi } from './services/ProxyApiService';
const data = await proxyApi.getFearGreedIndex();
```

**That's it!** No more CORS errors! 🎉

---

*All proxy endpoints are working and ready to use!* 🚀
