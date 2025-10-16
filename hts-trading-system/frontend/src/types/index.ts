// ==================== CORE DATA TYPES ====================

export interface PriceData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
  timestamp: number;
  bid?: number;
  ask?: number;
  high?: number;
  low?: number;
  open?: number;
}

export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ==================== TECHNICAL INDICATORS ====================

export interface RSIResult {
  rsi: number;
  trend: 'oversold' | 'neutral' | 'overbought';
}

export interface MACDResult {
  macd: number;
  signal: number;
  histogram: number;
  trend: 'bullish' | 'bearish' | 'neutral';
}

export interface BollingerBands {
  upper: number;
  middle: number;
  lower: number;
  width: number;
  percentB: number;
}

export interface StochasticResult {
  k: number;
  d: number;
  trend: 'oversold' | 'neutral' | 'overbought';
}

export interface WilliamsRResult {
  value: number;
  trend: 'oversold' | 'neutral' | 'overbought';
}

export interface TechnicalIndicators {
  rsi: RSIResult;
  macd: MACDResult;
  atr: number;
  sma20: number;
  sma50: number;
  sma200: number;
  bollingerBands: BollingerBands;
  ema12: number;
  ema26: number;
  stochastic: StochasticResult;
  williamsR: WilliamsRResult;
}

// ==================== SENTIMENT ANALYSIS ====================

export interface SentimentData {
  fearGreed: number;
  redditSentiment: number;
  coinGeckoSentiment: number;
  twitterSentiment: number;
  overallScore: number;
  trend: 'extreme fear' | 'fear' | 'neutral' | 'greed' | 'extreme greed';
  confidence: number;
  timestamp: number;
}

// ==================== NEWS & MEDIA ====================

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  image: string;
  published: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  impact: 'high' | 'medium' | 'low';
  tags: string[];
  author?: string;
}

// ==================== WHALE TRACKING ====================

export interface WhaleTransaction {
  id: string;
  blockchain: 'ethereum' | 'bitcoin' | 'bsc' | 'tron' | 'polygon';
  amount: number;
  from: string;
  to: string;
  type: 'buy' | 'sell' | 'transfer';
  timestamp: number;
  txHash: string;
  token: string;
  usdValue: number;
  gasUsed?: number;
  gasPrice?: number;
}

// ==================== AI PREDICTIONS ====================

export interface PredictionData {
  symbol: string;
  bullishProbability: number;
  bearishProbability: number;
  neutralProbability: number;
  confidence: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  riskScore: number;
  priceTarget?: {
    short: number;
    medium: number;
    long: number;
  };
  timeframe: '1h' | '4h' | '1d' | '1w';
  timestamp: number;
  modelVersion: string;
}

// ==================== TRAINING METRICS ====================

export interface TrainingMetrics {
  epoch: number;
  loss: number;
  mse: number;
  mae: number;
  r2Score: number;
  learningRate: number;
  gradientNorm: number;
  validationLoss: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  timestamp: number;
}

// ==================== PORTFOLIO MANAGEMENT ====================

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  allocation: number;
  entryTime: number;
  lastUpdated: number;
  status: 'active' | 'closed' | 'pending';
}

export interface Portfolio {
  totalValue: number;
  totalPnl: number;
  totalPnlPercent: number;
  positions: PortfolioPosition[];
  cash: number;
  lastUpdated: number;
}

// ==================== WEBSOCKET EVENTS ====================

export interface WebSocketPriceUpdate {
  symbol: string;
  currentPrice: number;
  rsi: number;
  rsiTrend: string;
  macd: number;
  signal: number;
  histogram: number;
  macdTrend: string;
  prediction: PredictionData;
  timestamp: number;
}

export interface WebSocketSentimentUpdate {
  sentiment: SentimentData;
  timestamp: number;
}

export interface WebSocketNewsUpdate {
  news: NewsArticle[];
  timestamp: number;
}

export interface WebSocketWhaleUpdate {
  transactions: WhaleTransaction[];
  timestamp: number;
}

// ==================== API RESPONSES ====================

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
  timestamp: number;
}

export interface HealthCheck {
  status: 'OK' | 'ERROR';
  timestamp: string;
  uptime: number;
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  services: {
    binance: boolean;
    redis: boolean;
    websocket: boolean;
  };
}

