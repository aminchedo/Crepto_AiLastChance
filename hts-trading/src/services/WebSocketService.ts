import { Server as SocketIOServer } from 'socket.io';
import BinanceService from './BinanceService';
import IndicatorService from './IndicatorService';
import SentimentService from './SentimentService';
import NewsService from './NewsService';

class WebSocketService {
  private io: SocketIOServer;
  private updateInterval: NodeJS.Timeout | null = null;
  private priceHistory: Map<string, number[]> = new Map();
  private sentiment: any = null;
  private news: any[] = [];

  constructor(io: SocketIOServer) {
    this.io = io;
  }

  // Start real-time monitoring
  async startMonitoring(symbols: string[]): Promise<void> {
    console.log('🚀 Starting monitoring for:', symbols);

    // Initialize price history
    symbols.forEach(symbol => {
      this.priceHistory.set(symbol, []);
    });

    // Fetch initial data
    try {
      for (const symbol of symbols) {
        const candles = await BinanceService.getCandles(symbol, 100);
        const prices = candles.map(c => c.close);
        this.priceHistory.set(symbol, prices);
      }

      // Get initial sentiment and news
      [this.sentiment, this.news] = await Promise.all([
        SentimentService.getAggregatedSentiment(),
        NewsService.getLatestNews(20)
      ]);
    } catch (error) {
      console.error('❌ Error fetching initial data:', error);
    }

    // Connect to Binance WebSocket
    BinanceService.connectWebSocket(symbols, (data) => {
      this.handlePriceUpdate(data, symbols);
    });

    // Emit updates every second
    this.updateInterval = setInterval(() => {
      this.emitUpdates(symbols);
    }, 1000);

    // Refresh sentiment and news every 5 minutes
    setInterval(() => {
      this.refreshSentimentAndNews();
    }, 300000);
  }

  // Handle price updates from WebSocket
  private handlePriceUpdate(data: any, symbols: string[]): void {
    const { symbol, price } = data;

    if (symbols.includes(symbol)) {
      const history = this.priceHistory.get(symbol) || [];

      // Keep last 200 prices
      if (history.length > 200) {
        history.shift();
      }

      history.push(price);
      this.priceHistory.set(symbol, history);
    }
  }

  // Emit data to connected clients
  private emitUpdates(symbols: string[]): void {
    try {
      for (const symbol of symbols) {
        const prices = this.priceHistory.get(symbol) || [];

        if (prices.length < 14) continue;

        // Calculate indicators
        const rsiData = IndicatorService.calculateRSI(prices);
        const macdData = IndicatorService.calculateMACD(prices);

        // Emit to all clients
        this.io.emit('priceUpdate', {
          symbol,
          currentPrice: prices[prices.length - 1],
          rsi: rsiData.rsi,
          rsiTrend: rsiData.trend,
          macd: macdData.macd,
          signal: macdData.signal,
          histogram: macdData.histogram,
          macdTrend: macdData.trend,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('❌ Error emitting updates:', error);
    }
  }

  // Refresh sentiment and news
  private async refreshSentimentAndNews(): Promise<void> {
    try {
      [this.sentiment, this.news] = await Promise.all([
        SentimentService.getAggregatedSentiment(),
        NewsService.getLatestNews(20)
      ]);

      this.io.emit('sentimentUpdate', this.sentiment);
      this.io.emit('newsUpdate', this.news);
    } catch (error) {
      console.error('❌ Error refreshing sentiment/news:', error);
    }
  }

  // Stop monitoring
  stopMonitoring(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    BinanceService.closeWebSocket();
  }
}

export default WebSocketService;