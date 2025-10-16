// Reuse types from backend
export interface PriceData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
  timestamp: number;
}

export interface TechnicalIndicators {
  rsi: { rsi: number; trend: string };
  macd: { macd: number; signal: number; histogram: number; trend: string };
  atr: number;
  sma20: number;
  sma50: number;
  bollingerBands: {
    upper: number;
    middle: number;
    lower: number;
  };
}

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

export interface SentimentData {
  fearGreed: number;
  redditSentiment: number;
  coinGeckoSentiment: number;
  overallScore: number;
  trend: string;
}

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

export interface PortfolioPosition {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  allocation: number;
}

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
