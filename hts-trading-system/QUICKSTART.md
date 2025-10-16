# 🚀 HTS Trading System - Quick Start Guide

## One-Command Start

### Windows
```cmd
:: Start Backend
cd hts-trading-system\backend
npm install
npm run dev

:: In new terminal - Start Frontend
cd hts-trading-system\frontend
npm install
npm run dev
```

### Linux/Mac
```bash
# Start Backend
cd hts-trading-system/backend
npm install && npm run dev &

# Start Frontend
cd hts-trading-system/frontend
npm install && npm run dev
```

---

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://localhost:3001 | REST API |
| **Health Check** | http://localhost:3001/api/health | System status |
| **WebSocket** | ws://localhost:3001 | Real-time data |

---

## Quick Test

### 1. Test Backend
```bash
curl http://localhost:3001/api/health
# Expected: {"status":"OK",...}

curl http://localhost:3001/api/prices
# Expected: Array of price data
```

### 2. Test Frontend
1. Open http://localhost:5173
2. Check connection status (green = connected)
3. Verify prices are updating
4. Check charts are rendering

---

## Environment Variables

**Backend (.env)** - Already configured ✅
```env
PORT=3001
BINANCE_TESTNET_URL=https://testnet.binance.vision/api
SYMBOLS=BTC,ETH,BNB,ADA,SOL
```

---

## Key Features

✅ **Real-time Prices** - Live from Binance Testnet  
✅ **Technical Indicators** - RSI, MACD, ATR, Bollinger Bands  
✅ **AI Predictions** - BUY/SELL/HOLD signals  
✅ **Market Sentiment** - Fear & Greed Index  
✅ **News Feed** - Latest crypto news  
✅ **Whale Tracking** - Large transactions  
✅ **Feature Flags** - Progressive rollout  

---

## Troubleshooting

**Port in use?**
```bash
# Kill process on port 3001
lsof -i :3001
kill -9 <PID>
```

**Dependencies missing?**
```bash
cd backend && npm install
cd ../frontend && npm install
```

**WebSocket not connecting?**
1. Ensure backend is running
2. Check port 3001 is accessible
3. Refresh browser (Ctrl+R)

---

## Navigation

- **Dashboard** - Main overview with all data
- **Charts** - Advanced price charts
- **Training** - AI training dashboard
- **Portfolio** - Track positions
- **News** - Latest crypto news
- **Settings** - Feature flags & config

---

## Performance Expectations

- Dashboard load: < 2 seconds
- Price updates: Every 1 second
- Chart rendering: 60 FPS
- Memory usage: < 150MB

---

## Next Steps

1. ✅ Verify both servers are running
2. ✅ Open frontend in browser
3. ✅ Check WebSocket connection (green dot)
4. ✅ Verify prices updating
5. ✅ Explore different views
6. ✅ Try feature flags in Settings

---

**🎉 You're ready to start analyzing cryptocurrency markets!**

For detailed documentation, see: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
