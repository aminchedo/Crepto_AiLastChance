import axios from 'axios';
import WebSocket from 'ws';
import { PriceData, Candle } from '../types/index';

class BinanceService {
  private baseURL = 'https://testnet.binance.vision/api';
  private wsURL = 'wss://stream.binance.vision:9443/ws';
  private wsConnections: Map<string, WebSocket> = new Map();
  private requestCount = 0;
  private lastResetTime = Date.now();

  // Rate limiting
  private getRateLimit(): boolean {
    const now = Date.now();
    if (now - this.lastResetTime > 60000) {
      this.requestCount = 0;
      this.lastResetTime = now;
    }
    this.requestCount++;
    return this.requestCount <= 100; // 100 requests per minute
  }

  // Get current prices
  async getPrices(symbols: string[]): Promise<PriceData[]> {
    if (!this.getRateLimit()) {
      console.warn('Rate limit exceeded');
      return [];
    }

    try {
      const prices: PriceData[] = [];

      for (const symbol of symbols) {
        const response = await axios.get(
          `${this.baseURL}/v3/ticker/24hr`,
          {
            params: { symbol: symbol + 'USDT' },
            timeout: 10000
          }
        );

        prices.push({
          symbol,
          price: parseFloat(response.data.lastPrice),
          change24h: parseFloat(response.data.priceChangePercent),
          volume: parseFloat(response.data.quoteAssetVolume),
          marketCap: parseFloat(response.data.quoteAssetVolume) * 1000,
          timestamp: Date.now()
        });
      }

      console.log(`✅ Fetched prices for ${symbols.join(', ')}`);
      return prices;
    } catch (error) {
      console.error('❌ Error fetching prices:', error);
      return [];
    }
  }

  // Get candlestick data
  async getCandles(
    symbol: string,
    limit: number = 100,
    interval: string = '5m'
  ): Promise<Candle[]> {
    if (!this.getRateLimit()) {
      console.warn('Rate limit exceeded');
      return [];
    }

    try {
      const response = await axios.get(
        `${this.baseURL}/v3/klines`,
        {
          params: {
            symbol: symbol + 'USDT',
            interval,
            limit
          },
          timeout: 10000
        }
      );

      return response.data.map((candle: any[]) => ({
        timestamp: candle[0],
        open: parseFloat(candle[1]),
        high: parseFloat(candle[2]),
        low: parseFloat(candle[3]),
        close: parseFloat(candle[4]),
        volume: parseFloat(candle[7])
      }));
    } catch (error) {
      console.error(`❌ Error fetching candles for ${symbol}:`, error);
      return [];
    }
  }

  // Connect to WebSocket
  connectWebSocket(
    symbols: string[],
    onUpdate: (data: any) => void
  ): void {
    const streams = symbols
      .map(s => `${s.toLowerCase()}usdt@ticker`)
      .join('/');

    const wsUrl = `${this.wsURL}/${streams}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.on('open', () => {
        console.log('✅ Binance WebSocket connected');
      });

      ws.on('message', (data: WebSocket.Data) => {
        try {
          const parsed = JSON.parse(data.toString());
          onUpdate({
            symbol: parsed.s.replace('USDT', ''),
            price: parseFloat(parsed.c),
            change24h: parseFloat(parsed.P),
            volume: parseFloat(parsed.q),
            bid: parseFloat(parsed.b),
            ask: parseFloat(parsed.a)
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
      });

      ws.on('close', () => {
        console.log('⚠️ WebSocket disconnected, will reconnect...');
        setTimeout(() => this.connectWebSocket(symbols, onUpdate), 3000);
      });

      this.wsConnections.set('main', ws);
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      setTimeout(() => this.connectWebSocket(symbols, onUpdate), 3000);
    }
  }

  // Close WebSocket
  closeWebSocket(): void {
    this.wsConnections.forEach(ws => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    });
    this.wsConnections.clear();
  }
}

export default new BinanceService();
