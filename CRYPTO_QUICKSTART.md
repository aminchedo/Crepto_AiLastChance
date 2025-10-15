# 🚀 Enhanced Crypto Features - Quick Start Guide

## Overview

This guide will help you quickly get started with the new enhanced crypto features in the Bolt AI Crypto application.

## Prerequisites

- Node.js installed
- npm or yarn package manager
- Internet connection for API calls

## Installation

The required dependencies are already installed:
- ✅ recharts (v2.10.3) - For charts
- ✅ date-fns (v4.1.0) - For date handling
- ✅ lucide-react - For icons

If you need to reinstall:
```bash
npm install
```

## Quick Start

### 1. Start the Application

```bash
npm run dev
```

The application will start at `http://localhost:5173` (or your configured port).

### 2. Access the Enhanced Crypto Dashboard

1. Open your browser to the application URL
2. Look for the **"Enhanced Crypto"** tab in the navigation bar
3. Click on it to access the new dashboard

### 3. Explore the Features

#### Market Overview Tab (Default)
- View real-time prices for BTC, ETH, BNB, SOL, ADA
- See the Fear & Greed Index gauge
- Check top gainers and losers
- Auto-refreshes every 2 minutes

#### Charts Tab
- Select a cryptocurrency (BTC, ETH, BNB, SOL, ADA)
- Choose time range (7d, 30d, 90d, 180d, 365d)
- View interactive price history
- See sentiment analysis

#### Whale Activity Tab
- Monitor large transactions in real-time
- Filter by blockchain, type, or minimum amount
- View transaction statistics
- Updates every 30 seconds

#### News Tab
- Read latest cryptocurrency news
- Filter by sentiment (positive, negative, neutral)
- Click articles to read full content
- Auto-refreshes every 5 minutes

## Features at a Glance

### Real-Time Data
```
✓ Market prices update every 60 seconds
✓ Whale transactions update every 30 seconds
✓ Sentiment analysis updates every 5 minutes
✓ News updates every 5 minutes
```

### Data Sources
```
✓ CoinMarketCap (Primary market data)
✓ CoinGecko (Fallback market data)
✓ CryptoCompare (Historical data)
✓ NewsAPI (News articles)
✓ Reddit (Community sentiment)
✓ Alternative.me (Fear & Greed Index)
✓ Etherscan (Whale transactions)
```

### Key Capabilities
```
✓ Multi-source API integration with fallbacks
✓ Automatic retry on failures
✓ Real-time whale transaction monitoring
✓ Aggregated sentiment analysis
✓ Interactive price charts
✓ News sentiment analysis
```

## Common Use Cases

### 1. Check Market Sentiment
```
1. Go to "Enhanced Crypto" tab
2. View the Fear & Greed gauge in Market Overview
3. Or switch to Charts tab and check sentiment sidebar
```

### 2. Monitor Whale Activity
```
1. Click "Whale Activity" tab
2. Set minimum amount filter (e.g., $5,000,000)
3. Watch for new transactions (green "Live" indicator)
4. Click "View on Explorer" to see transaction details
```

### 3. Track Price History
```
1. Click "Charts" tab
2. Select cryptocurrency from top buttons
3. Choose time range (7d, 30d, etc.)
4. Hover over chart for detailed price info
```

### 4. Stay Updated with News
```
1. Click "News" tab
2. Filter by sentiment if desired
3. Click "Read more" to view full articles
4. Check sentiment indicators for each article
```

## Customization

### Change Refresh Intervals

Edit the hooks in your components:

```typescript
// Faster updates (30 seconds)
const { data } = useMarketData(['BTC', 'ETH'], 30000);

// Slower updates (10 minutes)
const { data } = useNews(20, 600000);
```

### Add More Cryptocurrencies

Edit `CryptoDashboard.tsx`:

```typescript
const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'MATIC', 'DOT'];
```

### Adjust Whale Transaction Threshold

Edit `WhaleFeed.tsx` or use the minimum amount filter in the UI.

## Troubleshooting

### Dashboard Not Loading

**Check 1**: Browser Console
```
Press F12 → Console tab → Look for errors
```

