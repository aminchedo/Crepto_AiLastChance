import express from 'express';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import BinanceService from './services/BinanceService.js';
import IndicatorService from './services/IndicatorService.js';
import SentimentService from './services/SentimentService.js';
import NewsService from './services/NewsService.js';
import WhaleTrackingService from './services/WhaleTrackingService.js';
import AIService from './services/AIService.js';
import WebSocketService from './services/WebSocketService.js';
import { 
  ApiResponse, 
  HealthCheck, 
  TradingSystemError,
  AppConfig 
} from './types/index.js';

// Load environment variables
dotenv.config();

// ==================== CONFIGURATION ====================

const config: AppConfig = {
  port: parseInt(process.env.PORT || '3001'),
  nodeEnv: process.env.NODE_ENV || 'development',
  binanceTestnetUrl: process.env.BINANCE_TESTNET_URL || 'https://testnet.binance.vision/api',
  binanceWsUrl: process.env.BINANCE_WS_URL || 'wss://stream.testnet.binance.com:9443/ws',
  fearGreedApi: process.env.FEAR_GREED_API || 'https://api.alternative.me/fng/',
  newsApiKey: process.env.NEWS_API_KEY || 'demo',
  coinGeckoApi: process.env.COINGECKO_API || 'https://api.coingecko.com/api/v3',
  symbols: (process.env.SYMBOLS || 'BTC,ETH,BNB,ADA,SOL').split(','),
  defaultInterval: process.env.DEFAULT_INTERVAL || '5m',
  cacheTtl: parseInt(process.env.CACHE_TTL || '300'),
  redisEnabled: process.env.REDIS_ENABLED === 'true',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  logLevel: process.env.LOG_LEVEL || 'info',
  rateLimitPerMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || '100'),
  rateLimitBurst: parseInt(process.env.RATE_LIMIT_BURST || '20'),
  wsHeartbeatInterval: parseInt(process.env.WS_HEARTBEAT_INTERVAL || '30000'),
  wsReconnectDelay: parseInt(process.env.WS_RECONNECT_DELAY || '3000'),
  wsMaxReconnectAttempts: parseInt(process.env.WS_MAX_RECONNECT_ATTEMPTS || '5')
};

// ==================== EXPRESS SETUP ====================

const app = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
    credentials: true
  },
  transports: ['websocket', 'polling']
});

// ==================== MIDDLEWARE ====================

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: true
}));

// Request logging
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`${timestamp} ${req.method} ${req.path} - ${req.ip}`);
  next();
});

// ==================== WEBSOCKET SERVICE ====================

const wsService = new WebSocketService(io);

// ==================== API ROUTES ====================

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const [binanceHealth, sentimentHealth, newsHealth, whaleHealth] = await Promise.allSettled([
      BinanceService.healthCheck(),
      SentimentService.healthCheck(),
      NewsService.healthCheck(),
      WhaleTrackingService.healthCheck()
    ]);

    const health: HealthCheck = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
        percentage: Math.round((process.memoryUsage().heapUsed / process.memoryUsage().heapTotal) * 100)
      },
      services: {
        binance: binanceHealth.status === 'fulfilled' ? binanceHealth.value : false,
        redis: false, // Redis not implemented yet
        websocket: wsService.isMonitoring()
      }
    };

    res.json(health);
  } catch (error) {
    console.error('❌ Health check error:', error);
    res.status(500).json({
      status: 'ERROR',
      timestamp: new Date().toISOString(),
      error: 'Health check failed'
    });
  }
});

