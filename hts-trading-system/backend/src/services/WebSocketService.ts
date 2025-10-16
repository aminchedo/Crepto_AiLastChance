import { Server as SocketIOServer, Socket } from 'socket.io';
import BinanceService from './BinanceService.js';
import IndicatorService from './IndicatorService.js';
import SentimentService from './SentimentService.js';
import NewsService from './NewsService.js';
import WhaleTrackingService from './WhaleTrackingService.js';
import AIService from './AIService.js';
import { 
  WebSocketPriceUpdate, 
  WebSocketSentimentUpdate, 
  WebSocketNewsUpdate, 
  WebSocketWhaleUpdate,
  TechnicalIndicators,
  SentimentData,
  NewsArticle,
  WhaleTransaction
} from '../types/index.js';

class WebSocketService {
  private io: SocketIOServer;
  private updateInterval: NodeJS.Timeout | null = null;
  private priceHistory: Map<string, number[]> = new Map();
  private candleHistory: Map<string, any[]> = new Map();
  private sentiment: SentimentData | null = null;
  private news: NewsArticle[] = [];
  private whaleTransactions: WhaleTransaction[] = [];
  private connectedClients: Set<string> = new Set();
  private symbols: string[] = [];
  private isRunning: boolean = false;

  constructor(io: SocketIOServer) {
    this.io = io;
    this.setupEventHandlers();
  }

  // ==================== EVENT HANDLERS ====================

  private setupEventHandlers(): void {
    this.io.on('connection', (socket: Socket) => {
      console.log(`✅ Client connected: ${socket.id}`);
      this.connectedClients.add(socket.id);

      // Send initial data
      this.sendInitialData(socket);

      // Handle client events
      socket.on('subscribe', (data: { symbols: string[] }) => {
        console.log(`📊 Client ${socket.id} subscribed to:`, data.symbols);
        // Could implement per-client subscriptions here
      });

      socket.on('unsubscribe', (data: { symbols: string[] }) => {
        console.log(`📊 Client ${socket.id} unsubscribed from:`, data.symbols);
      });

      socket.on('request_prediction', (data: { symbol: string }) => {
        const prediction = AIService.getPrediction(data.symbol);
        if (prediction) {
          socket.emit('prediction_update', prediction);
        }
      });

      socket.on('request_training_metrics', () => {
        const metrics = AIService.getTrainingMetrics();
        socket.emit('training_metrics', metrics);
      });

      socket.on('start_training', () => {
        AIService.startTraining();
        socket.emit('training_started', { success: true });
      });

      socket.on('stop_training', () => {
        AIService.stopTraining();
        socket.emit('training_stopped', { success: true });
      });

      socket.on('disconnect', () => {
        console.log(`❌ Client disconnected: ${socket.id}`);
        this.connectedClients.delete(socket.id);
      });

      socket.on('error', (error: Error) => {
        console.error(`❌ Socket error for ${socket.id}:`, error);
      });
    });
  }

  // ==================== INITIAL DATA ====================

  private async sendInitialData(socket: Socket): Promise<void> {
    try {
      // Send current prices
      const prices = await BinanceService.getPrices(this.symbols);
      socket.emit('initial_prices', prices);

      // Send sentiment data
      if (this.sentiment) {
        socket.emit('sentiment_update', this.sentiment);
      }

      // Send news data
      if (this.news.length > 0) {
        socket.emit('news_update', this.news);
      }

      // Send whale transactions
      if (this.whaleTransactions.length > 0) {
        socket.emit('whale_update', this.whaleTransactions);
      }

      // Send training metrics
      const trainingMetrics = AIService.getTrainingMetrics();
      if (trainingMetrics.length > 0) {
        socket.emit('training_metrics', trainingMetrics);
      }

      console.log(`📤 Initial data sent to ${socket.id}`);
    } catch (error) {
      console.error(`❌ Error sending initial data to ${socket.id}:`, error);
    }
  }

  // ==================== MONITORING CONTROL ====================

