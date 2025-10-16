import axios, { AxiosResponse } from 'axios';
import WebSocket from 'ws';
import { PriceData, Candle, Timeframe } from '../types/index.js';
import { TradingSystemError } from '../types/index.js';

class BinanceService {
  private baseURL: string;
  private wsURL: string;
  private wsConnections: Map<string, WebSocket> = new Map();
  private requestCount: number = 0;
  private lastResetTime: number = Date.now();
  private rateLimitPerMinute: number;
  private isConnected: boolean = false;

  constructor() {
    this.baseURL = process.env.BINANCE_TESTNET_URL || 'https://testnet.binance.vision/api';
    this.wsURL = process.env.BINANCE_WS_URL || 'wss://stream.testnet.binance.com:9443/ws';
    this.rateLimitPerMinute = parseInt(process.env.RATE_LIMIT_PER_MINUTE || '100');
  }

  // ==================== RATE LIMITING ====================

  private checkRateLimit(): boolean {
    const now = Date.now();
    if (now - this.lastResetTime > 60000) {
      this.requestCount = 0;
      this.lastResetTime = now;
    }
    this.requestCount++;
    return this.requestCount <= this.rateLimitPerMinute;
  }

  // ==================== PRICE DATA ====================

  async getPrices(symbols: string[]): Promise<PriceData[]> {
    if (!this.checkRateLimit()) {
      throw new TradingSystemError(
        'Rate limit exceeded',
        'RATE_LIMIT_EXCEEDED',
        429
      );
    }

    try {
      const prices: PriceData[] = [];

      for (const symbol of symbols) {
        try {
          const response: AxiosResponse = await axios.get(
            `${this.baseURL}/v3/ticker/24hr`,
            {
              params: { symbol: symbol + 'USDT' },
              timeout: 10000,
              headers: {
                'User-Agent': 'HTS-Trading-System/1.0.0'
              }
            }
          );

          const data = response.data;
          prices.push({
            symbol,
            price: parseFloat(data.lastPrice),
            change24h: parseFloat(data.priceChangePercent),
            volume: parseFloat(data.quoteAssetVolume),
            marketCap: parseFloat(data.quoteAssetVolume) * 1000, // Approximate
            timestamp: Date.now(),
            bid: parseFloat(data.bidPrice),
            ask: parseFloat(data.askPrice)
          });
        } catch (error) {
          console.warn(`⚠️ Failed to fetch price for ${symbol}:`, error);
          // Continue with other symbols
        }
      }

      console.log(`✅ Fetched prices for ${prices.length}/${symbols.length} symbols`);
      return prices;
    } catch (error) {
      console.error('❌ Error fetching prices:', error);
      throw new TradingSystemError(
        'Failed to fetch prices from Binance',
        'BINANCE_API_ERROR',
        500,
        error
      );
    }
  }

  // ==================== CANDLESTICK DATA ====================

  async getCandles(
    symbol: string,
    limit: number = 100,
    interval: Timeframe = '5m'
  ): Promise<Candle[]> {
    if (!this.checkRateLimit()) {
      throw new TradingSystemError(
        'Rate limit exceeded',
        'RATE_LIMIT_EXCEEDED',
        429
      );
    }

    try {
      const response: AxiosResponse = await axios.get(
        `${this.baseURL}/v3/klines`,
        {
          params: {
            symbol: symbol + 'USDT',
            interval,
            limit
          },
          timeout: 10000,
          headers: {
            'User-Agent': 'HTS-Trading-System/1.0.0'
          }
        }
      );

      const candles: Candle[] = response.data.map((candle: any[]) => ({
        timestamp: candle[0],
        open: parseFloat(candle[1]),
        high: parseFloat(candle[2]),
        low: parseFloat(candle[3]),
        close: parseFloat(candle[4]),
        volume: parseFloat(candle[7])
      }));

      console.log(`✅ Fetched ${candles.length} candles for ${symbol} (${interval})`);
      return candles;
    } catch (error) {
      console.error(`❌ Error fetching candles for ${symbol}:`, error);
      throw new TradingSystemError(
        `Failed to fetch candles for ${symbol}`,
        'BINANCE_CANDLES_ERROR',
        500,
        error
      );
    }
  }