// Get current prices
app.get('/api/prices', async (req, res) => {
  try {
    const prices = await BinanceService.getPrices(config.symbols);
    const response: ApiResponse<typeof prices> = {
      success: true,
      data: prices,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching prices:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get technical indicators for a symbol
app.get('/api/indicators/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { interval = config.defaultInterval, limit = 100 } = req.query;

    if (!config.symbols.includes(symbol.toUpperCase())) {
      throw new TradingSystemError(
        `Symbol ${symbol} not supported`,
        'UNSUPPORTED_SYMBOL',
        400
      );
    }

    const candles = await BinanceService.getCandles(
      symbol.toUpperCase(),
      parseInt(limit as string),
      interval as string
    );
    const prices = candles.map(c => c.close);

    const indicators = IndicatorService.getAllIndicators(candles, prices);

    const response: ApiResponse<typeof indicators> = {
      success: true,
      data: indicators,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error(`❌ Error fetching indicators for ${req.params.symbol}:`, error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get market sentiment
app.get('/api/sentiment', async (req, res) => {
  try {
    const sentiment = await SentimentService.getAggregatedSentiment();
    const response: ApiResponse<typeof sentiment> = {
      success: true,
      data: sentiment,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching sentiment:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get latest news
app.get('/api/news', async (req, res) => {
  try {
    const { limit = 20, sentiment, impact } = req.query;
    let news;

    if (sentiment) {
      news = await NewsService.getNewsBySentiment(
        sentiment as 'positive' | 'negative' | 'neutral',
        parseInt(limit as string)
      );
    } else if (impact) {
      news = await NewsService.getNewsByImpact(
        impact as 'high' | 'medium' | 'low',
        parseInt(limit as string)
      );
    } else {
      news = await NewsService.getLatestNews(parseInt(limit as string));
    }

    const response: ApiResponse<typeof news> = {
      success: true,
      data: news,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching news:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get whale transactions
app.get('/api/whale-transactions', async (req, res) => {
  try {
    const { limit = 20, blockchain, type, token, minAmount } = req.query;
    let transactions;

    if (blockchain) {
      transactions = await WhaleTrackingService.getTransactionsByBlockchain(
        blockchain as any,
        parseInt(limit as string)
      );
    } else if (type) {
      transactions = await WhaleTrackingService.getTransactionsByType(
        type as 'buy' | 'sell' | 'transfer',
        parseInt(limit as string)
      );
    } else if (token) {
      transactions = await WhaleTrackingService.getTransactionsByToken(
        token as string,
        parseInt(limit as string)
      );
    } else if (minAmount) {
      transactions = await WhaleTrackingService.filterLargeTransfers(
        parseInt(minAmount as string)
      );
    } else {
      transactions = await WhaleTrackingService.getTransactions(parseInt(limit as string));
    }

    const response: ApiResponse<typeof transactions> = {
      success: true,
      data: transactions,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching whale transactions:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get AI prediction for a symbol
app.get('/api/prediction/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;

    if (!config.symbols.includes(symbol.toUpperCase())) {
      throw new TradingSystemError(
        `Symbol ${symbol} not supported`,
        'UNSUPPORTED_SYMBOL',
        400
      );
    }

    const prediction = AIService.getPrediction(symbol.toUpperCase());
    
    if (!prediction) {
      throw new TradingSystemError(
        `No prediction available for ${symbol}`,
        'PREDICTION_NOT_FOUND',
        404
      );
    }

    const response: ApiResponse<typeof prediction> = {
      success: true,
      data: prediction,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error(`❌ Error fetching prediction for ${req.params.symbol}:`, error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Get all predictions
app.get('/api/predictions', (req, res) => {
  try {
    const predictions = AIService.getAllPredictions();
    const response: ApiResponse<typeof predictions> = {
      success: true,
      data: Object.fromEntries(predictions),
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching predictions:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Training endpoints
app.post('/api/training/start', (req, res) => {
  try {
    AIService.startTraining();
    const response: ApiResponse<{ status: string }> = {
      success: true,
      data: { status: 'Training started' },
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error starting training:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

app.post('/api/training/stop', (req, res) => {
  try {
    AIService.stopTraining();
    const response: ApiResponse<{ status: string }> = {
      success: true,
      data: { status: 'Training stopped' },
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error stopping training:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

app.get('/api/training/metrics', (req, res) => {
  try {
    const metrics = AIService.getTrainingMetrics();
    const response: ApiResponse<typeof metrics> = {
      success: true,
      data: metrics,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching training metrics:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

app.get('/api/training/status', (req, res) => {
  try {
    const status = {
      isTraining: AIService.getIsTraining(),
      duration: AIService.getTrainingDuration(),
      modelVersion: AIService.getModelVersion()
    };
    const response: ApiResponse<typeof status> = {
      success: true,
      data: status,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching training status:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// Whale analysis endpoints
app.get('/api/whale-analysis/summary', async (req, res) => {
  try {
    const summary = await WhaleTrackingService.getWhaleActivitySummary();
    const response: ApiResponse<typeof summary> = {
      success: true,
      data: summary,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching whale analysis:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

app.get('/api/whale-analysis/alerts', async (req, res) => {
  try {
    const alerts = await WhaleTrackingService.getWhaleAlerts();
    const response: ApiResponse<typeof alerts> = {
      success: true,
      data: alerts,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching whale alerts:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// News analysis endpoints
app.get('/api/news/statistics', async (req, res) => {
  try {
    const news = await NewsService.getLatestNews(100);
    const statistics = NewsService.getNewsStatistics(news);
    const response: ApiResponse<typeof statistics> = {
      success: true,
      data: statistics,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching news statistics:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// WebSocket status endpoint
app.get('/api/websocket/status', (req, res) => {
  try {
    const status = wsService.healthCheck();
    const response: ApiResponse<typeof status> = {
      success: true,
      data: status,
      timestamp: Date.now()
    };
    res.json(response);
  } catch (error) {
    console.error('❌ Error fetching WebSocket status:', error);
    const response: ApiResponse<null> = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: Date.now()
    };
    res.status(500).json(response);
  }
});

// ==================== ERROR HANDLING ====================

// 404 handler
app.use('*', (req, res) => {
  const response: ApiResponse<null> = {
    success: false,
    data: null,
    error: `Route ${req.originalUrl} not found`,
    timestamp: Date.now()
  };
  res.status(404).json(response);
});

// Global error handler
app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('❌ Unhandled error:', error);
  
  const response: ApiResponse<null> = {
    success: false,
    data: null,
    error: error.message || 'Internal server error',
    timestamp: Date.now()
  };
  
  res.status(500).json(response);
});

// ==================== SERVER STARTUP ====================

const startServer = async () => {
  try {
    // Start WebSocket monitoring
    await wsService.startMonitoring(config.symbols);

    // Start HTTP server
    httpServer.listen(config.port, config.nodeEnv === 'development' ? 'localhost' : '0.0.0.0', () => {
      console.log(`
╔════════════════════════════════════════════════════════════════════════════════╗
║                    🚀 HTS Trading System - Backend Started                    ║
║                                                                                ║
║  📍 Port: ${config.port}                                                           ║
║  🌐 Environment: ${config.nodeEnv}                                                    ║
║  🔄 Symbols: ${config.symbols.join(', ')}                                    ║
║  📊 WebSocket: ${wsService.isMonitoring() ? '✅ Active' : '❌ Inactive'}                                    ║
║  🤖 AI Service: ${AIService.healthCheck() ? '✅ Ready' : '❌ Error'}                                      ║
║                                                                                ║
║  📡 API Endpoints:                                                             ║
║    • Health: http://localhost:${config.port}/api/health                        ║
║    • Prices: http://localhost:${config.port}/api/prices                        ║
║    • Indicators: http://localhost:${config.port}/api/indicators/:symbol        ║
║    • Sentiment: http://localhost:${config.port}/api/sentiment                  ║
║    • News: http://localhost:${config.port}/api/news                            ║
║    • Predictions: http://localhost:${config.port}/api/predictions              ║
║                                                                                ║
║  🔌 WebSocket: ws://localhost:${config.port}                                   ║
║                                                                                ║
║  ✅ Status: Ready for connections                                              ║
╚════════════════════════════════════════════════════════════════════════════════╝
      `);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

// ==================== GRACEFUL SHUTDOWN ====================

const gracefulShutdown = (signal: string) => {
  console.log(`\n🛑 Received ${signal}. Shutting down gracefully...`);
  
  // Stop WebSocket monitoring
  wsService.stopMonitoring();
  
  // Close HTTP server
  httpServer.close(() => {
    console.log('✅ HTTP server closed');
    
    // Close all connections
    process.exit(0);
  });
  
  // Force close after 10 seconds
  setTimeout(() => {
    console.log('⚠️ Forced shutdown');
    process.exit(1);
  }, 10000);
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// ==================== START SERVER ====================

startServer();

export default app;