  async startMonitoring(symbols: string[]): Promise<void> {
    if (this.isRunning) {
      console.log('⚠️ WebSocket monitoring already running');
      return;
    }

    this.symbols = symbols;
    this.isRunning = true;
    console.log('🚀 Starting WebSocket monitoring for:', symbols.join(', '));

    // Initialize price history
    symbols.forEach(symbol => {
      this.priceHistory.set(symbol, []);
      this.candleHistory.set(symbol, []);
    });

    // Load initial data
    await this.loadInitialData();

    // Connect to Binance WebSocket
    BinanceService.connectWebSocket(symbols, (data) => {
      this.handlePriceUpdate(data);
    }, (error) => {
      console.error('❌ Binance WebSocket error:', error);
    });

    // Start update intervals
    this.startUpdateIntervals();

    console.log('✅ WebSocket monitoring started');
  }

  stopMonitoring(): void {
    if (!this.isRunning) {
      console.log('⚠️ WebSocket monitoring not running');
      return;
    }

    this.isRunning = false;

    // Clear intervals
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    // Close Binance WebSocket
    BinanceService.closeWebSocket();

    // Clear data
    this.priceHistory.clear();
    this.candleHistory.clear();
    this.sentiment = null;
    this.news = [];
    this.whaleTransactions = [];

    console.log('🛑 WebSocket monitoring stopped');
  }

  // ==================== INITIAL DATA LOADING ====================

  private async loadInitialData(): Promise<void> {
    try {
      // Load price history for each symbol
      for (const symbol of this.symbols) {
        const candles = await BinanceService.getCandles(symbol, 100);
        const prices = candles.map(c => c.close);
        this.priceHistory.set(symbol, prices);
        this.candleHistory.set(symbol, candles);
      }

      // Load sentiment data
      this.sentiment = await SentimentService.getAggregatedSentiment();

      // Load news data
      this.news = await NewsService.getLatestNews(20);

      // Load whale transactions
      this.whaleTransactions = await WhaleTrackingService.getTransactions(20);

      console.log('✅ Initial data loaded');
    } catch (error) {
      console.error('❌ Error loading initial data:', error);
    }
  }

  // ==================== UPDATE INTERVALS ====================

  private startUpdateIntervals(): void {
    // Price and indicator updates every 1 second
    this.updateInterval = setInterval(() => {
      this.emitPriceUpdates();
    }, 1000);

    // Sentiment updates every 5 minutes
    setInterval(() => {
      this.refreshSentiment();
    }, 300000);

    // News updates every 5 minutes
    setInterval(() => {
      this.refreshNews();
    }, 300000);

    // Whale transactions every 2 minutes
    setInterval(() => {
      this.refreshWhaleTransactions();
    }, 120000);

    // Training metrics every 10 seconds (if training)
    setInterval(() => {
      if (AIService.getIsTraining()) {
        this.emitTrainingMetrics();
      }
    }, 10000);
  }

  // ==================== PRICE UPDATE HANDLING ====================

  private handlePriceUpdate(data: any): void {
    const { symbol, price } = data;

    if (this.symbols.includes(symbol)) {
      const history = this.priceHistory.get(symbol) || [];

      // Add new price to history
      history.push(price);

      // Keep only last 200 prices
      if (history.length > 200) {
        history.shift();
      }

      this.priceHistory.set(symbol, history);
    }
  }

  private emitPriceUpdates(): void {
    if (this.connectedClients.size === 0) return;

    try {
      for (const symbol of this.symbols) {
        const prices = this.priceHistory.get(symbol) || [];
        const candles = this.candleHistory.get(symbol) || [];

        if (prices.length < 14) continue;

        // Calculate technical indicators
        const indicators = IndicatorService.getAllIndicators(candles, prices);

        // Generate AI prediction
        const prediction = AIService.generatePrediction(
          symbol,
          indicators,
          this.sentiment || this.getDefaultSentiment(),
          prices
        );

        // Create price update
        const priceUpdate: WebSocketPriceUpdate = {
          symbol,
          currentPrice: prices[prices.length - 1],
          rsi: indicators.rsi.rsi,
          rsiTrend: indicators.rsi.trend,
          macd: indicators.macd.macd,
          signal: indicators.macd.signal,
          histogram: indicators.macd.histogram,
          macdTrend: indicators.macd.trend,
          prediction,
          timestamp: Date.now()
        };

        // Emit to all connected clients
        this.io.emit('price_update', priceUpdate);
      }
    } catch (error) {
      console.error('❌ Error emitting price updates:', error);
    }
  }

