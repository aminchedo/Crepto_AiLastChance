# Enhanced Crypto Features Documentation

## Overview

This document describes the enhanced cryptocurrency features added to the Bolt AI Crypto application. These features provide real-time market data, sentiment analysis, whale transaction monitoring, and news aggregation from multiple API sources.

## Features Added

### 1. Real-Time Market Data
- **Current Prices**: Live cryptocurrency prices from CoinMarketCap, CoinGecko, and CryptoCompare
- **Historical Data**: Price history for multiple time ranges (7d, 30d, 90d, 180d, 365d)
- **Top Movers**: Real-time tracking of top gainers and losers
- **Market Statistics**: 24h volume, market cap, price changes

### 2. Sentiment Analysis
- **Fear & Greed Index**: Market sentiment indicator from Alternative.me
- **Reddit Sentiment**: Community sentiment analysis from r/CryptoCurrency
- **CoinGecko Community**: Social metrics and community engagement
- **Aggregated Score**: Weighted average sentiment from multiple sources

### 3. Whale Transaction Monitoring
- **Real-Time Tracking**: Monitor large cryptocurrency transactions (>$1M)
- **Multiple Blockchains**: Support for Ethereum, Bitcoin, Tron, and BSC
- **Transaction Details**: Amount, addresses, blockchain, transaction type
- **Filtering**: Filter by blockchain, type, and minimum amount
- **Statistics**: Total volume, average transaction size, transaction counts

### 4. News Aggregation
- **Multiple Sources**: NewsAPI, CryptoPanic, Reddit
- **Sentiment Analysis**: Automatic sentiment detection (positive/negative/neutral)
- **Filtering**: Filter news by sentiment
- **Caching**: 5-minute cache to reduce API calls
- **Auto-Refresh**: Updates every 5 minutes

## Architecture

### Service Layer

#### BaseApiService
Foundation for all API interactions with:
- Retry logic with exponential backoff (3 attempts)
- Automatic fallback to backup APIs
- Timeout handling (10 seconds default)
- Request logging and statistics

#### EnhancedMarketDataService
Handles cryptocurrency price and market data:
- **Primary**: CoinMarketCap API
- **Fallbacks**: CoinGecko, CryptoCompare
- **Methods**:
  - `getCurrentPrices(symbols)` - Get current prices
  - `getHistoricalData(symbol, days)` - Get price history
  - `getTopMovers(limit)` - Get top gainers/losers
  - `getCoinDetails(symbol)` - Get detailed coin information

#### NewsService
Aggregates cryptocurrency news:
- **Primary**: NewsAPI
- **Fallbacks**: Reddit
- **Caching**: In-memory cache (5 minutes)
- **Methods**:
  - `getLatestNews(limit)` - Get recent news
  - `searchNews(query, fromDate, toDate)` - Search with filters
  - `getCoinNews(symbol, limit)` - Get coin-specific news

#### SentimentService
Analyzes market sentiment:
- **Sources**: Fear & Greed Index, Reddit, CoinGecko
- **Weighting**: Fear & Greed 40%, Reddit 30%, CoinGecko 30%
- **Methods**:
  - `getFearGreedIndex()` - Get Fear & Greed Index
  - `getRedditSentiment(subreddit, limit)` - Analyze Reddit sentiment
  - `getCoinGeckoSentiment(coinId)` - Get community metrics
  - `getAggregatedSentiment(symbol)` - Get combined sentiment

#### WhaleTrackingService
Monitors large transactions:
- **Polling**: 30-second intervals
- **Sources**: Etherscan (primary), WhaleAlert (if available)
- **Storage**: In-memory (last 100 transactions)
- **Methods**:
  - `startPolling(interval, callback)` - Start monitoring
  - `stopPolling()` - Stop monitoring
  - `getRecentTransactions(limit)` - Get recent transactions
  - `getStatistics()` - Get transaction statistics

#### CryptoDataOrchestrator
Coordinates all services:
- **Parallel Requests**: Uses `Promise.allSettled` for graceful degradation
- **Unified Interface**: Single entry point for all crypto data
- **Methods**:
  - `getMarketOverview(symbols)` - Get comprehensive market data
  - `getCompleteAssetData(symbol)` - Get all data for one asset
  - `getWhaleActivity(limit)` - Get whale transactions
  - `startRealTimeMonitoring(callbacks)` - Start live updates

### React Hooks

#### useMarketData
Real-time price updates with auto-refresh:
```typescript
const { data, loading, error, refetch } = useMarketData(
  ['BTC', 'ETH', 'BNB'],
  60000 // Refresh interval in ms
);
```

#### useMarketOverview
Comprehensive market overview:
```typescript
const { data, loading, error, refetch } = useMarketOverview(
  ['BTC', 'ETH', 'BNB'],
  120000 // 2 minutes
);
```

#### useWhaleFeed
Real-time whale transaction monitoring:
```typescript
const { data, loading, error, statistics } = useWhaleFeed(30000);
```

#### useSentiment
Market sentiment analysis:
```typescript
const { data, loading, error, refetch } = useSentiment('BTC', 300000);
```

#### useNews
Cryptocurrency news:
```typescript
const { data, loading, error, refetch } = useNews(20, 300000);
```

#### useHistoricalData
Price history:
```typescript
const { data, loading, error, refetch } = useHistoricalData('BTC', 30);
```

### Components

#### MarketOverview
Displays market overview with:
- Price cards for major cryptocurrencies
- Fear & Greed gauge with circular progress
- Top gainers and losers

