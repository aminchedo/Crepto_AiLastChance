# HTS Trading System - Quick Start Guide

## 🚀 Get Running in 5 Minutes

This guide will get your HTS Trading System up and running quickly.

---

## Prerequisites

✅ Node.js 18+ installed ([Download here](https://nodejs.org/))  
✅ Terminal/Command Prompt access  
✅ Text editor (VS Code recommended)

---

## Step 1: Navigate to Project

```bash
cd hts-trading-system
```

---

## Step 2: Install Backend

```bash
cd backend-node
npm install
```

**Expected output:** Dependencies installed successfully

---

## Step 3: Install Frontend

```bash
cd ../frontend-react
npm install
```

**Expected output:** Dependencies installed successfully

---

## Step 4: Start Backend

**Open Terminal 1:**
```bash
cd backend-node
npm run dev
```

**Look for:**
```
╔════════════════════════════════════════════════════════╗
║   🚀 HTS Trading System - Backend Started              ║
║   📍 Port: 3001                                        ║
║   🔄 Symbols: BTC, ETH, BNB                           ║
║   ✅ Status: Ready for connections                     ║
╚════════════════════════════════════════════════════════╝
```

---

## Step 5: Start Frontend

**Open Terminal 2:**
```bash
cd frontend-react
npm run dev
```

**Look for:**
```
  VITE v4.4.5  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Step 6: Open Browser

Navigate to: **http://localhost:5173**

You should see:
- ✅ Green "Connected" indicator
- ✅ Live cryptocurrency prices
- ✅ Technical indicators (RSI, MACD)
- ✅ Market sentiment gauge
- ✅ AI predictions
- ✅ News feed

---

## Step 7: Verify Everything Works

### Backend API Test

Open a new terminal:
```bash
curl http://localhost:3001/api/health
```

**Expected:** `{"status":"OK","timestamp":"..."}`

### WebSocket Test

In the browser:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for: `✅ WebSocket connected`
4. Watch prices update every second

---

## 🎉 Success!

Your HTS Trading System is now running!

### What's Working:

✅ **Live Data** - Real-time prices from Binance  
✅ **Technical Analysis** - RSI, MACD calculations  
✅ **Sentiment** - Market mood tracking  
✅ **News** - Cryptocurrency news feed  
✅ **AI** - Price predictions  
✅ **Charts** - Interactive visualizations

---

## 📊 Using the Dashboard

### Navigation Tabs:
- **Dashboard** - Main overview (default)
- **Charts** - Advanced charting (Phase 2)
- **Training** - AI training metrics (Phase 2)
- **Portfolio** - Position tracking (Phase 2)
- **News** - News articles view
- **Settings** - Feature flag management

### Feature Flags:
1. Go to **Settings** tab
2. Toggle features ON/OFF
3. Changes save automatically

---

## 🔍 Testing Checklist

Run through this checklist:

- [ ] Backend started successfully (port 3001)
- [ ] Frontend loaded (http://localhost:5173)
- [ ] Green "Connected" indicator visible
- [ ] Prices updating every 1 second
- [ ] RSI gauge showing 0-100 value
- [ ] MACD chart displaying
- [ ] Sentiment score visible
- [ ] News articles loaded
- [ ] AI prediction showing BUY/SELL/HOLD
- [ ] No errors in browser console
- [ ] Navigation works (all tabs)

---

## ⚡ Quick Commands

### Restart Backend
```bash
# Ctrl+C to stop
npm run dev
```

### Restart Frontend
```bash
# Ctrl+C to stop  
npm run dev
```

### Check API Health
```bash
curl http://localhost:3001/api/health
```

### View All Prices
```bash
curl http://localhost:3001/api/prices
```

### View BTC Indicators
```bash
curl http://localhost:3001/api/indicators/BTC
```

---

## 🐛 Quick Fixes

### Port Already in Use
```bash
lsof -i :3001
kill -9 <PID>
```

### WebSocket Not Connecting
1. Refresh browser (Ctrl+R)
2. Check backend is running
3. Clear browser cache

### Missing Dependencies
```bash
# Backend
cd backend-node
rm -rf node_modules
npm install

# Frontend
cd frontend-react
rm -rf node_modules
npm install
```

---

## 📱 Mobile Testing

1. Get your computer's IP:
   ```bash
   # Mac/Linux
   ifconfig | grep inet
   
   # Windows
   ipconfig
   ```

2. Access from phone:
   ```
   http://<your-ip>:5173
   ```

---

## 🎯 Next Steps

Now that you're running:

1. **Explore the Dashboard** - Watch live data flow
2. **Check Settings** - Toggle feature flags
3. **Read API Docs** - See [README.md](./README.md)
4. **Review Code** - Understand the architecture
5. **Prepare for Phase 2** - Smart Money Concepts coming!

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](./README.md)
- **API Endpoints:** See README.md § API Documentation
- **Troubleshooting:** See README.md § Troubleshooting
- **Phase 2 Features:** See README.md § Phase 2 Roadmap

---

**🎊 Congratulations! You're all set!**

Your professional cryptocurrency trading system is now live and analyzing markets in real-time.

Happy Trading! 📈