  // ==================== DATA REFRESH METHODS ====================

  private async refreshSentiment(): Promise<void> {
    try {
      this.sentiment = await SentimentService.getAggregatedSentiment();
      
      const sentimentUpdate: WebSocketSentimentUpdate = {
        sentiment: this.sentiment,
        timestamp: Date.now()
      };

      this.io.emit('sentiment_update', sentimentUpdate);
      console.log('📊 Sentiment data refreshed');
    } catch (error) {
      console.error('❌ Error refreshing sentiment:', error);
    }
  }

  private async refreshNews(): Promise<void> {
    try {
      this.news = await NewsService.getLatestNews(20);
      
      const newsUpdate: WebSocketNewsUpdate = {
        news: this.news,
        timestamp: Date.now()
      };

      this.io.emit('news_update', newsUpdate);
      console.log('📰 News data refreshed');
    } catch (error) {
      console.error('❌ Error refreshing news:', error);
    }
  }

  private async refreshWhaleTransactions(): Promise<void> {
    try {
      this.whaleTransactions = await WhaleTrackingService.getTransactions(20);
      
      const whaleUpdate: WebSocketWhaleUpdate = {
        transactions: this.whaleTransactions,
        timestamp: Date.now()
      };

      this.io.emit('whale_update', whaleUpdate);
      console.log('🐋 Whale transaction data refreshed');
    } catch (error) {
      console.error('❌ Error refreshing whale transactions:', error);
    }
  }

  private emitTrainingMetrics(): void {
    try {
      const metrics = AIService.getTrainingMetrics();
      if (metrics.length > 0) {
        this.io.emit('training_metrics', metrics);
      }
    } catch (error) {
      console.error('❌ Error emitting training metrics:', error);
    }
  }

  // ==================== UTILITY METHODS ====================

  private getDefaultSentiment(): SentimentData {
    return {
      fearGreed: 50,
      redditSentiment: 50,
      coinGeckoSentiment: 50,
      twitterSentiment: 50,
      overallScore: 50,
      trend: 'neutral',
      confidence: 50,
      timestamp: Date.now()
    };
  }

  // ==================== STATUS METHODS ====================

  getConnectedClientsCount(): number {
    return this.connectedClients.size;
  }

  isMonitoring(): boolean {
    return this.isRunning;
  }

  getSymbols(): string[] {
    return [...this.symbols];
  }

  // ==================== BROADCAST METHODS ====================

  broadcastToAll(event: string, data: any): void {
    this.io.emit(event, data);
  }

  broadcastToRoom(room: string, event: string, data: any): void {
    this.io.to(room).emit(event, data);
  }

  sendToClient(clientId: string, event: string, data: any): void {
    this.io.to(clientId).emit(event, data);
  }

  // ==================== ROOM MANAGEMENT ====================

  joinRoom(socketId: string, room: string): void {
    this.io.sockets.sockets.get(socketId)?.join(room);
  }

  leaveRoom(socketId: string, room: string): void {
    this.io.sockets.sockets.get(socketId)?.leave(room);
  }

  // ==================== HEALTH CHECK ====================

  healthCheck(): {
    isRunning: boolean;
    connectedClients: number;
    symbols: string[];
    binanceConnected: boolean;
  } {
    return {
      isRunning: this.isRunning,
      connectedClients: this.connectedClients.size,
      symbols: this.symbols,
      binanceConnected: BinanceService.isWebSocketConnected()
    };
  }
}

export default WebSocketService;