  // ==================== WEBSOCKET CONNECTION ====================

  connectWebSocket(
    symbols: string[],
    onUpdate: (data: any) => void,
    onError?: (error: Error) => void
  ): void {
    const streams = symbols
      .map(s => `${s.toLowerCase()}usdt@ticker`)
      .join('/');

    const wsUrl = `${this.wsURL}/${streams}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.on('open', () => {
        console.log('✅ Binance WebSocket connected');
        this.isConnected = true;
      });

      ws.on('message', (data: WebSocket.Data) => {
        try {
          const parsed = JSON.parse(data.toString());
          
          // Handle both single and multiple stream data
          const streamData = Array.isArray(parsed) ? parsed : [parsed];
          
          streamData.forEach((data: any) => {
            if (data.e === '24hrTicker') {
              onUpdate({
                symbol: data.s.replace('USDT', ''),
                price: parseFloat(data.c),
                change24h: parseFloat(data.P),
                volume: parseFloat(data.q),
                bid: parseFloat(data.b),
                ask: parseFloat(data.a),
                high: parseFloat(data.h),
                low: parseFloat(data.l),
                open: parseFloat(data.o),
                timestamp: Date.now()
              });
            }
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          onError?.(error as Error);
        }
      });

      ws.on('error', (error: Error) => {
        console.error('❌ WebSocket error:', error);
        this.isConnected = false;
        onError?.(error);
      });

      ws.on('close', (code: number, reason: string) => {
        console.log(`⚠️ WebSocket disconnected (${code}): ${reason}`);
        this.isConnected = false;
        
        // Auto-reconnect after delay
        setTimeout(() => {
          console.log('🔄 Attempting to reconnect WebSocket...');
          this.connectWebSocket(symbols, onUpdate, onError);
        }, parseInt(process.env.WS_RECONNECT_DELAY || '3000'));
      });

      this.wsConnections.set('main', ws);
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      onError?.(error as Error);
    }
  }

  // ==================== CONNECTION MANAGEMENT ====================

  closeWebSocket(): void {
    console.log('🛑 Closing WebSocket connections...');
    this.wsConnections.forEach((ws, key) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    });
    this.wsConnections.clear();
    this.isConnected = false;
  }

  isWebSocketConnected(): boolean {
    return this.isConnected;
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/v3/ping`, {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      console.error('❌ Binance API health check failed:', error);
      return false;
    }
  }

  // ==================== EXCHANGE INFO ====================

  async getExchangeInfo(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseURL}/v3/exchangeInfo`, {
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching exchange info:', error);
      throw new TradingSystemError(
        'Failed to fetch exchange info',
        'BINANCE_EXCHANGE_INFO_ERROR',
        500,
        error
      );
    }
  }

  // ==================== ORDER BOOK ====================

  async getOrderBook(symbol: string, limit: number = 100): Promise<any> {
    if (!this.checkRateLimit()) {
      throw new TradingSystemError(
        'Rate limit exceeded',
        'RATE_LIMIT_EXCEEDED',
        429
      );
    }

    try {
      const response = await axios.get(`${this.baseURL}/v3/depth`, {
        params: {
          symbol: symbol + 'USDT',
          limit
        },
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error(`❌ Error fetching order book for ${symbol}:`, error);
      throw new TradingSystemError(
        `Failed to fetch order book for ${symbol}`,
        'BINANCE_ORDER_BOOK_ERROR',
        500,
        error
      );
    }
  }

  // ==================== RECENT TRADES ====================

  async getRecentTrades(symbol: string, limit: number = 100): Promise<any[]> {
    if (!this.checkRateLimit()) {
      throw new TradingSystemError(
        'Rate limit exceeded',
        'RATE_LIMIT_EXCEEDED',
        429
      );
    }

    try {
      const response = await axios.get(`${this.baseURL}/v3/trades`, {
        params: {
          symbol: symbol + 'USDT',
          limit
        },
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      console.error(`❌ Error fetching recent trades for ${symbol}:`, error);
      throw new TradingSystemError(
        `Failed to fetch recent trades for ${symbol}`,
        'BINANCE_TRADES_ERROR',
        500,
        error
      );
    }
  }
}

export default new BinanceService();