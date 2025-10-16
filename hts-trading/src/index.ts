import express from 'express';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import BinanceService from './services/BinanceService';
import IndicatorService from './services/IndicatorService';
import SentimentService from './services/SentimentService';
import NewsService from './services/NewsService';
import WebSocketService from './services/WebSocketService';

// Load environment variables
dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: { origin: '*' }
});

const wsService = new WebSocketService(io);
const SYMBOLS = (process.env.SYMBOLS || 'BTC,ETH,BNB').split(',');

// Middleware
app.use(express.json());
app.use(cors());

// Routes
app.get('/api/prices', async (req, res) => {
  try {
    const prices = await BinanceService.getPrices(SYMBOLS);
    res.json(prices);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch prices' });
  }
});

app.get('/api/indicators/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const candles = await BinanceService.getCandles(symbol, 100);
    const prices = candles.map(c => c.close);
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);

    const rsi = IndicatorService.calculateRSI(prices);
    const macd = IndicatorService.calculateMACD(prices);
    const atr = IndicatorService.calculateATR(highs, lows, prices);

    res.json({ rsi, macd, atr });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch indicators' });
  }
});

app.get('/api/sentiment', async (req, res) => {
  try {
    const sentiment = await SentimentService.getAggregatedSentiment();
    res.json(sentiment);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch sentiment' });
  }
});

app.get('/api/news', async (req, res) => {
  try {
    const { limit = 20 } = req.query;
    const news = await NewsService.getLatestNews(parseInt(limit as string));
    res.json(news);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch news' });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// WebSocket connection
io.on('connection', (socket) => {
  console.log(`✅ Client connected: ${socket.id}`);

  socket.on('disconnect', () => {
    console.log(`❌ Client disconnected: ${socket.id}`);
  });
});

// Start server
const PORT = 3002;
httpServer.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║   🚀 HTS Trading System Started        ║
║   Port: ${PORT}                              ║
║   Symbols: ${SYMBOLS.join(', ')}                    ║
║   Status: Ready for connections        ║
╚════════════════════════════════════════╝
  `);

  wsService.startMonitoring(SYMBOLS);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  wsService.stopMonitoring();
  httpServer.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

export default app;