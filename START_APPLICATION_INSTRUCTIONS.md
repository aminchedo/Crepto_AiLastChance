# 🚀 Start Crepto_AI Application - Step by Step Guide

**Date:** 2025-10-15  
**Status:** Proxy Server Running ✅ | Backend Needed ⚠️ | Frontend Ready to Start

---

## ✅ Current Status

### Proxy Server (Port 3002) - 🟢 RUNNING
```
✅ CoinMarketCap API - Available
✅ CryptoCompare API - Available
✅ CoinGecko API - Available
✅ Fear & Greed API - Available
✅ News API - Available (NEW KEY WORKING!)
✅ Whale Alert API - Available
```

### Backend Server (Port 8000) - ⚠️ NOT RUNNING
- Needs to be started manually

### Frontend Server (Port 5173) - ⏸️ READY TO START
- Will start in the next steps

---

## 🚀 Quick Start (Windows)

### Option 1: Use the Automated Launcher (EASIEST)

Open a **new Command Prompt** window and run:

```bash
cd C:\project\Crepto_Ai
start-with-proxy.bat
```

This will automatically:
1. ✅ Proxy Server (already running - will detect and skip)
2. 🚀 Start Python Backend (Port 8000)
3. 🚀 Start React Frontend (Port 5173)
4. 🌐 Open browser automatically

**Then wait 15-20 seconds** for all services to start.

---

## 🚀 Manual Start (Step by Step)

If you prefer to start services manually:

### Step 1: Start Backend Server

Open a **new terminal/command prompt**:

```bash
cd C:\project\Crepto_Ai\backend

# If you have a virtual environment:
call venv\Scripts\activate

# Start the backend:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Keep this terminal open!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 2: Start Frontend Server

Open **another new terminal/command prompt**:

```bash
cd C:\project\Crepto_Ai

# Start the frontend:
npm run dev
```

**Keep this terminal open!** You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Step 3: Open Browser

Open your browser to:
```
http://localhost:5173
```

---

## 🔍 Browser Console Verification

Once the application opens:

### 1. Open Developer Tools
- Press **F12** or **Ctrl+Shift+I** (Windows/Linux)
- Press **Cmd+Option+I** (Mac)

### 2. Go to Console Tab
Look for these **GOOD** signs:
```
✅ No CORS errors
✅ Proxy server connected: http://localhost:3002
✅ API calls returning 200 status
✅ Fear & Greed Index loaded
✅ Market data displaying
```

### 3. Look for **BAD** signs (should not see):
```
❌ Access to fetch at '...' has been blocked by CORS policy
❌ Failed to fetch
❌ Network error
❌ 401 Unauthorized
```

### 4. Test API Calls in Console

Click in the **Console** tab and paste these test commands:

#### Test 1: Quick Health Check
```javascript
fetch('http://localhost:3002/health')
  .then(r => r.json())
  .then(d => console.log('✅ Proxy Health:', d))
  .catch(e => console.error('❌ Error:', e));
```

#### Test 2: Fear & Greed Index
```javascript
fetch('http://localhost:3002/api/feargreed')
  .then(r => r.json())
  .then(d => console.log('😨 Fear & Greed:', d.data[0]))
  .catch(e => console.error('❌ Error:', e));
```

#### Test 3: Bitcoin Price
```javascript
fetch('http://localhost:3002/api/coingecko/price?ids=bitcoin')
  .then(r => r.json())
  .then(d => console.log('₿ Bitcoin:', d.bitcoin))
  .catch(e => console.error('❌ Error:', e));
```

#### Test 4: Crypto News
```javascript
fetch('http://localhost:3002/api/news/crypto?q=bitcoin')
  .then(r => r.json())
  .then(d => console.log('📰 News:', d.articles?.slice(0, 3)))
  .catch(e => console.error('❌ Error:', e));
```

---

## 📊 Expected Console Output

### Good Output ✅
```javascript
✅ Proxy Health: {
  status: "OK",
  service: "Crypto API Proxy Server",
  port: "3002",
  endpoints: { ... }
}

😨 Fear & Greed: {
  value: "34",
  value_classification: "Fear"
}

₿ Bitcoin: {
  usd: 111303,
  usd_24h_change: -1.44
}

📰 News: [
  { title: "...", description: "...", url: "..." },
  ...
]
```

### Bad Output ❌
```javascript
❌ Access to fetch at 'https://api.alternative.me/fng/' from origin 'http://localhost:5173' 
   has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

