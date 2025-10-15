# 🚀 CORS Quick Reference Card

**Last Updated:** 2025-10-15

---

## ⚡ Quick Start

```batch
# Start everything at once
start-app.bat

# Backend runs on: http://localhost:8000
# Frontend runs on: http://localhost:5173
# Proxy runs on: http://localhost:3002
```

---

## 📌 Which Solution Should I Use?

| Situation | Use This | Why |
|-----------|----------|-----|
| **Production** | FastAPI Proxy | Secure, integrated, scalable |
| **Development** | Any/All | Maximum flexibility |
| **Quick test** | Alternative APIs | No setup needed |
| **Backend down** | Standalone Proxy | Independent service |

---

## 🔗 Quick API Reference

### FastAPI Backend Proxy (Recommended)

```javascript
// Base URL
const BASE = '/api/proxy';

// Fear & Greed
fetch(`${BASE}/fear-greed`)

// Market data
fetch(`${BASE}/coinmarketcap/listings?limit=20`)
fetch(`${BASE}/coingecko/markets?per_page=20`)

// Prices
fetch(`${BASE}/coinmarketcap/quotes?symbols=BTC,ETH`)
fetch(`${BASE}/coingecko/price?ids=bitcoin,ethereum&vs_currencies=usd`)

// News
fetch(`${BASE}/news?query=bitcoin&page_size=20`)

// Health
fetch(`${BASE}/health`)
```

### Standalone Proxy Server

```javascript
// Base URL
const BASE = 'http://localhost:3002/api';

// Fear & Greed
fetch(`${BASE}/feargreed`)

// Prices
fetch(`${BASE}/cryptocompare/price?fsyms=BTC,ETH&tsyms=USD`)
fetch(`${BASE}/coingecko/price?ids=bitcoin,ethereum&vs_currencies=usd`)

// Market data (with auto-fallback)
fetch(`${BASE}/coinmarketcap/quotes?symbols=BTC,ETH`)

// News (with fallback)
fetch(`${BASE}/news/crypto?q=bitcoin&pageSize=20`)

// Health
fetch('http://localhost:3002/health')
```

### Direct APIs (No Proxy)

```javascript
// CoinGecko
fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=20')
fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd')

// Binance
fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
fetch('https://api.binance.com/api/v3/ticker/24hr')
```

---

## 🧪 Quick Test

### Test in Browser Console

```javascript
// Test FastAPI proxy
fetch('/api/proxy/health').then(r => r.json()).then(console.log)

// Test standalone proxy
fetch('http://localhost:3002/health').then(r => r.json()).then(console.log)

// Test Fear & Greed
fetch('/api/proxy/fear-greed').then(r => r.json()).then(console.log)

// Test CoinGecko direct
fetch('https://api.coingecko.com/api/v3/ping').then(r => r.json()).then(console.log)
```

### Test Page

Open in browser:
```
http://localhost:5173/test-cors-solutions.html
```

---

## 🛠️ Troubleshooting

### Backend not responding

```batch
cd backend
venv\Scripts\activate
python main.py
```

### Proxy not running

```batch
fix-proxy-now.bat
```

### CORS errors still appearing

**Change from:**
```javascript
fetch('https://api.alternative.me/fng/')  // ❌
```

**To:**
```javascript
fetch('/api/proxy/fear-greed')  // ✅
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `backend/api/proxy.py` | FastAPI proxy endpoints |
| `proxy-server/server.js` | Standalone proxy server |
| `vite.config.ts` | Vite proxy configuration |
| `start-app.bat` | Start everything |
| `fix-proxy-now.bat` | Start standalone proxy |
| `test-cors-solutions.html` | Test all solutions |

---

## 🔑 API Keys Location

```python
# backend/config.py
DATABASE_URL = "sqlite+aiosqlite:///./crypto_ai.db"

# backend/api/proxy.py
CMC_KEY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
NEWS_KEY = "968a5e25552b4cb5ba3280361d8444ab"

# proxy-server/server.js
CMC_PRIMARY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
CRYPTOCOMPARE = "e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f"
```

---

## 💡 Common Use Cases

### Get Fear & Greed Index

```javascript
const { data } = await fetch('/api/proxy/fear-greed').then(r => r.json());
const sentiment = data.data[0];
console.log(`Sentiment: ${sentiment.value_classification} (${sentiment.value}/100)`);
```

### Get Top 10 Cryptocurrencies

```javascript
const { data } = await fetch('/api/proxy/coinmarketcap/listings?limit=10').then(r => r.json());
console.log(data.data); // Array of top 10 coins
```

### Get Bitcoin Price

```javascript
const { data } = await fetch('/api/proxy/coingecko/price?ids=bitcoin&vs_currencies=usd').then(r => r.json());
console.log(`BTC: $${data.bitcoin.usd}`);
```

### Get Crypto News

```javascript
const { data } = await fetch('/api/proxy/news?query=bitcoin&page_size=10').then(r => r.json());
console.log(data.articles); // Array of 10 news articles
```

---

## ✅ Checklist

Before deploying:

- [ ] Backend `/api/proxy` endpoints tested
- [ ] All API keys moved to environment variables
- [ ] CORS origins configured for production domain
- [ ] Rate limiting enabled
- [ ] Caching layer implemented (Redis)
- [ ] Error handling tested
- [ ] Monitoring/logging in place

---

## 📚 Full Documentation

- **Complete Guide:** `COMPLETE_CORS_SOLUTIONS.md`
- **Proxy Fix:** `PROXY_FIX_README.md`
- **Database Fix:** `ASYNC_DATABASE_FIX.md`

---

## 🎯 Remember

**Golden Rule:** Never call external APIs directly from the browser in production!

Always use:
1. ✅ Backend proxy (FastAPI)
2. ✅ Proxy server
3. ✅ APIs with good CORS (CoinGecko, Binance)

---

*Keep this card handy for quick reference!* 🚀
