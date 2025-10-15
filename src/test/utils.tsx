import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { FeatureFlagProvider } from '../contexts/FeatureFlagContext';
import { MarketData, CandlestickData, TechnicalIndicators, PredictionData, TrainingMetrics, NewsItem, PortfolioPosition } from '../types';

// Mock data generators
export const createMockMarketData = (overrides: Partial<MarketData> = {}): MarketData => ({
  id: 'bitcoin',
  symbol: 'BTC',
  name: 'Bitcoin',
  price: 43250.75,
  change24h: 1250.30,
  changePercent24h: 2.98,
  volume24h: 28500000000,
  marketCap: 850000000000,
  high24h: 43800.50,
  low24h: 41950.25,
  timestamp: Date.now(),
  ...overrides,
});

export const createMockCandlestickData = (count: number = 100): CandlestickData[] => {
  const data: CandlestickData[] = [];
  const basePrice = 40000;
  
  for (let i = 0; i < count; i++) {
    const time = Date.now() - (i * 60 * 60 * 1000);
    const open = basePrice * (0.98 + Math.random() * 0.04);
    const close = open * (0.995 + Math.random() * 0.01);
    const high = Math.max(open, close) * (1 + Math.random() * 0.01);
    const low = Math.min(open, close) * (0.99 + Math.random() * 0.005);
    const volume = Math.random() * 1000000;
    
    data.push({ time, open, high, low, close, volume });
  }
  
  return data;
};

export const createMockTechnicalIndicators = (overrides: Partial<TechnicalIndicators> = {}): TechnicalIndicators => ({
  rsi: 45 + Math.random() * 30,
  macd: {
    macd: Math.random() * 100 - 50,
    signal: Math.random() * 100 - 50,
    histogram: Math.random() * 20 - 10,
  },
  sma20: 40000 * (0.98 + Math.random() * 0.04),
  sma50: 40000 * (0.96 + Math.random() * 0.08),
  ema12: 40000 * (0.99 + Math.random() * 0.02),
  ema26: 40000 * (0.97 + Math.random() * 0.06),
  bb: {
    upper: 40000 * 1.02,
    middle: 40000,
    lower: 40000 * 0.98,
  },
  ...overrides,
});

export const createMockPredictionData = (overrides: Partial<PredictionData> = {}): PredictionData => ({
  symbol: 'BTC',
  prediction: 'BULL',
  confidence: 0.75,
  bullishProbability: 0.6,
  bearishProbability: 0.25,
  neutralProbability: 0.15,
  riskScore: 0.3,
  timestamp: Date.now(),
  ...overrides,
});

export const createMockTrainingMetrics = (overrides: Partial<TrainingMetrics> = {}): TrainingMetrics => ({
  epoch: 100,
  mse: 0.001234,
  mae: 0.0456,
  r2: 0.789,
  learningRate: 0.001,
  resetEvents: 0,
  timestamp: Date.now(),
  ...overrides,
});

export const createMockNewsItem = (overrides: Partial<NewsItem> = {}): NewsItem => ({
  id: 'news-1',
  title: 'Bitcoin reaches new all-time high',
  description: 'Bitcoin has reached a new all-time high of $50,000, marking a significant milestone in cryptocurrency adoption.',
  url: 'https://example.com/news/bitcoin-ath',
  source: 'CryptoNews',
  publishedAt: new Date().toISOString(),
  sentiment: 'positive',
  impact: 'high',
  ...overrides,
});

export const createMockPortfolioPosition = (overrides: Partial<PortfolioPosition> = {}): PortfolioPosition => ({
  symbol: 'BTC',
  quantity: 0.5,
  averagePrice: 41000,
  currentPrice: 43250,
  pnl: 1125,
  pnlPercent: 5.49,
  allocation: 60.0,
  ...overrides,
});