#### PriceChart
Interactive price chart with:
- Historical price visualization using Recharts
- Time range selector (7d, 30d, 90d, 180d, 365d)
- Interactive tooltip
- Price statistics (current, high, low, change)

#### SentimentDashboard
Visual sentiment analysis with:
- Overall sentiment gauge
- Source breakdown (Fear & Greed, Reddit, CoinGecko)
- Progress bars and circular gauges
- Sentiment emoji indicators

#### WhaleFeed
Real-time whale transaction feed with:
- Transaction list with details
- Filters (blockchain, type, minimum amount)
- Statistics dashboard
- Live indicator

#### NewsPanel
Cryptocurrency news panel with:
- News articles with images
- Sentiment filtering
- Source and timestamp
- External links to full articles

#### CryptoDashboard
Main dashboard combining all components with:
- Tab navigation (Overview, Charts, Whale Activity, News)
- Symbol selector
- Responsive grid layout

## API Configuration

### API Keys
All API keys are configured in `src/config/apiConfig.ts`:

```typescript
export const API_CONFIG = {
  coinmarketcap: {
    primary: { key: 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c' },
    fallback: { key: '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1' }
  },
  cryptocompare: {
    primary: { key: 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f' }
  },
  newsapi: {
    primary: { key: 'pub_346789abc123def456789ghi012345jkl' }
  },
  etherscan: {
    primary: { key: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2' },
    fallback: { key: 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45' }
  },
  bscscan: {
    primary: { key: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT' }
  },
  tronscan: {
    primary: { key: '7ae72726-bffe-4e74-9c33-97b761eeea21' }
  }
};
```

### Rate Limits
Rate limits are configured per service:
- CoinMarketCap: 333 requests/day
- CryptoCompare: 100,000 requests/month
- NewsAPI: 1,000 requests/day
- CoinGecko: 50 requests/minute
- Etherscan/BscScan: 5 requests/second

## Usage

### Accessing the Enhanced Crypto Dashboard

1. Start the application:
```bash
npm run dev
```

2. Navigate to the "Enhanced Crypto" tab in the main navigation

3. The dashboard will automatically start fetching data and monitoring whale transactions

### Customizing Refresh Intervals

You can customize refresh intervals in the hooks:

```typescript
// Custom refresh intervals
useMarketData(symbols, 30000);  // 30 seconds
useMarketOverview(symbols, 60000);  // 1 minute
useSentiment('BTC', 600000);  // 10 minutes
useNews(20, 300000);  // 5 minutes
useWhaleFeed(15000);  // 15 seconds
```

### Stopping Real-Time Monitoring

Whale tracking automatically starts when the WhaleFeed component mounts and stops when it unmounts. To manually control:

```typescript
import { cryptoDataOrchestrator } from './services/CryptoDataOrchestrator';

// Start monitoring
cryptoDataOrchestrator.startRealTimeMonitoring({
  onWhaleTransaction: (tx) => console.log('New whale transaction:', tx)
});

// Stop monitoring
cryptoDataOrchestrator.stopRealTimeMonitoring();
```

## Error Handling

### ErrorTracker Service

Monitor API health and track errors:

```typescript
import { errorTracker } from './services/ErrorTracker';

// Get error statistics
const stats = errorTracker.getErrorStats();

// Get service health
const health = errorTracker.getServiceHealth('coinmarketcap');

// Export error report
const report = errorTracker.exportReport();
```

### Graceful Degradation

All services implement graceful degradation:
1. Primary API fails → Try fallback API
2. All APIs fail → Return cached data or empty array
3. Partial failures → Return available data with error indicators

## Performance Optimizations

### Implemented Optimizations

1. **Request Caching**: 5-minute cache for news to reduce API calls
2. **Memoization**: React.memo on expensive components
3. **Parallel Requests**: Promise.allSettled for concurrent API calls
4. **Request Deduplication**: Prevent duplicate simultaneous requests
5. **Efficient Re-rendering**: Only update when data changes
6. **Cleanup**: Proper cleanup of intervals and subscriptions

### Best Practices

1. **Use appropriate refresh intervals**: Don't refresh too frequently
2. **Monitor API usage**: Check rate limits regularly
3. **Handle errors gracefully**: Always provide fallback UI
4. **Clean up subscriptions**: Use useEffect cleanup functions
5. **Optimize bundle size**: Lazy load components when possible

## Troubleshooting

### Common Issues

**Issue**: No data loading
- **Solution**: Check API keys in `apiConfig.ts`
- **Solution**: Check browser console for errors
- **Solution**: Verify internet connection

**Issue**: Rate limit exceeded
- **Solution**: Increase refresh intervals
- **Solution**: Use fallback APIs
- **Solution**: Check RATE_LIMITS configuration

**Issue**: Whale tracking not working
- **Solution**: Verify Etherscan API key
- **Solution**: Check if polling is started
- **Solution**: Look for errors in console

**Issue**: News not loading
- **Solution**: Check NewsAPI key
- **Solution**: Try Reddit fallback
- **Solution**: Clear news cache

### Debug Mode

Enable debug logging:

```typescript
// In browser console
localStorage.setItem('DEBUG', 'true');
```

## Future Enhancements

Potential improvements:
1. WebSocket connections for real-time data
2. More blockchain support for whale tracking
3. Advanced charting with technical indicators
4. Portfolio tracking integration
5. Price alerts and notifications
6. Export data to CSV/JSON
7. Historical sentiment analysis
8. Machine learning predictions

## Support

For issues or questions:
1. Check this documentation
2. Review error logs in ErrorTracker
3. Check API service status
4. Verify API keys and rate limits

## License

This feature set is part of the Bolt AI Crypto application.

