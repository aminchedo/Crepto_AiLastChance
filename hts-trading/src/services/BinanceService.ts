import axios from 'axios';

interface PriceData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
  timestamp: number;
}

interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

class BinanceService {
  private baseURL = 'https://testnet.binance.vision/api';
  private wsURL = 'wss://stream.testnet.binance.com:9443/ws';
  private wsConnections: Map<string, WebSocket> = new Map();

  // Get current prices
  async getPrices(symbols: string[]): Promise<PriceData[]> {
    try {
      const prices: PriceData[] = [];

      for (const symbol of symbols) {
        const response = await axios.get(
          `${this.baseURL}/v3/ticker/24hr`,
          { params: { symbol: symbol + 'USDT' } }
        );

        prices.push({
          symbol: symbol,
          price: parseFloat(response.data.lastPrice),
          change24h: parseFloat(response.data.priceChangePercent),
          volume: parseFloat(response.data.quoteAssetVolume),
          marketCap: parseFloat(response.data.quoteAssetVolume) || 0,
          timestamp: Date.now()
        });
      }

      return prices;
    } catch (error) {
      console.warn('⚠️ Binance API unavailable, using mock data:', error instanceof Error ? error.message : 'Unknown error');
      // Return mock data when API is unavailable
      return symbols.map(symbol => ({
        symbol: symbol,
        price: this.getMockPrice(symbol),
        change24h: (Math.random() - 0.5) * 10, // Random change between -5% and +5%
        volume: Math.random() * 1000000000,
        marketCap: Math.random() * 100000000000,
        timestamp: Date.now()
      }));
    }
  }

  // Generate mock price data
  private getMockPrice(symbol: string): number {
    const basePrices: { [key: string]: number } = {
      'BTC': 45000 + Math.random() * 10000,
      'ETH': 3000 + Math.random() * 1000,
      'BNB': 300 + Math.random() * 100
    };
    return basePrices[symbol] || 100;
  }

  // Get historical candle data
  async getCandles(
    symbol: string,
    limit: number = 100,
    interval: string = '5m'
  ): Promise<Candle[]> {
    try {
      const response = await axios.get(
        `${this.baseURL}/v3/klines`,
        {
          params: {
            symbol: symbol + 'USDT',
            interval: interval,
            limit: limit
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
      console.warn(`⚠️ Binance API unavailable for ${symbol}, using mock data:`, error instanceof Error ? error.message : 'Unknown error');
      // Return mock candle data
      return this.generateMockCandles(symbol, limit);
    }
  }

  // Generate mock candle data
  private generateMockCandles(symbol: string, limit: number): Candle[] {
    const basePrice = this.getMockPrice(symbol);
    const candles: Candle[] = [];
    let currentPrice = basePrice;

    for (let i = limit; i > 0; i--) {
      const timestamp = Date.now() - (i * 5 * 60 * 1000); // 5 minutes ago
      const change = (Math.random() - 0.5) * 0.02; // ±1% change
      const open = currentPrice;
      const close = currentPrice * (1 + change);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      const volume = Math.random() * 1000000;

      candles.push({
        timestamp,
        open,
        high,
        low,
        close,
        volume
      });

      currentPrice = close;
    }

    return candles;
  }

  // Connect to WebSocket for real-time updates
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

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onUpdate({
            symbol: data.s.replace('USDT', ''),
            price: parseFloat(data.c),
            change24h: parseFloat(data.P),
            volume: parseFloat(data.q),
            bid: parseFloat(data.b),
            ask: parseFloat(data.a)
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('⚠️ WebSocket disconnected, reconnecting...');
        setTimeout(() => this.connectWebSocket(symbols, onUpdate), 3000);
      };

      this.wsConnections.set('main', ws);
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      setTimeout(() => this.connectWebSocket(symbols, onUpdate), 3000);
    }
  }

  // Close WebSocket
  closeWebSocket(): void {
    this.wsConnections.forEach(ws => {
      if (ws) ws.close();
    });
    this.wsConnections.clear();
  }
}

export default new BinanceService();