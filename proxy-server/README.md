# 🌐 CORS-Free Crypto API Proxy Server

**The ultimate solution to CORS issues for crypto applications.**

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start server
npm start

# Test endpoints
npm test
```

---

## ✅ What This Does

**Eliminates ALL CORS errors by:**
- Proxying API calls through Node.js backend
- Securing API keys on server (not exposed to browser)
- Automatic fallbacks when APIs fail
- Request caching to reduce API calls
- Rate limiting to prevent abuse

---

## 📊 Supported APIs

### ✅ **Working APIs:**
- CoinMarketCap (with 2 API keys + fallback)
- CoinGecko (free tier)
- CryptoCompare (with API key)
- Fear & Greed Index
- NewsAPI
- Etherscan
- BscScan
- TronScan

---

## 🔌 Endpoints

### Market Data:
```
GET /api/coinmarketcap/quotes?symbols=BTC,ETH,BNB
GET /api/coingecko/price?ids=bitcoin,ethereum
GET /api/cryptocompare/price?fsyms=BTC,ETH
```

### Sentiment:
```
GET /api/feargreed
```

### News:
```
GET /api/news/crypto?q=bitcoin&pageSize=20
```

### Health:
```
GET /health
```

---

## ⚙️ Configuration

All API keys in `.env` file (already configured with your keys!)

```env
CMC_API_KEY=b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c
CRYPTOCOMPARE_KEY=e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f
ETHERSCAN_KEY=SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2
# ... more keys
```

---

## 🧪 Testing

```bash
# Test all endpoints
npm test

# Manual test
curl http://localhost:3002/health
curl http://localhost:3002/api/feargreed
```

---

## 🎯 Frontend Usage

```typescript
import { proxyDataService } from './services/proxyDataService';

// Get data - NO CORS errors!
const data = await proxyDataService.getCoinMarketCapData(['BTC']);
const sentiment = await proxyDataService.getFearGreedIndex();
const news = await proxyDataService.getCryptoNews();
```

---

## 🎉 Benefits

- ✅ **NO CORS errors** - All requests are same-origin
- ✅ **Secure** - API keys hidden from browser
- ✅ **Fast** - Built-in caching
- ✅ **Reliable** - Automatic fallbacks
- ✅ **Production-ready** - Rate limiting, logging

---

**See PROXY_SERVER_SETUP.md for complete documentation.**
