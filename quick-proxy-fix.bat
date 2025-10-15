@echo off
chcp 65001 > nul
title Quick Proxy Fix
color 0E

echo.
echo ╔═══════════════════════════════════════╗
echo ║    🚀 QUICK PROXY FIX                ║
echo ╚═══════════════════════════════════════╝
echo.
echo Starting proxy server...

:: Kill existing process on port 3002
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3002" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start proxy
cd proxy-server
start "Proxy" cmd /k "node server.js"
timeout /t 3 >nul

echo.
echo ✅ Proxy server started on http://localhost:3002
echo.
echo NEXT: Apply browser fix
echo   1. Press F12 in browser
echo   2. Paste this in console:
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo (function() {
echo   const original = window.fetch;
echo   window.fetch = function(url, opts) {
echo     if (typeof url === 'string') {
echo       if (url.includes('alternative.me/fng')) {
echo         return original('http://localhost:3002/api/feargreed', opts);
echo       }
echo       if (url.includes('cryptocompare.com')) {
echo         return original('http://localhost:3002/api/cryptocompare/price?fsyms=BTC,ETH,BNB,ADA,SOL^&tsyms=USD', opts);
echo       }
echo       if (url.includes('coingecko.com')) {
echo         return original('http://localhost:3002/api/coingecko/price?ids=bitcoin,ethereum,binancecoin,cardano,solana^&vs_currencies=usd', opts);
echo       }
echo     }
echo     return original.apply(this, arguments);
echo   };
echo   console.log('✅ CORS fix applied!');
echo })();
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 3. Press Enter in console
echo 4. Refresh page (F5)
echo.
pause