// Mock feature flag configurations
export const createMockFeatureFlagConfig = (overrides: any = {}) => ({
  flags: {
    'ai-predictions': { id: 'ai-predictions', name: 'AI Predictions', enabled: true, category: 'ai' },
    'portfolio-management': { id: 'portfolio-management', name: 'Portfolio Management', enabled: true, category: 'trading' },
    'real-time-charts': { id: 'real-time-charts', name: 'Real-time Charts', enabled: true, category: 'ui' },
    'news-feed': { id: 'news-feed', name: 'News Feed', enabled: true, category: 'analytics' },
    'training-dashboard': { id: 'training-dashboard', name: 'Training Dashboard', enabled: true, category: 'ai' },
    'advanced-charts': { id: 'advanced-charts', name: 'Advanced Charts', enabled: false, category: 'ui' },
    'backtesting': { id: 'backtesting', name: 'Backtesting', enabled: false, category: 'trading' },
    'risk-management': { id: 'risk-management', name: 'Risk Management', enabled: false, category: 'trading' },
    'whale-tracking': { id: 'whale-tracking', name: 'Whale Tracking', enabled: false, category: 'analytics' },
    'social-sentiment': { id: 'social-sentiment', name: 'Social Sentiment', enabled: false, category: 'analytics' },
    'ai-optimization': { id: 'ai-optimization', name: 'AI Optimization', enabled: false, category: 'ai' },
    'paper-trading': { id: 'paper-trading', name: 'Paper Trading', enabled: false, category: 'trading' },
    'alerts-system': { id: 'alerts-system', name: 'Alerts System', enabled: false, category: 'functionality' },
    'quantum-ai': { id: 'quantum-ai', name: 'Quantum AI', enabled: false, category: 'experimental' },
    'blockchain-analysis': { id: 'blockchain-analysis', name: 'Blockchain Analysis', enabled: false, category: 'experimental' },
    ...overrides.flags,
  },
  userGroups: ['default'],
  environment: 'test',
  userId: 'test-user-123',
  ...overrides,
});

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  featureFlags?: any;
  initialEntries?: string[];
}

export const renderWithProviders = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { featureFlags = {}, ...renderOptions } = options;

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <FeatureFlagProvider initialConfig={createMockFeatureFlagConfig(featureFlags)}>
      {children}
    </FeatureFlagProvider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

// Mock service functions
export const mockMarketDataService = {
  initialize: vi.fn().mockResolvedValue(undefined),
  subscribe: vi.fn().mockReturnValue(() => {}),
  getCandlestickData: vi.fn().mockResolvedValue(createMockCandlestickData()),
  getTechnicalIndicators: vi.fn().mockResolvedValue(createMockTechnicalIndicators()),
  getNews: vi.fn().mockResolvedValue([createMockNewsItem()]),
};

export const mockAIPredictionService = {
  initialize: vi.fn().mockResolvedValue(undefined),
  subscribeToPredictions: vi.fn().mockReturnValue(() => {}),
  subscribeToTraining: vi.fn().mockReturnValue(() => {}),
  getIsTraining: vi.fn().mockReturnValue(false),
  startTraining: vi.fn(),
  stopTraining: vi.fn(),
};

// Test helpers
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const mockLocalStorage = () => {
  const store: Record<string, string> = {};
  
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
  };
};

export const mockFetch = (response: any, status: number = 200) => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(response),
    text: vi.fn().mockResolvedValue(JSON.stringify(response)),
  });
};

export const mockWebSocket = () => {
  const mockWS = {
    close: vi.fn(),
    send: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    readyState: WebSocket.OPEN,
  };
  
  global.WebSocket = vi.fn().mockImplementation(() => mockWS);
  return mockWS;
};

// Test data sets
export const mockMarketData = [
  createMockMarketData({ symbol: 'BTC', name: 'Bitcoin' }),
  createMockMarketData({ symbol: 'ETH', name: 'Ethereum', price: 2650.30 }),
  createMockMarketData({ symbol: 'SOL', name: 'Solana', price: 98.75 }),
];

export const mockPredictions = {
  BTC: createMockPredictionData({ symbol: 'BTC' }),
  ETH: createMockPredictionData({ symbol: 'ETH', prediction: 'BEAR' }),
  SOL: createMockPredictionData({ symbol: 'SOL', prediction: 'NEUTRAL' }),
};

export const mockTrainingHistory = Array.from({ length: 50 }, (_, i) => 
  createMockTrainingMetrics({ 
    epoch: i + 1, 
    mse: 0.01 - (i * 0.0001), 
    r2: 0.5 + (i * 0.01) 
  })
);

export const mockNewsData = [
  createMockNewsItem({
    id: 'news-1',
    title: 'Bitcoin reaches new all-time high',
    sentiment: 'positive',
    impact: 'high',
  }),
  createMockNewsItem({
    id: 'news-2',
    title: 'Market correction expected',
    sentiment: 'negative',
    impact: 'medium',
  }),
  createMockNewsItem({
    id: 'news-3',
    title: 'New regulations announced',
    sentiment: 'neutral',
    impact: 'low',
  }),
];

export const mockPortfolioPositions = [
  createMockPortfolioPosition({ symbol: 'BTC', quantity: 0.5 }),
  createMockPortfolioPosition({ symbol: 'ETH', quantity: 4.2, allocation: 30.0 }),
  createMockPortfolioPosition({ symbol: 'SOL', quantity: 25, allocation: 10.0 }),
];

// Re-export everything from testing library
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';