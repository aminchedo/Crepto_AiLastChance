# 🚀 HTS Trading System - Installation Guide

## Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git (optional)

### 1. Clone/Download Project
```bash
# If using git
git clone <repository-url>
cd hts-trading-system

# Or download and extract the project files
```

### 2. Backend Setup
```bash
cd backend
npm install
npm run dev
```

### 3. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3001
- **API Health**: http://localhost:3001/api/health

---

## Detailed Installation

### Backend Installation

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Environment Configuration
The `.env` file is already configured with default values:
```env
PORT=3001
NODE_ENV=development
BINANCE_TESTNET_URL=https://testnet.binance.vision/api
SYMBOLS=BTC,ETH,BNB,ADA,SOL
```

#### 4. Start Backend
```bash
# Development mode
npm run dev

# Production mode
npm run build
npm start
```

#### 5. Verify Backend
```bash
curl http://localhost:3001/api/health
```

### Frontend Installation

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Start Frontend
```bash
# Development mode
npm run dev

# Production build
npm run build
npm run preview
```

#### 4. Verify Frontend
Open http://localhost:5173 in your browser

---

## Project Structure

```
hts-trading-system/
├── backend/
│   ├── src/
│   │   ├── services/          # API services
│   │   │   ├── BinanceService.ts
│   │   │   ├── IndicatorService.ts
│   │   │   ├── SentimentService.ts
│   │   │   ├── NewsService.ts
│   │   │   ├── WhaleTrackingService.ts
│   │   │   ├── AIService.ts
│   │   │   └── WebSocketService.ts
│   │   ├── types/             # TypeScript types
│   │   └── index.ts           # Main server
│   ├── package.json
│   ├── tsconfig.json
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── views/            # Page views
│   │   ├── hooks/            # Custom hooks
│   │   ├── contexts/         # React contexts
│   │   └── types/            # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── README.md
```

---

## Features Overview

### ✅ Implemented Features

#### Backend Services
- **BinanceService**: Real-time price data from Binance testnet
- **IndicatorService**: Technical indicators (RSI, MACD, ATR, Bollinger Bands)
- **SentimentService**: Market sentiment analysis (Fear & Greed Index)
- **NewsService**: Cryptocurrency news aggregation
- **WhaleTrackingService**: Large transaction monitoring
- **AIService**: AI-powered price predictions
- **WebSocketService**: Real-time data streaming

#### Frontend Components
- **PriceCard**: Live cryptocurrency price display
- **RSIGauge**: RSI indicator visualization
- **MACDChart**: MACD chart with histogram
- **SentimentGauge**: Market sentiment display
- **AIPredictor**: AI prediction interface
- **NewsCard**: News article display
- **StatusBar**: Connection status indicator
- **Navbar**: Navigation with feature flags

#### Views
- **DashboardView**: Main trading dashboard
- **ChartView**: Advanced charting tools
- **TrainingView**: AI training monitoring
- **PortfolioView**: Portfolio management
- **NewsView**: News feed with filtering
- **SettingsView**: Feature flag management

#### Advanced Features
- **Feature Flags**: Progressive rollout system
- **WebSocket**: Real-time data updates
- **Responsive Design**: Mobile and desktop optimized
- **Error Handling**: Comprehensive error management
- **Loading States**: Smooth user experience

---

## API Endpoints

### Health & Status
- `GET /api/health` - System health check
- `GET /api/websocket/status` - WebSocket status

### Market Data
- `GET /api/prices` - Current cryptocurrency prices
- `GET /api/indicators/:symbol` - Technical indicators for symbol
- `GET /api/sentiment` - Market sentiment data
- `GET /api/news` - Latest news articles
- `GET /api/whale-transactions` - Whale transaction data

### AI & Predictions
- `GET /api/prediction/:symbol` - AI prediction for symbol
- `GET /api/predictions` - All predictions
- `POST /api/training/start` - Start AI training
- `POST /api/training/stop` - Stop AI training
- `GET /api/training/metrics` - Training metrics
- `GET /api/training/status` - Training status

### Analysis
- `GET /api/whale-analysis/summary` - Whale activity summary
- `GET /api/whale-analysis/alerts` - Whale alerts
- `GET /api/news/statistics` - News statistics

---

## Configuration

### Backend Configuration (.env)
```env
# Server
PORT=3001
NODE_ENV=development
HOST=0.0.0.0

# APIs
BINANCE_TESTNET_URL=https://testnet.binance.vision/api
FEAR_GREED_API=https://api.alternative.me/fng/
NEWS_API_KEY=demo
COINGECKO_API=https://api.coingecko.com/api/v3

# Trading
SYMBOLS=BTC,ETH,BNB,ADA,SOL
DEFAULT_INTERVAL=5m
CACHE_TTL=300

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# WebSocket
WS_HEARTBEAT_INTERVAL=30000
WS_RECONNECT_DELAY=3000
WS_MAX_RECONNECT_ATTEMPTS=5
```

### Frontend Configuration (vite.config.ts)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
  // ... other config
});
```

---

## Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if port 3001 is available
lsof -i :3001

# Kill process if needed
kill -9 <PID>

# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Frontend Won't Start
```bash
# Check if port 5173 is available
lsof -i :5173

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if backend is running
curl http://localhost:3001/api/health
```

#### WebSocket Connection Issues
1. Ensure backend is running on port 3001
2. Check CORS configuration
3. Verify firewall settings
4. Try refreshing the page

#### No Data Showing
1. Check browser console for errors
2. Verify API endpoints are responding
3. Check network connectivity
4. Ensure Binance API is accessible

### Performance Issues

#### Slow Loading
- Check network connection
- Verify API response times
- Clear browser cache
- Check system resources

#### High Memory Usage
- Restart the application
- Check for memory leaks
- Monitor WebSocket connections
- Clear browser cache

---

## Development

### Adding New Features

#### Backend
1. Create new service in `backend/src/services/`
2. Add API endpoint in `backend/src/index.ts`
3. Update types in `backend/src/types/index.ts`
4. Test with `curl` or Postman

#### Frontend
1. Create component in `frontend/src/components/`
2. Add view in `frontend/src/views/`
3. Update types in `frontend/src/types/index.ts`
4. Add feature flag if needed

### Testing

#### Backend Tests
```bash
cd backend
npm test
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### Manual Testing
1. Start both backend and frontend
2. Open browser to http://localhost:5173
3. Check all features work correctly
4. Test WebSocket connection
5. Verify API endpoints

---

## Production Deployment

### Backend Deployment
```bash
cd backend
npm run build
npm start
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## Support

### Getting Help
1. Check this installation guide
2. Review the main README.md
3. Check browser console for errors
4. Verify all dependencies are installed
5. Ensure ports are available

### Common Commands
```bash
# Start everything
cd backend && npm run dev &
cd frontend && npm run dev

# Check status
curl http://localhost:3001/api/health

# View logs
# Backend logs will show in terminal
# Frontend logs in browser console (F12)
```

---

## Next Steps

After successful installation:

1. **Explore the Dashboard** - View real-time cryptocurrency data
2. **Test AI Predictions** - See AI-powered market analysis
3. **Configure Feature Flags** - Enable/disable features in Settings
4. **Monitor WebSocket** - Watch real-time data updates
5. **Customize Settings** - Adjust preferences and configurations

**🎉 Congratulations! Your HTS Trading System is now running!**