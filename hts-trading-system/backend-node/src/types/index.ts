// Price Data Types
export interface PriceData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
  timestamp: number;
}

// OHLC Candle
export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// RSI Result
export interface RSIResult {
  rsi: number;
  trend: 'oversold' | 'neutral' | 'overbought';
}

// MACD Result
export interface MACDResult {
  macd: number;
  signal: number;
  histogram: number;
  trend: 'bullish' | 'bearish' | 'neutral';
}

// Technical Indicators
export interface TechnicalIndicators {
  rsi: RSIResult;
  macd: MACDResult;
  atr: number;
  sma20: number;
  sma50: number;
  bollingerBands: {
    upper: number;
    middle: number;
    lower: number;
  };
}

// Sentiment Data
export interface SentimentData {
  fearGreed: number;
  redditSentiment: number;
  coinGeckoSentiment: number;
  overallScore: number;
  trend: string;
}

// News Article
export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  image: string;
  published: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

// Whale Transaction
export interface WhaleTransaction {
  id: string;
  blockchain: 'ethereum' | 'bitcoin' | 'bsc' | 'tron';
  amount: number;
  from: string;
  to: string;
  type: 'buy' | 'sell';
  timestamp: number;
  txHash: string;
}

// AI Prediction
export interface PredictionData {
  symbol: string;
  bullishProbability: number;
  bearishProbability: number;
  neutralProbability: number;
  confidence: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  riskScore: number;
  timestamp: number;
}

// Training Metrics
export interface TrainingMetrics {
  epoch: number;
  loss: number;
  mse: number;
  mae: number;
  r2Score: number;
  learningRate: number;
  gradientNorm: number;
  timestamp: number;
}

// Portfolio Position
export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  allocation: number;
}