If you see CORS errors, the proxy is not being used correctly.

---

## 🎯 What to Look For in the UI

### 1. Market Overview Section
- ✅ Bitcoin, Ethereum prices updating
- ✅ 24h change percentages showing
- ✅ Market cap values displaying

### 2. Fear & Greed Indicator
- ✅ Current value (e.g., "34")
- ✅ Classification (e.g., "Fear")
- ✅ Progress bar showing
- ✅ Color indicator (red/orange/yellow/green/blue)

### 3. News Section
- ✅ Latest crypto news articles
- ✅ Article titles and descriptions
- ✅ "Read more" links

### 4. Charts
- ✅ Price charts rendering
- ✅ Data points displaying
- ✅ Interactive tooltips

---

## 🐛 Troubleshooting

### Issue 1: CORS Errors Still Appearing

**Problem:** Still seeing CORS errors in console  
**Solution:**
```bash
# 1. Make sure proxy is running
curl http://localhost:3002/health

# 2. Check .env.local has:
VITE_PROXY_SERVER_URL=http://localhost:3002
VITE_USE_REAL_APIS=true

# 3. Restart frontend
# Press Ctrl+C in frontend terminal
npm run dev
```

### Issue 2: Proxy Server Not Responding

**Problem:** `curl http://localhost:3002/health` fails  
**Solution:**
```bash
cd C:\project\Crepto_Ai\proxy-server
npm start
```

### Issue 3: Backend Not Starting

**Problem:** Backend fails to start  
**Solution:**
```bash
# Check Python is installed
python --version

# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed, then restart
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 4: Frontend Not Starting

**Problem:** `npm run dev` fails  
**Solution:**
```bash
# Check Node.js is installed
node --version

# Check if port 5173 is in use
netstat -ano | findstr :5173

# Reinstall dependencies if needed
npm install
npm run dev
```

### Issue 5: API Calls Return 401

**Problem:** API calls failing with 401 Unauthorized  
**Solution:**
```bash
# Check API keys in proxy-server/.env
cat proxy-server/.env

# Should show:
# NEWSAPI_KEY=968a5e25552b4cb5ba3280361d8444ab
# CMC_API_KEY=b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c
# etc.

# If incorrect, update and restart proxy
cd proxy-server
npm start
```

---

## 📋 Verification Checklist

Before you start:
- [x] Proxy server running on port 3002
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] Browser open to http://localhost:5173
- [ ] Developer console open (F12)
- [ ] No CORS errors in console
- [ ] API data loading in UI
- [ ] Fear & Greed showing current value
- [ ] News articles displaying

---

## 🎉 Success Criteria

Your application is working correctly when you see:

### In Browser Console:
```
✅ No CORS policy errors
✅ API calls to http://localhost:3002/api/* succeeding
✅ 200 status codes on all requests
✅ Data objects logging successfully
```

### In Browser UI:
```
✅ Fear & Greed Index: 34 (Fear)
✅ Bitcoin Price: $111,303
✅ News articles loading
✅ Charts displaying
✅ No error messages
```

---

## 🔗 Quick Reference

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Proxy Server | 3002 | http://localhost:3002 | 🟢 Running |
| Backend API | 8000 | http://localhost:8000 | ⚪ Not Started |
| Frontend App | 5173 | http://localhost:5173 | ⚪ Not Started |

---

## 💡 Pro Tips

1. **Keep all terminal windows open** - closing them stops the services
2. **Check proxy health first** - `curl http://localhost:3002/health`
3. **Use Ctrl+C to stop services** - don't just close terminals
4. **Check console for errors** - F12 in browser
5. **Use the test commands** - they help verify everything works

---

## 📞 Need Help?

If you see errors:
1. Check which service is failing (proxy/backend/frontend)
2. Look at the error message in the terminal
3. Check the troubleshooting section above
4. Verify API keys in `.env` files
5. Make sure all ports (3002, 8000, 5173) are available

---

**Ready to start!** 🚀

Open a Command Prompt and run:
```bash
cd C:\project\Crepto_Ai
start-with-proxy.bat
```

Then check the browser console for CORS errors!

---

*Last Updated: 2025-10-15 23:00 UTC*  
*Proxy Status: 🟢 RUNNING*  
*All APIs: ✅ CONFIGURED*
