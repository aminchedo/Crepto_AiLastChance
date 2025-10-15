# API Services Documentation

## Overview

This document provides detailed information about all API services used in the enhanced crypto features.

## BaseApiService

### Purpose
Foundation class for all API interactions providing retry logic, fallback support, and error handling.

### Key Features
- Automatic retry with exponential backoff (1s, 2s, 4s)
- Fallback to backup APIs
- Request timeout handling (10 seconds default)
- Request logging and statistics

### Methods

#### `request<T>(config, endpoint, options, fallbacks, attempt)`
Main request handler with retry and fallback logic.

**Parameters:**
- `config`: API configuration object
- `endpoint`: API endpoint path
- `options`: Fetch options
- `fallbacks`: Array of fallback configurations
- `attempt`: Current attempt number (internal)

**Returns:** Promise<T>

**Example:**
```typescript
const data = await this.request(
  API_CONFIG.coinmarketcap.primary,
  '/cryptocurrency/quotes/latest?symbol=BTC',
  {},
  [API_CONFIG.coinmarketcap.fallback]
);
```

#### `getStats()`
Get request statistics.

**Returns:**
```typescript
{
  totalRequests: number;
  successRate: number;
  averageLatency: number;
  recentLogs: RequestLog[];
}
```

## EnhancedMarketDataService

### Purpose
Handle cryptocurrency price and market data from multiple sources.

### API Sources
1. **CoinMarketCap** (Primary)
   - Endpoint: `/v1/cryptocurrency/quotes/latest`
   - Rate Limit: 333 requests/day
   - Data: Prices, market cap, volume, changes

2. **CoinGecko** (Fallback)
   - Endpoint: `/api/v3/simple/price`
   - Rate Limit: 50 requests/minute
   - Data: Prices, market data

3. **CryptoCompare** (Historical)
   - Endpoint: `/data/v2/histoday`
   - Rate Limit: 100,000 requests/month
   - Data: Historical prices

### Methods

#### `getCurrentPrices(symbols: string[])`
Get current prices for multiple cryptocurrencies.

**Parameters:**
- `symbols`: Array of symbols (e.g., ['BTC', 'ETH', 'BNB'])

**Returns:** Promise<EnhancedMarketData[]>

**Example:**
```typescript
const prices = await enhancedMarketDataService.getCurrentPrices(['BTC', 'ETH']);
// Returns: [{ symbol: 'BTC', price: 43250.75, ... }, ...]
```

#### `getHistoricalData(symbol: string, days: number)`
Get historical price data.

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `days`: Number of days (max 2000)

**Returns:** Promise<Array<{ time: number; price: number }>>

**Example:**
```typescript
const history = await enhancedMarketDataService.getHistoricalData('BTC', 30);
// Returns: [{ time: 1234567890000, price: 42000 }, ...]
```

#### `getTopMovers(limit: number)`
Get top gainers and losers.

**Parameters:**
- `limit`: Number of results per category (default: 5)

**Returns:** Promise<{ gainers: TopMover[]; losers: TopMover[] }>

**Example:**
```typescript
const movers = await enhancedMarketDataService.getTopMovers(5);
// Returns: { gainers: [...], losers: [...] }
```

#### `getCoinDetails(symbol: string)`
Get detailed information about a coin.

**Parameters:**
- `symbol`: Cryptocurrency symbol

**Returns:** Promise<any>

### Data Structure

```typescript
interface EnhancedMarketData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  marketCap: number;
  high24h?: number;
  low24h?: number;
  lastUpdate: number;
}
```

## NewsService

### Purpose
Aggregate cryptocurrency news from multiple sources with caching.

### API Sources
1. **NewsAPI** (Primary)
   - Endpoint: `/v2/everything`
   - Rate Limit: 1,000 requests/day
   - Data: News articles

2. **Reddit** (Fallback)
   - Endpoint: `/r/CryptoCurrency/hot.json`
   - Rate Limit: Public API
   - Data: Community posts

### Methods

#### `getLatestNews(limit: number)`
Get latest cryptocurrency news.

