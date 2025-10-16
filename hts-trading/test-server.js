const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: '*' }
});

app.use(express.json());
app.use(cors());

// Mock data
const mockPrices = {
  'BTC': { price: 45000, change24h: 2.5, volume: 1000000000 },
  'ETH': { price: 3200, change24h: -1.2, volume: 800000000 },
  'BNB': { price: 350, change24h: 3.8, volume: 200000000 }
};

// Routes
app.get('/api/prices', (req, res) => {
  res.json(Object.entries(mockPrices).map(([symbol, data]) => ({
    symbol,
    price: data.price,
    change24h: data.change24h,
    volume: data.volume,
    timestamp: Date.now()
  })));
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// WebSocket
io.on('connection', (socket) => {
  console.log('✅ Client connected:', socket.id);
  
  // Send mock price updates every 2 seconds
  const interval = setInterval(() => {
    Object.entries(mockPrices).forEach(([symbol, data]) => {
      const newPrice = data.price * (1 + (Math.random() - 0.5) * 0.01);
      const newChange = (Math.random() - 0.5) * 10;
      
      socket.emit('priceUpdate', {
        symbol,
        currentPrice: newPrice,
        rsi: 30 + Math.random() * 40,
        rsiTrend: 'neutral',
        macd: (Math.random() - 0.5) * 100,
        signal: (Math.random() - 0.5) * 100,
        histogram: (Math.random() - 0.5) * 50,
        macdTrend: Math.random() > 0.5 ? 'bullish' : 'bearish',
        timestamp: Date.now()
      });
    });
  }, 2000);

  socket.on('disconnect', () => {
    console.log('❌ Client disconnected:', socket.id);
    clearInterval(interval);
  });
});

const PORT = 9999;
httpServer.listen(PORT, () => {
  console.log(`🚀 Test server running on port ${PORT}`);
});