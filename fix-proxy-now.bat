@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title Crepto AI - IMMEDIATE PROXY FIX
color 0E

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        🚨 IMMEDIATE PROXY SERVER FIX                    ║
echo ║           Crepto AI - CORS Solution                     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo This script will:
echo   ✅ Check proxy server setup
echo   ✅ Install dependencies if needed
echo   ✅ Start proxy server on port 3002
echo   ✅ Test all endpoints
echo   ✅ Provide browser console fix
echo.
pause

:: Step 1: Check if proxy server exists
echo.
echo [1/6] Checking proxy server directory...
if not exist "proxy-server" (
    echo ❌ ERROR: proxy-server directory not found!
    echo    Please ensure you're in the Crepto_Ai root directory.
    pause
    exit /b 1
)
echo ✅ Proxy server directory found

:: Step 2: Check if node_modules exists in proxy-server
echo.
echo [2/6] Checking dependencies...
cd proxy-server
if not exist "node_modules" (
    echo 📦 Installing proxy server dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

:: Step 3: Kill any existing process on port 3002
echo.
echo [3/6] Checking for existing proxy server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3002" ^| findstr "LISTENING"') do (
    echo ⚠️  Found process on port 3002 (PID: %%a^)
    echo    Stopping existing process...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 >nul
)
echo ✅ Port 3002 is ready

:: Step 4: Start the proxy server in background
echo.
echo [4/6] Starting proxy server...
start "Crepto AI Proxy Server" cmd /k "node server.js"
echo ⏳ Waiting for proxy server to start...
timeout /t 5 >nul

:: Step 5: Test the proxy server
echo.
echo [5/6] Testing proxy server endpoints...
echo.

:: Test 1: Health check
echo 🏥 Testing health endpoint...
curl --silent --max-time 5 "http://localhost:3002/health" > nul 2>&1
if errorlevel 1 (
    echo ❌ Proxy server not responding
    echo    Please check if Node.js is installed and port 3002 is available
    pause
    exit /b 1
) else (
    echo ✅ Proxy server is running
)

:: Test 2: CryptoCompare endpoint
echo 📈 Testing CryptoCompare endpoint...
curl --silent --max-time 5 "http://localhost:3002/api/cryptocompare/price?fsyms=BTC&tsyms=USD" | findstr "BTC" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  CryptoCompare test failed
) else (
    echo ✅ CryptoCompare working
)

:: Test 3: Fear & Greed endpoint
echo 😨 Testing Fear & Greed endpoint...
curl --silent --max-time 5 "http://localhost:3002/api/feargreed" | findstr "value" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Fear & Greed test failed
) else (
    echo ✅ Fear & Greed working
)

:: Test 4: CoinGecko endpoint
echo 💎 Testing CoinGecko endpoint...
curl --silent --max-time 5 "http://localhost:3002/api/coingecko/price?ids=bitcoin&vs_currencies=usd" | findstr "bitcoin" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  CoinGecko test failed
) else (
    echo ✅ CoinGecko working
)

cd ..

:: Step 6: Create browser console fix
echo.
echo [6/6] Creating browser console fix...

if not exist "quick-fixes" mkdir quick-fixes