**Parameters:**
- `limit`: Number of articles (default: 20)

**Returns:** Promise<NewsArticle[]>

**Example:**
```typescript
const news = await newsService.getLatestNews(20);
```

#### `searchNews(query, fromDate, toDate, limit)`
Search news with filters.

**Parameters:**
- `query`: Search query
- `fromDate`: Start date (ISO string)
- `toDate`: End date (ISO string)
- `limit`: Number of results

**Returns:** Promise<NewsArticle[]>

**Example:**
```typescript
const news = await newsService.searchNews('Bitcoin', '2024-01-01', '2024-01-31', 10);
```

#### `getCoinNews(symbol: string, limit: number)`
Get news for specific cryptocurrency.

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `limit`: Number of articles

**Returns:** Promise<NewsArticle[]>

**Example:**
```typescript
const btcNews = await newsService.getCoinNews('BTC', 10);
```

#### `clearCache()`
Clear the in-memory news cache.

### Data Structure

```typescript
interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  urlToImage?: string;
  publishedAt: string;
  source: string;
  author?: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
}
```

### Caching
- Cache Duration: 5 minutes
- Storage: In-memory Map
- Key Format: `${method}_${params}`

## SentimentService

### Purpose
Analyze market sentiment from multiple sources with weighted aggregation.

### API Sources
1. **Alternative.me Fear & Greed Index**
   - Endpoint: `/?limit=1&format=json`
   - Rate Limit: Public API
   - Weight: 40%

2. **Reddit**
   - Endpoint: `/r/CryptoCurrency/hot.json`
   - Rate Limit: Public API
   - Weight: 30%

3. **CoinGecko Community**
   - Endpoint: `/coins/{id}?community_data=true`
   - Rate Limit: 50 requests/minute
   - Weight: 30%

### Methods

#### `getFearGreedIndex()`
Get Fear & Greed Index.

**Returns:** Promise<{ value: number; classification: string }>

**Example:**
```typescript
const fearGreed = await sentimentService.getFearGreedIndex();
// Returns: { value: 65, classification: 'Greed' }
```

#### `getRedditSentiment(subreddit, limit)`
Analyze Reddit sentiment.

**Parameters:**
- `subreddit`: Subreddit name (default: 'CryptoCurrency')
- `limit`: Number of posts (default: 25)

**Returns:** Promise<{ score: number; posts: number; topPosts: any[] }>

**Example:**
```typescript
const reddit = await sentimentService.getRedditSentiment('CryptoCurrency', 25);
```

#### `getCoinGeckoSentiment(coinId)`
Get CoinGecko community sentiment.

**Parameters:**
- `coinId`: CoinGecko coin ID

**Returns:** Promise<{ score: number; metrics: any }>

**Example:**
```typescript
const cg = await sentimentService.getCoinGeckoSentiment('bitcoin');
```

#### `getAggregatedSentiment(symbol)`
Get combined sentiment from all sources.

**Parameters:**
- `symbol`: Cryptocurrency symbol

**Returns:** Promise<SentimentData>

**Example:**
```typescript
const sentiment = await sentimentService.getAggregatedSentiment('BTC');
```

### Data Structure

```typescript
interface SentimentData {
  overall: number; // 0-100 scale
  fearGreed: {
    value: number;
    classification: string;
  };
  reddit: {
    score: number;
    posts: number;
  };
  coinGecko?: {
    score: number;
    metrics: any;
  };
  timestamp: number;
}
```

### Sentiment Calculation
- Overall = (Fear&Greed × 0.4) + (Reddit × 0.3) + (CoinGecko × 0.3)
- Scale: 0-100 (0 = Extreme Fear, 100 = Extreme Greed)

## WhaleTrackingService

### Purpose
Monitor large cryptocurrency transactions in real-time.

### API Sources
1. **Etherscan** (Primary)
   - Endpoint: `?module=account&action=txlist`
   - Rate Limit: 5 requests/second
   - Data: Ethereum transactions

2. **WhaleAlert** (If available)
   - Endpoint: `/v1/transactions`
   - Rate Limit: Varies
   - Data: Multi-chain whale transactions

