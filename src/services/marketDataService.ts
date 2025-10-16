import axios, { AxiosError } from 'axios';
import { handleError, logError } from '../utils/errorHandler';
import { MarketData, CandlestickData, TechnicalIndicators, NewsItem } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    logError('Request Interceptor', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const apiError = handleError(error);
    logError('API Response Error', apiError);
    return Promise.reject(apiError);
  }
);

class MarketDataService {
  private ws: WebSocket | null = null;
  private subscribers: ((data: MarketData[]) => void)[] = [];
  private cache: Map<string, MarketData> = new Map();

  // Supported cryptocurrencies
  private readonly SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
    'MATICUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'XRPUSDT'
  ];

  async initialize(): Promise<void> {
    try {
      await this.loadRealData();
      this.startRealTimeUpdates();
    } catch (error) {
      logError('MarketDataService initialization', error);
      await this.loadFallbackData();
    }
  }

  private async loadRealData(): Promise<void> {
    try {
      // Try to get data from backend API first
      const response = await apiClient.get('/market/overview');
      const marketData = response.data.data || response.data;
      
      if (Array.isArray(marketData)) {
        marketData.forEach(item => this.cache.set(item.symbol, item));
        this.notifySubscribers();
        return;
      }
      
      // Fallback to individual symbol requests
      await this.loadSymbolData();
    } catch (error) {
      logError('loadRealData', error);
      throw error;
    }
  }

  private async loadSymbolData(): Promise<void> {
    const promises = this.SYMBOLS.map(async (symbol) => {
      try {
        const response = await apiClient.get(`/market/${symbol}`);
        const data = response.data.data || response.data;
        if (data && data.symbol) {
          this.cache.set(data.symbol, data);
        }
      } catch (error) {
        logError(`loadSymbolData for ${symbol}`, error);
        // Continue with other symbols
      }
    });

    await Promise.allSettled(promises);
    this.notifySubscribers();
  }

  private async loadFallbackData(): Promise<void> {
    const fallbackData: MarketData[] = [
      {
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
        timestamp: Date.now()
      },
      {
        id: 'ethereum',
        symbol: 'ETH',
        name: 'Ethereum',
        price: 2650.30,
        change24h: 85.20,
        changePercent24h: 3.32,
        volume24h: 15000000000,
        marketCap: 320000000000,
        high24h: 2680.50,
        low24h: 2565.10,
        timestamp: Date.now()
      }
    ];

    fallbackData.forEach(item => this.cache.set(item.symbol, item));
    this.notifySubscribers();
  }

  private startRealTimeUpdates(): void {
    // Update market data every 30 seconds
    setInterval(() => {
      this.refreshMarketData();
    }, 30000);
  }

  private async refreshMarketData(): Promise<void> {
    try {
      await this.loadRealData();
    } catch (error) {
      logError('refreshMarketData', error);
      // Continue with cached data
    }
  }

  subscribe(callback: (data: MarketData[]) => void): () => void {
    this.subscribers.push(callback);

    // Send initial data
    callback(Array.from(this.cache.values()));

    return () => {
      this.subscribers = this.subscribers.filter(sub => sub !== callback);
    };
  }

  private notifySubscribers(): void {
    const data = Array.from(this.cache.values());
    this.subscribers.forEach(callback => callback(data));
  }

  async getMarketData(symbol: string): Promise<MarketData> {
    try {
      const response = await apiClient.get(`/market/${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      logError('getMarketData', error);
      throw error;
    }
  }

  async getCandlestickData(symbol: string, interval: string = '1h'): Promise<CandlestickData[]> {
    try {
      const response = await apiClient.get(`/market/${symbol}/history`, {
        params: { period: interval },
      });
      return response.data.data || response.data;
    } catch (error) {
      logError('getCandlestickData', error);
      // Return mock data as fallback
      return this.generateMockCandlestickData(symbol);
    }
  }

  private generateMockCandlestickData(symbol: string): CandlestickData[] {
    const data: CandlestickData[] = [];
    const basePrice = this.cache.get(symbol)?.price || 40000;

    for (let i = 99; i >= 0; i--) {
      const time = Date.now() - (i * 60 * 60 * 1000);
      const open = basePrice * (0.98 + Math.random() * 0.04);
      const close = open * (0.995 + Math.random() * 0.01);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (0.99 + Math.random() * 0.005);
      const volume = Math.random() * 1000000;
      data.push({ time, open, high, low, close, volume });
    }
    return data;
  }

  async getTechnicalIndicators(symbol: string): Promise<TechnicalIndicators> {
    try {
      const response = await apiClient.get(`/market/${symbol}/indicators`);
      return response.data.data || response.data;
    } catch (error) {
      logError('getTechnicalIndicators', error);
      // Return mock indicators as fallback
      return this.getMockTechnicalIndicators(symbol);
    }
  }

  private getMockTechnicalIndicators(symbol: string): TechnicalIndicators {
    const price = this.cache.get(symbol)?.price || 40000;
    return {
      rsi: 45 + Math.random() * 30,
      macd: {
        macd: Math.random() * 100 - 50,
        signal: Math.random() * 100 - 50,
        histogram: Math.random() * 20 - 10
      },
      sma20: price * (0.98 + Math.random() * 0.04),
      sma50: price * (0.96 + Math.random() * 0.08),
      ema12: price * (0.99 + Math.random() * 0.02),
      ema26: price * (0.97 + Math.random() * 0.06),
      bb: {
        upper: price * 1.02,
        middle: price,
        lower: price * 0.98
      }
    };
  }

  async getNews(): Promise<NewsItem[]> {
    try {
      const response = await apiClient.get('/news');
      const newsData = response.data.data || response.data;
      return Array.isArray(newsData) ? newsData : newsData.articles || [];
    } catch (error) {
      logError('getNews', error);
      return [];
    }
  }

  async getPriceHistory(symbol: string, period: string): Promise<CandlestickData[]> {
    try {
      const response = await apiClient.get(`/market/${symbol}/history`, {
        params: { period },
      });
      return response.data.data || response.data;
    } catch (error) {
      logError('getPriceHistory', error);
      throw error;
    }
  }
}

export const marketDataService = new MarketDataService();
export default apiClient;