// ==================== FEATURE FLAGS ====================

export interface FeatureFlag {
  name: string;
  enabled: boolean;
  rolloutPercentage: number;
  userGroups?: string[];
  dependencies?: string[];
  description?: string;
}

export interface FeatureFlags {
  [key: string]: FeatureFlag;
}

// ==================== UTILITY TYPES ====================

export type Timeframe = '1m' | '3m' | '5m' | '15m' | '30m' | '1h' | '2h' | '4h' | '6h' | '8h' | '12h' | '1d' | '3d' | '1w' | '1M';

export type Symbol = 'BTC' | 'ETH' | 'BNB' | 'ADA' | 'SOL' | 'DOT' | 'MATIC' | 'AVAX' | 'LINK' | 'UNI';

export type Signal = 'BUY' | 'SELL' | 'HOLD';

export type Trend = 'bullish' | 'bearish' | 'neutral';

export type Sentiment = 'positive' | 'negative' | 'neutral';

export type Blockchain = 'ethereum' | 'bitcoin' | 'bsc' | 'tron' | 'polygon';

export type ViewType = 'dashboard' | 'charts' | 'training' | 'portfolio' | 'news' | 'settings';

// ==================== COMPONENT PROPS ====================

export interface PriceCardProps {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  isLoading?: boolean;
}

export interface RSIGaugeProps {
  rsi: number;
  trend: string;
  isLoading?: boolean;
}

export interface MACDChartProps {
  data: ChartDataPoint[];
  currentMACD: {
    macd: number;
    signal: number;
    histogram: number;
    trend: string;
  };
  isLoading?: boolean;
}

export interface SentimentGaugeProps {
  score: number;
  fearGreed: number;
  reddit: number;
  coinGecko: number;
  trend: string;
  isLoading?: boolean;
}

export interface AIPredictorProps {
  prediction: PredictionData | null;
  symbol: string;
  isLoading?: boolean;
}

export interface NewsCardProps extends NewsArticle {
  isLoading?: boolean;
}

export interface StatusBarProps {
  connected: boolean;
  lastUpdate: number;
  isLoading?: boolean;
}

export interface NavbarProps {
  activeView: ViewType;
  onViewChange: (view: ViewType) => void;
}

// ==================== CHART DATA ====================

export interface ChartDataPoint {
  time: number;
  macd: number;
  signal: number;
  histogram: number;
}

export interface CandlestickDataPoint {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ==================== WEBSOCKET HOOK TYPES ====================

export interface WebSocketData {
  priceData: Map<string, WebSocketPriceUpdate>;
  sentiment: SentimentData | null;
  news: NewsArticle[];
  connected: boolean;
  lastUpdate: number;
}

// ==================== CONTEXT TYPES ====================

export interface FeatureFlagsContextType {
  flags: FeatureFlags;
  isFeatureEnabled: (featureName: string) => boolean;
  toggleFeature: (featureName: string) => void;
}

// ==================== ERROR TYPES ====================

export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}

// ==================== THEME TYPES ====================

export interface Theme {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
}

// ==================== SETTINGS TYPES ====================

export interface AppSettings {
  theme: Theme;
  autoRefresh: boolean;
  refreshInterval: number;
  notifications: boolean;
  soundEnabled: boolean;
  defaultSymbols: string[];
  chartType: 'candlestick' | 'line' | 'area';
  timeFrame: Timeframe;
}

// ==================== ALERT TYPES ====================

export interface Alert {
  id: string;
  type: 'price' | 'volume' | 'sentiment' | 'news' | 'whale';
  symbol?: string;
  condition: string;
  value: number;
  currentValue: number;
  triggered: boolean;
  timestamp: number;
  message: string;
}

// ==================== STATISTICS TYPES ====================

export interface MarketStatistics {
  totalMarketCap: number;
  totalVolume: number;
  activeCryptocurrencies: number;
  marketDominance: {
    bitcoin: number;
    ethereum: number;
    others: number;
  };
  fearGreedIndex: number;
  totalWhaleTransactions: number;
  averageTransactionSize: number;
}

// ==================== PERFORMANCE TYPES ====================

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkLatency: number;
  errorRate: number;
  uptime: number;
}