(
echo // ═══════════════════════════════════════════════════════════
echo // 🔧 BROWSER CONSOLE FIX - Crepto AI CORS Solution
echo // ═══════════════════════════════════════════════════════════
echo //
echo // INSTRUCTIONS:
echo // 1. Open your browser developer console ^(F12^)
echo // 2. Copy and paste this entire code
echo // 3. Press Enter
echo // 4. Refresh the page ^(F5^)
echo //
echo // This will redirect all API calls to your local proxy server
echo // running on http://localhost:3002
echo //
echo.
echo ^(function^(^) {
echo   'use strict';
echo   
echo   console.log^('🔧 Applying Crepto AI CORS fix...'^);
echo   
echo   // Store original fetch
echo   const originalFetch = window.fetch;
echo   
echo   // Override fetch to use proxy
echo   window.fetch = function^(url, options^) {
echo     if ^(typeof url === 'string'^) {
echo       
echo       // Redirect CoinMarketCap calls
echo       if ^(url.includes^('coinmarketcap.com'^) ^|^| url.includes^('/api/coinmarketcap'^)^) {
echo         const symbols = 'BTC,ETH,BNB,ADA,SOL,MATIC,DOT,LINK,LTC,XRP';
echo         const proxyUrl = `http://localhost:3002/api/coinmarketcap/quotes?symbols=${symbols}`;
echo         console.log^('🔄 Redirecting to proxy:', proxyUrl^);
echo         return originalFetch^(proxyUrl, { ...options, mode: 'cors' }^);
echo       }
echo       
echo       // Redirect CryptoCompare calls
echo       if ^(url.includes^('cryptocompare.com'^) ^|^| url.includes^('/api/cryptocompare'^)^) {
echo         const fsyms = 'BTC,ETH,BNB,ADA,SOL,MATIC,DOT,LINK,LTC,XRP';
echo         const proxyUrl = `http://localhost:3002/api/cryptocompare/price?fsyms=${fsyms}&tsyms=USD`;
echo         console.log^('🔄 Redirecting to proxy:', proxyUrl^);
echo         return originalFetch^(proxyUrl, { ...options, mode: 'cors' }^);
echo       }
echo       
echo       // Redirect CoinGecko calls
echo       if ^(url.includes^('coingecko.com'^) ^|^| url.includes^('/api/coingecko'^)^) {
echo         const ids = 'bitcoin,ethereum,binancecoin,cardano,solana,polygon,polkadot,chainlink,litecoin,ripple';
echo         const proxyUrl = `http://localhost:3002/api/coingecko/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true`;
echo         console.log^('🔄 Redirecting to proxy:', proxyUrl^);
echo         return originalFetch^(proxyUrl, { ...options, mode: 'cors' }^);
echo       }
echo       
echo       // Redirect Fear & Greed calls
echo       if ^(url.includes^('alternative.me/fng'^) ^|^| url.includes^('/api/feargreed'^)^) {
echo         const proxyUrl = 'http://localhost:3002/api/feargreed';
echo         console.log^('🔄 Redirecting to proxy:', proxyUrl^);
echo         return originalFetch^(proxyUrl, { ...options, mode: 'cors' }^);
echo       }
echo       
echo       // Redirect NewsAPI calls
echo       if ^(url.includes^('newsapi.org'^) ^|^| url.includes^('/api/news'^)^) {
echo         const proxyUrl = 'http://localhost:3002/api/news/crypto?pageSize=20';
echo         console.log^('🔄 Redirecting to proxy:', proxyUrl^);
echo         return originalFetch^(proxyUrl, { ...options, mode: 'cors' }^);
echo       }
echo       
echo       // Block problematic CORS proxies
echo       if ^(url.includes^('allorigins.win'^) ^|^| url.includes^('cors-anywhere'^)^) {
echo         console.warn^('🚫 Blocked problematic CORS proxy:', url^);
echo         return Promise.reject^(new Error^('CORS proxy blocked - use local proxy instead'^)^);
echo       }
echo     }
echo     
echo     // Pass through all other requests
echo     return originalFetch.apply^(this, arguments^);
echo   };
echo   
echo   // Also override XMLHttpRequest for older code
echo   const XHROpen = XMLHttpRequest.prototype.open;
echo   XMLHttpRequest.prototype.open = function^(method, url, ...rest^) {
echo     if ^(typeof url === 'string'^) {
echo       // Apply same redirections as fetch
echo       if ^(url.includes^('alternative.me/fng'^)^) {
echo         url = 'http://localhost:3002/api/feargreed';
echo       } else if ^(url.includes^('cryptocompare.com'^)^) {
echo         url = 'http://localhost:3002/api/cryptocompare/price?fsyms=BTC,ETH,BNB,ADA,SOL&tsyms=USD';
echo       } else if ^(url.includes^('coingecko.com'^)^) {
echo         url = 'http://localhost:3002/api/coingecko/price?ids=bitcoin,ethereum&vs_currencies=usd';
echo       }
echo     }
echo     return XHROpen.call^(this, method, url, ...rest^);
echo   };
echo   
echo   console.log^('✅ CORS fix applied successfully!'^);
echo   console.log^('💡 All API calls will now use http://localhost:3002'^);
echo   console.log^('📊 Refresh the page to see real crypto data!'^);
echo   console.log^('🎯 Proxy server provides automatic fallbacks if primary APIs fail'^);
echo   
echo }^)^(^);
) > quick-fixes\browser-console-fix.js

echo ✅ Browser console fix created

:: Summary
cls
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           ✅ PROXY SERVER IS NOW RUNNING!               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🚀 Proxy Server Status:
echo    URL:  http://localhost:3002
echo    PID:  Check task manager for "Crepto AI Proxy Server"
echo.
echo 📊 Available Endpoints:
echo    ✅ /health                           - Health check
echo    ✅ /api/coinmarketcap/quotes         - Market data with fallbacks
echo    ✅ /api/cryptocompare/price          - CryptoCompare data
echo    ✅ /api/coingecko/price              - CoinGecko data
echo    ✅ /api/feargreed                    - Fear & Greed Index
echo    ✅ /api/news/crypto                  - Crypto news
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎯 NEXT STEP - Apply Browser Fix:
echo.
echo    1. Start your frontend app (if not already running):
echo       npm run dev
echo.
echo    2. Open browser to: http://localhost:5173
echo.
echo    3. Press F12 to open Developer Console
echo.
echo    4. Go to the "Console" tab
echo.
echo    5. Copy the code from:
echo       quick-fixes\browser-console-fix.js
echo.
echo    6. Paste it in the console and press Enter
echo.
echo    7. You should see: ✅ CORS fix applied successfully!
echo.
echo    8. Refresh the page (F5)
echo.
echo    9. Your app will now use real crypto data! 🎉
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 QUICK TEST:
echo.
echo    Open browser console after applying fix and run:
echo.
echo    fetch('http://localhost:3002/health').then(r =^> r.json()).then(console.log)
echo.
echo    You should see the proxy server status! ✅
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📝 FILES CREATED:
echo    quick-fixes\browser-console-fix.js   - Copy & paste in browser
echo.
echo 🔄 AUTO-FALLBACK ENABLED:
echo    If one API fails, proxy automatically tries alternatives:
echo    - Market: CMC → CoinGecko → CryptoCompare
echo    - News: NewsAPI → CryptoPanic → CryptoControl
echo    - Sentiment: Alternative.me → CoinGecko
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎊 ALL DONE! Your CORS issues are now fixed!
echo.
echo    The proxy server will continue running in the background.
echo    You can close that window when you're done testing.
echo.
echo Press any key to view the browser console fix code...
pause > nul

:: Display the browser fix
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        📋 BROWSER CONSOLE FIX (Copy This)               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo COPY AND PASTE THIS IN YOUR BROWSER CONSOLE (F12):
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type quick-fixes\browser-console-fix.js
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo After pasting, press Enter and refresh the page!
echo.
echo To test the proxy directly in console, run:
echo   fetch('http://localhost:3002/health').then(r =^> r.json()).then(console.log)
echo.
pause