### Methods

#### `startPolling(interval, callback)`
Start monitoring whale transactions.

**Parameters:**
- `interval`: Polling interval in ms (default: 30000)
- `callback`: Optional callback for new transactions

**Example:**
```typescript
whaleTrackingService.startPolling(30000, (tx) => {
  console.log('New whale transaction:', tx);
});
```

#### `stopPolling()`
Stop monitoring.

**Example:**
```typescript
whaleTrackingService.stopPolling();
```

#### `getRecentTransactions(limit)`
Get recent whale transactions.

**Parameters:**
- `limit`: Number of transactions (default: 20)

**Returns:** WhaleTransaction[]

**Example:**
```typescript
const transactions = whaleTrackingService.getRecentTransactions(20);
```

#### `getStatistics()`
Get transaction statistics.

**Returns:**
```typescript
{
  totalTransactions: number;
  totalVolumeUSD: number;
  averageValueUSD: number;
  byBlockchain: Record<string, number>;
  byType: Record<string, number>;
}
```

### Data Structure

```typescript
interface WhaleTransaction {
  id: string;
  blockchain: string;
  symbol: string;
  amount: number;
  amountUSD: number;
  from: string;
  to: string;
  timestamp: number;
  type: 'transfer' | 'deposit' | 'withdrawal';
  hash: string;
}
```

### Storage
- Type: In-memory array
- Capacity: Last 100 transactions
- Persistence: None (resets on reload)

## CryptoDataOrchestrator

### Purpose
Unified interface to coordinate all crypto services.

### Methods

#### `getMarketOverview(symbols)`
Get comprehensive market overview.

**Parameters:**
- `symbols`: Array of symbols

**Returns:** Promise<MarketOverview>

**Example:**
```typescript
const overview = await cryptoDataOrchestrator.getMarketOverview(['BTC', 'ETH', 'BNB']);
```

#### `getCompleteAssetData(symbol, historicalDays)`
Get all data for one asset.

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `historicalDays`: Days of history (default: 30)

**Returns:** Promise<CompleteAssetData>

**Example:**
```typescript
const assetData = await cryptoDataOrchestrator.getCompleteAssetData('BTC', 30);
```

#### `startRealTimeMonitoring(callbacks)`
Start real-time monitoring.

**Parameters:**
- `callbacks`: Object with callback functions

**Example:**
```typescript
cryptoDataOrchestrator.startRealTimeMonitoring({
  onWhaleTransaction: (tx) => console.log(tx)
});
```

#### `stopRealTimeMonitoring()`
Stop real-time monitoring.

#### `getServicesStats()`
Get health status of all services.

**Returns:**
```typescript
{
  marketData: ServiceStats;
  news: ServiceStats;
  sentiment: ServiceStats;
  whale: ServiceStats;
  isMonitoring: boolean;
}
```

## Error Handling

All services implement comprehensive error handling:

1. **Try-Catch Blocks**: All async operations wrapped
2. **Fallback APIs**: Automatic switch on primary failure
3. **Graceful Degradation**: Return partial data on errors
4. **Error Logging**: All errors logged to console
5. **User Feedback**: Error states returned to UI

## Rate Limiting

Rate limits are enforced at the service level:

```typescript
export const RATE_LIMITS = {
  coinmarketcap: { requests: 333, window: 86400000 },
  cryptocompare: { requests: 100000, window: 2592000000 },
  newsapi: { requests: 1000, window: 86400000 },
  coingecko: { requests: 50, window: 60000 },
  etherscan: { requests: 5, window: 1000 },
  bscscan: { requests: 5, window: 1000 },
};
```

## Best Practices

1. **Always handle errors**: Use try-catch blocks
2. **Respect rate limits**: Don't exceed API quotas
3. **Use caching**: Reduce unnecessary API calls
4. **Implement fallbacks**: Always have backup APIs
5. **Monitor health**: Use ErrorTracker service
6. **Clean up resources**: Stop polling when done
7. **Log requests**: Track API usage
8. **Handle timeouts**: Set appropriate timeout values

