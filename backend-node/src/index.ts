import express from 'express';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import BinanceService from './services/BinanceService';
import IndicatorService from './services/IndicatorService';
import SentimentService from './services/SentimentService';
import NewsService from './services/NewsService';
import WhaleTrackingService from './services/WhaleTrackingService';
import AIService from './services/AIService';
import WebSocketService from './services/WebSocketService';

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: { origin: '*' },
  transports: ['websocket', 'polling']
});

const wsService = new WebSocketService(io);
const SYMBOLS = (process.env.SYMBOLS || 'BTC,ETH,BNB').split(',');

// Middleware
app.use(express.json());
app.use(cors());

// ==================== API ROUTES ====================

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Get prices
app.get('/api/prices', async (req, res) => {
  try {
    const prices = await BinanceService.getPrices(SYMBOLS);
    res.json(prices);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch prices' });
  }
});

// Get indicators for symbol
app.get('/api/indicators/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const candles = await BinanceService.getCandles(symbol, 100);
    const prices = candles.map(c => c.close);

    const indicators = IndicatorService.getAllIndicators(candles, prices);
    res.json(indicators);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch indicators' });
  }
});

// Get sentiment
app.get('/api/sentiment', async (req, res) => {
  try {
    const sentiment = await SentimentService.getAggregatedSentiment();
    res.json(sentiment);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch sentiment' });
  }
});

// Get news
app.get('/api/news', async (req, res) => {
  try {
    const { limit = '20' } = req.query;
    const news = await NewsService.getLatestNews(parseInt(limit as string));
    res.json(news);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch news' });
  }
});

// Get whale transactions
app.get('/api/whale-transactions', async (req, res) => {
  try {
    const { limit = '20' } = req.query;
    const transactions = await WhaleTrackingService.getTransactions(
      parseInt(limit as string)
    );
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch transactions' });
  }
});

// Get AI prediction
app.get('/api/prediction/:symbol', (req, res) => {
  try {
    const { symbol } = req.params;
    const prediction = AIService.getPrediction(symbol);
    if (prediction) {
      res.json(prediction);
    } else {
      res.status(404).json({ error: 'Prediction not found' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch prediction' });
  }
});

// Start training
app.post('/api/training/start', (req, res) => {
  AIService.startTraining();
  res.json({ status: 'Training started' });
});

// Stop training
app.post('/api/training/stop', (req, res) => {
  AIService.stopTraining();
  res.json({ status: 'Training stopped' });
});

// Get training metrics
app.get('/api/training/metrics', (req, res) => {
  const metrics = AIService.getTrainingMetrics();
  res.json(metrics);
});

// ==================== WEBSOCKET ====================

io.on('connection', (socket) => {
  console.log(`✅ Client connected: ${socket.id}`);

  socket.on('disconnect', () => {
    console.log(`❌ Client disconnected: ${socket.id}`);
  });

  socket.on('error', (error) => {
    console.error('Socket error:', error);
  });
});

// ==================== START SERVER ====================

const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════╗
║   🚀 HTS Trading System - Backend Started              ║
║   📍 Port: ${PORT}                                        ║
║   🔄 Symbols: ${SYMBOLS.join(', ')}                        ║
║   ✅ Status: Ready for connections                     ║
╚════════════════════════════════════════════════════════╝
  `);

  wsService.startMonitoring(SYMBOLS);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 Shutting down gracefully...');
  wsService.stopMonitoring();
  httpServer.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

export default app;