**Check 2**: Network Tab
```
Press F12 → Network tab → Check for failed requests
```

**Check 3**: API Keys
```
Verify keys in: src/config/apiConfig.ts
```

### No Data Showing

**Solution 1**: Wait for Initial Load
```
First load may take 5-10 seconds
```

**Solution 2**: Check Internet Connection
```
All features require internet access
```

**Solution 3**: Refresh Manually
```
Click the "Refresh" button in Market Overview
```

### Whale Transactions Not Updating

**Solution 1**: Wait 30 Seconds
```
First poll happens after 30 seconds
```

**Solution 2**: Check Etherscan API
```
Verify Etherscan key in apiConfig.ts
```

**Solution 3**: Check Console
```
Look for polling errors in browser console
```

## Performance Tips

### 1. Optimize Refresh Intervals
- Don't set intervals too low (< 30 seconds)
- Balance between freshness and API limits

### 2. Use Filters
- Filter whale transactions to reduce data
- Filter news by sentiment to focus on relevant articles

### 3. Close Unused Tabs
- Only keep active tabs open in the dashboard
- Reduces unnecessary API calls

### 4. Clear Cache
- If data seems stale, clear browser cache
- Or wait for automatic cache expiration (5 minutes)

## API Rate Limits

Be aware of rate limits:

```
CoinMarketCap:  333 requests/day
CryptoCompare:  100,000 requests/month
NewsAPI:        1,000 requests/day
CoinGecko:      50 requests/minute
Etherscan:      5 requests/second
```

The application automatically manages these limits with:
- Caching (5-minute cache for news)
- Fallback APIs (switches on primary failure)
- Rate limit tracking (prevents quota exhaustion)

## Advanced Usage

### Access Services Directly

In browser console:

```javascript
// Import orchestrator
import { cryptoDataOrchestrator } from './services/CryptoDataOrchestrator';

// Get market overview
const overview = await cryptoDataOrchestrator.getMarketOverview(['BTC', 'ETH']);

// Get sentiment
const sentiment = await cryptoDataOrchestrator.getSentiment('BTC');

// Get whale statistics
const stats = cryptoDataOrchestrator.getWhaleStatistics();
```

### Monitor API Health

```javascript
// Get service statistics
const stats = cryptoDataOrchestrator.getServicesStats();
console.log(stats);

// Check error tracker
import { errorTracker } from './services/ErrorTracker';
const errors = errorTracker.getErrorStats();
console.log(errors);
```

### Export Data

```javascript
// Export error report
import { errorTracker } from './services/ErrorTracker';
const report = errorTracker.exportReport();
console.log(report);

// Download as JSON
const blob = new Blob([report], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'crypto-api-report.json';
a.click();
```

## Keyboard Shortcuts

While on the Enhanced Crypto dashboard:

```
Tab Navigation:
- 1: Market Overview
- 2: Charts
- 3: Whale Activity
- 4: News

Symbol Selection:
- B: Select BTC
- E: Select ETH
- N: Select BNB
- S: Select SOL
- A: Select ADA

(Note: Shortcuts need to be implemented if desired)
```

## Next Steps

1. **Explore All Tabs**: Check out each tab to see all features
2. **Customize Settings**: Adjust refresh intervals to your needs
3. **Monitor Whale Activity**: Watch for large transactions
4. **Read Documentation**: Check `docs/` folder for detailed info
5. **Integrate with Portfolio**: Connect whale data with your portfolio

## Support

For issues or questions:

1. Check `IMPLEMENTATION_COMPLETE.md` for detailed information
2. Review `docs/CRYPTO_FEATURES_README.md` for feature documentation
3. Check `docs/API_SERVICES.md` for API details
4. Review `docs/HOOKS.md` for hook usage

## Summary

You now have access to:
- ✅ Real-time cryptocurrency market data
- ✅ Whale transaction monitoring
- ✅ Market sentiment analysis
- ✅ Cryptocurrency news aggregation
- ✅ Interactive price charts
- ✅ Multi-source data with automatic fallbacks

**Enjoy exploring the enhanced crypto features!** 🚀

