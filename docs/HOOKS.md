# React Hooks Documentation

## Overview

Custom React hooks for managing cryptocurrency data with automatic refresh, error handling, and cleanup.

## Common Pattern

All hooks follow this pattern:

```typescript
interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}
```

## Hooks

### useMarketData

Real-time market data with auto-refresh.

**Signature:**
```typescript
useMarketData(
  symbols: string[],
  refreshInterval?: number
): UseDataResult<EnhancedMarketData[]>
```

**Parameters:**
- `symbols`: Array of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
- `refreshInterval`: Refresh interval in milliseconds (default: 60000 = 1 minute)

**Returns:**
- `data`: Array of market data or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Function to manually refresh data

**Example:**
```typescript
import { useMarketData } from '../hooks/useCryptoData';

function MyComponent() {
  const { data, loading, error, refetch } = useMarketData(
    ['BTC', 'ETH', 'BNB'],
    60000 // Refresh every minute
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {data?.map(coin => (
        <div key={coin.symbol}>
          {coin.symbol}: ${coin.price}
        </div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

**Data Structure:**
```typescript
interface EnhancedMarketData {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  marketCap: number;
  lastUpdate: number;
}
```

---

### useMarketOverview

Comprehensive market overview including prices, sentiment, and top movers.

**Signature:**
```typescript
useMarketOverview(
  symbols?: string[],
  refreshInterval?: number
): UseDataResult<MarketOverview>
```

**Parameters:**
- `symbols`: Array of symbols (default: ['BTC', 'ETH', 'BNB'])
- `refreshInterval`: Refresh interval in ms (default: 120000 = 2 minutes)

**Returns:**
- `data`: Market overview object or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useMarketOverview(
  ['BTC', 'ETH', 'BNB', 'SOL', 'ADA'],
  120000
);
```

**Data Structure:**
```typescript
interface MarketOverview {
  prices: EnhancedMarketData[];
  sentiment: SentimentData;
  topMovers: {
    gainers: TopMover[];
    losers: TopMover[];
  };
  timestamp: number;
}
```

---

### useWhaleFeed

Real-time whale transaction monitoring.

**Signature:**
```typescript
useWhaleFeed(
  pollingInterval?: number
): UseDataResult<WhaleTransaction[]> & { statistics: any }
```

**Parameters:**
- `pollingInterval`: Polling interval in ms (default: 30000 = 30 seconds)

**Returns:**
- `data`: Array of whale transactions or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function
- `statistics`: Transaction statistics

**Example:**
```typescript
const { data, loading, error, statistics } = useWhaleFeed(30000);

console.log('Total transactions:', statistics?.totalTransactions);
console.log('Total volume:', statistics?.totalVolumeUSD);
```

**Data Structure:**
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

**Important Notes:**
- Automatically starts monitoring on mount
- Automatically stops monitoring on unmount
- Updates in real-time via callbacks
- Stores last 50 transactions in state

---

### useSentiment

Market sentiment analysis from multiple sources.

**Signature:**
```typescript
useSentiment(
  symbol?: string,
  refreshInterval?: number
): UseDataResult<SentimentData>
```

**Parameters:**
- `symbol`: Cryptocurrency symbol (default: 'BTC')
- `refreshInterval`: Refresh interval in ms (default: 300000 = 5 minutes)

**Returns:**
- `data`: Sentiment data or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useSentiment('BTC', 300000);

if (data) {
  console.log('Overall sentiment:', data.overall);
  console.log('Fear & Greed:', data.fearGreed.value);
  console.log('Reddit score:', data.reddit.score);
}
```

**Data Structure:**
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

---

### useNews

Cryptocurrency news aggregation.

**Signature:**
```typescript
useNews(
  limit?: number,
  refreshInterval?: number
): UseDataResult<NewsArticle[]>
```

**Parameters:**
- `limit`: Number of articles (default: 20)
- `refreshInterval`: Refresh interval in ms (default: 300000 = 5 minutes)

**Returns:**
- `data`: Array of news articles or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useNews(20, 300000);

return (
  <div>
    {data?.map(article => (
      <div key={article.id}>
        <h3>{article.title}</h3>
        <p>{article.description}</p>
        <span>Sentiment: {article.sentiment}</span>
      </div>
    ))}
  </div>
);
```

**Data Structure:**
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

---

### useHistoricalData

Historical price data for charting.

**Signature:**
```typescript
useHistoricalData(
  symbol: string,
  days?: number
): UseDataResult<Array<{ time: number; price: number }>>
```

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `days`: Number of days of history (default: 30)

**Returns:**
- `data`: Array of price points or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useHistoricalData('BTC', 30);

// Use with Recharts
<LineChart data={data}>
  <Line dataKey="price" />
