import { Server as SocketIOServer } from 'socket.io';
import BinanceService from './BinanceService';
import IndicatorService from './IndicatorService';
import SentimentService from './SentimentService';
import NewsService from './NewsService';
import WhaleTrackingService from './WhaleTrackingService';
import AIService from './AIService';

class WebSocketService {
  private io: SocketIOServer;
  private updateInterval: NodeJS.Timeout | null = null;
  private priceHistory: Map<string, number[]> = new Map();
  private sentiment: any = null;
  private news: any[] = [];
  private whaleTransactions: any[] = [];

  constructor(io: SocketIOServer) {
    this.io = io;
  }

  async startMonitoring(symbols: string[]): Promise<void> {
    console.log('🚀 Starting WebSocket monitoring for:', symbols.join(', '));

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
      [this.sentiment, this.news, this.whaleTransactions] = await Promise.all([
        SentimentService.getAggregatedSentiment(),
        NewsService.getLatestNews(20),
        WhaleTrackingService.getTransactions(20)
      ]);

      console.log('✅ Initial data loaded');
    } catch (error) {
      console.error('❌ Error loading initial data:', error);
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

    // Refresh whale transactions every 2 minutes
    setInterval(() => {
      this.refreshWhaleTransactions();
    }, 120000);
  }

  private handlePriceUpdate(data: any, symbols: string[]): void {
    const { symbol, price } = data;

    if (symbols.includes(symbol)) {
      const history = this.priceHistory.get(symbol) || [];

      if (history.length > 200) {
        history.shift();
      }

      history.push(price);
      this.priceHistory.set(symbol, history);
    }
  }

  private emitUpdates(symbols: string[]): void {
    try {
      for (const symbol of symbols) {
        const prices = this.priceHistory.get(symbol) || [];

        if (prices.length < 14) continue;

        // Calculate indicators
        const rsiData = IndicatorService.calculateRSI(prices);
        const macdData = IndicatorService.calculateMACD(prices);

        // Generate AI prediction
        const prediction = AIService.generatePrediction(
          symbol,
          rsiData.rsi,
          macdData.macd,
          this.sentiment?.overallScore || 50
        );

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
          prediction,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('❌ Error emitting updates:', error);
    }
  }

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

  private async refreshWhaleTransactions(): Promise<void> {
    try {
      this.whaleTransactions = await WhaleTrackingService.getTransactions(20);
      this.io.emit('whaleUpdate', this.whaleTransactions);
    } catch (error) {
      console.error('❌ Error refreshing whale transactions:', error);
    }
  }

  stopMonitoring(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    BinanceService.closeWebSocket();
  }
}

export default WebSocketService;
