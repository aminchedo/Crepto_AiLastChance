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
  stochastic: {
    k: number;
    d: number;
    trend: 'oversold' | 'neutral' | 'overbought';
  };
  williamsR: {
    value: number;
    trend: 'oversold' | 'neutral' | 'overbought';
  };
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

// ==================== CONFIGURATION ====================

export interface AppConfig {
  port: number;
  nodeEnv: string;
  binanceTestnetUrl: string;
  binanceWsUrl: string;
  fearGreedApi: string;
  newsApiKey: string;
  coinGeckoApi: string;
  symbols: string[];
  defaultInterval: string;
  cacheTtl: number;
  redisEnabled: boolean;
  redisUrl: string;
  logLevel: string;
  rateLimitPerMinute: number;
  rateLimitBurst: number;
  wsHeartbeatInterval: number;
  wsReconnectDelay: number;
  wsMaxReconnectAttempts: number;
}

// ==================== ERROR TYPES ====================

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}

export class TradingSystemError extends Error {
  public code: string;
  public statusCode: number;
  public details?: any;

  constructor(
    message: string,
    code: string = 'UNKNOWN_ERROR',
    statusCode: number = 500,
    details?: any
  ) {
    super(message);
    this.name = 'TradingSystemError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }
}

// ==================== UTILITY TYPES ====================

export type Timeframe = '1m' | '3m' | '5m' | '15m' | '30m' | '1h' | '2h' | '4h' | '6h' | '8h' | '12h' | '1d' | '3d' | '1w' | '1M';

export type Symbol = 'BTC' | 'ETH' | 'BNB' | 'ADA' | 'SOL' | 'DOT' | 'MATIC' | 'AVAX' | 'LINK' | 'UNI';

export type Signal = 'BUY' | 'SELL' | 'HOLD';

export type Trend = 'bullish' | 'bearish' | 'neutral';

export type Sentiment = 'positive' | 'negative' | 'neutral';

export type Blockchain = 'ethereum' | 'bitcoin' | 'bsc' | 'tron' | 'polygon';

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