</LineChart>
```

**Data Structure:**
```typescript
Array<{
  time: number;    // Unix timestamp in milliseconds
  price: number;   // Price in USD
}>
```

**Important Notes:**
- Fetches once on mount (no auto-refresh)
- Refetches when symbol or days changes
- Maximum 2000 days supported

---

### useCompleteAssetData

Complete data for a single asset including prices, sentiment, news, and history.

**Signature:**
```typescript
useCompleteAssetData(
  symbol: string,
  historicalDays?: number
): UseDataResult<CompleteAssetData>
```

**Parameters:**
- `symbol`: Cryptocurrency symbol
- `historicalDays`: Days of price history (default: 30)

**Returns:**
- `data`: Complete asset data or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useCompleteAssetData('BTC', 30);

if (data) {
  console.log('Price:', data.marketData.price);
  console.log('Sentiment:', data.sentiment.overall);
  console.log('News count:', data.news.length);
  console.log('History points:', data.historicalPrices.length);
}
```

**Data Structure:**
```typescript
interface CompleteAssetData {
  marketData: EnhancedMarketData;
  sentiment: SentimentData;
  news: NewsArticle[];
  historicalPrices: Array<{ time: number; price: number }>;
  timestamp: number;
}
```

---

### useNewsAndSentiment

Combined news and sentiment data.

**Signature:**
```typescript
useNewsAndSentiment(
  limit?: number,
  refreshInterval?: number
): UseDataResult<NewsAndSentiment>
```

**Parameters:**
- `limit`: Number of news articles (default: 20)
- `refreshInterval`: Refresh interval in ms (default: 300000 = 5 minutes)

**Returns:**
- `data`: Combined news and sentiment or null
- `loading`: Loading state
- `error`: Error message or null
- `refetch`: Manual refresh function

**Example:**
```typescript
const { data, loading, error } = useNewsAndSentiment(20, 300000);
```

**Data Structure:**
```typescript
interface NewsAndSentiment {
  news: NewsArticle[];
  sentiment: SentimentData;
  timestamp: number;
}
```

---

## Best Practices

### 1. Cleanup

All hooks automatically clean up on unmount:
```typescript
useEffect(() => {
  // Setup
  const interval = setInterval(fetchData, refreshInterval);
  
  // Cleanup
  return () => {
    clearInterval(interval);
  };
}, []);
```

### 2. Error Handling

Always handle errors in your components:
```typescript
const { data, loading, error } = useMarketData(['BTC']);

if (error) {
  return <ErrorMessage message={error} onRetry={refetch} />;
}
```

### 3. Loading States

Show appropriate loading UI:
```typescript
if (loading) {
  return <Skeleton />;
}
```

### 4. Refresh Intervals

Choose appropriate intervals:
- Market prices: 30-60 seconds
- Sentiment: 5-10 minutes
- News: 5-10 minutes
- Whale transactions: 15-30 seconds
- Historical data: No auto-refresh

### 5. Manual Refresh

Provide manual refresh option:
```typescript
<button onClick={refetch}>Refresh</button>
```

### 6. Memoization

Use useMemo for expensive calculations:
```typescript
const processedData = useMemo(() => {
  return data?.map(item => /* expensive operation */);
}, [data]);
```

### 7. Conditional Fetching

Conditionally fetch based on props:
```typescript
const { data } = useMarketData(
  isActive ? ['BTC', 'ETH'] : [],
  isActive ? 60000 : 0
);
```

## Common Patterns

### Pattern 1: Multiple Data Sources

```typescript
function Dashboard() {
  const prices = useMarketData(['BTC', 'ETH']);
  const sentiment = useSentiment('BTC');
  const news = useNews(10);
  
  if (prices.loading || sentiment.loading || news.loading) {
    return <Loading />;
  }
  
  return (
    <div>
      <PriceDisplay data={prices.data} />
      <SentimentGauge data={sentiment.data} />
      <NewsFeed data={news.data} />
    </div>
  );
}
```

### Pattern 2: Conditional Rendering

```typescript
function CoinDetails({ symbol }: { symbol: string }) {
  const { data, loading, error, refetch } = useCompleteAssetData(symbol);
  
  if (loading) return <Skeleton />;
  if (error) return <Error message={error} onRetry={refetch} />;
  if (!data) return <NoData />;
  
  return <Details data={data} />;
}
```

### Pattern 3: Real-Time Updates

```typescript
function WhaleMonitor() {
  const { data, statistics } = useWhaleFeed(30000);
  
  useEffect(() => {
    if (data && data.length > 0) {
      const latestTx = data[0];
      showNotification(`New whale transaction: $${latestTx.amountUSD}`);
    }
  }, [data]);
  
  return <TransactionList transactions={data} />;
}
```

## Performance Tips

1. **Use appropriate refresh intervals** - Don't refresh too frequently
2. **Memoize expensive calculations** - Use useMemo and useCallback
3. **Lazy load components** - Use React.lazy for code splitting
4. **Debounce user inputs** - Prevent excessive API calls
5. **Cache data** - Services implement caching automatically
6. **Clean up subscriptions** - Hooks handle cleanup automatically

## Troubleshooting

### Hook not fetching data
- Check if component is mounted
- Verify refresh interval is > 0
- Check browser console for errors

### Too many API calls
- Increase refresh intervals
- Check for multiple component instances
- Verify cleanup is working

### Stale data
- Decrease refresh interval
- Call refetch() manually
- Clear service caches

### Memory leaks
- Ensure components unmount properly
- Check that intervals are cleared
- Verify whale tracking stops on unmount

