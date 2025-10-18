export interface MarketData {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  marketCap: number;
  high24h: number;
  low24h: number;
  timestamp: number;
}

export interface CandlestickData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PredictionData {
  symbol: string;
  bullishProbability: number;
  bearishProbability: number;
  neutralProbability: number;
  confidence: number;
  prediction: 'BULL' | 'BEAR' | 'NEUTRAL';
  riskScore: number;
  timestamp: number;
}

export interface TrainingMetrics {
  epoch: number;
  mse: number;
  mae: number;
  r2: number;
  learningRate: number;
  gradientNorm: number;
  resetEvents: number;
  timestamp: number;
}

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  allocation: number;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  sma20: number;
  sma50: number;
  ema12: number;
  ema26: number;
  bb: {
    upper: number;
    middle: number;
    lower: number;
  };
}

export interface NewsItem {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  impact: 'high' | 'medium' | 'low';
}

// ==================== HTS TRADING SYSTEM TYPES ====================

// Core Data Types
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

// Technical Indicators (Enhanced)
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

// Sentiment Analysis
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

// News & Media (Enhanced)
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

// Whale Tracking
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

// AI Predictions (Enhanced)
export interface PredictionDataEnhanced {
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

// WebSocket Events
export interface WebSocketPriceUpdate {
  symbol: string;
  currentPrice: number;
  rsi: number;
  rsiTrend: string;
  macd: number;
  signal: number;
  histogram: number;
  macdTrend: string;
  prediction: PredictionDataEnhanced;
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

// API Responses
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

// Feature Flags
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

// Utility Types
export type Timeframe = '1m' | '3m' | '5m' | '15m' | '30m' | '1h' | '2h' | '4h' | '6h' | '8h' | '12h' | '1d' | '3d' | '1w' | '1M';
export type Symbol = 'BTC' | 'ETH' | 'BNB' | 'ADA' | 'SOL' | 'DOT' | 'MATIC' | 'AVAX' | 'LINK' | 'UNI';
export type Signal = 'BUY' | 'SELL' | 'HOLD';
export type Trend = 'bullish' | 'bearish' | 'neutral';
export type Sentiment = 'positive' | 'negative' | 'neutral';
export type Blockchain = 'ethereum' | 'bitcoin' | 'bsc' | 'tron' | 'polygon';
export type ViewType = 'dashboard' | 'charts' | 'training' | 'portfolio' | 'news' | 'settings';

// Component Props
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
  prediction: PredictionDataEnhanced | null;
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

// Chart Data
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

// WebSocket Hook Types
export interface WebSocketData {
  priceData: Map<string, WebSocketPriceUpdate>;
  sentiment: SentimentData | null;
  news: NewsArticle[];
  connected: boolean;
  lastUpdate: number;
}

// Context Types
export interface FeatureFlagsContextType {
  flags: FeatureFlags;
  isFeatureEnabled: (featureName: string) => boolean;
  toggleFeature: (featureName: string) => void;
}