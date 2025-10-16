<<<<<<< HEAD
# HTS Trading System - Hybrid Trading System + Bolt AI Crypto

## 🚀 Professional-Grade Algorithmic Cryptocurrency Trading System

A complete, production-ready cryptocurrency trading analysis platform built with **Node.js/TypeScript** backend and **React/TypeScript** frontend.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Phase 2 Roadmap](#phase-2-roadmap)

---

## ✨ Features

### Phase 1 - Core Foundation (✅ COMPLETE)

**Real-time Market Analysis:**
- ✅ Live prices from Binance testnet
- ✅ Technical indicators (RSI, MACD, ATR, SMA, Bollinger Bands)
- ✅ WebSocket real-time updates
- ✅ Price charts with candlesticks

**Advanced Analytics:**
- ✅ Market sentiment (Fear & Greed Index)
- ✅ News aggregation with sentiment analysis
- ✅ Whale transaction tracking
- ✅ Portfolio P&L tracking

**AI Predictions:**
- ✅ Machine learning-based price predictions
- ✅ Multi-symbol forecasting
- ✅ Training simulation
- ✅ Risk assessment

**User Interface:**
- ✅ Professional trading dashboard
- ✅ Real-time data updates
- ✅ Feature flags for progressive rollout
- ✅ Responsive design (desktop/mobile)
- ✅ Dark theme optimized

---

## 🛠️ Technology Stack

### Backend
- **Runtime:** Node.js 18+
- **Framework:** Express.js
- **Language:** TypeScript
- **Real-time:** Socket.io
- **HTTP Client:** Axios
- **APIs:** Binance Testnet, Fear & Greed, NewsAPI

### Frontend
- **Framework:** React 18+
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Icons:** Lucide React
- **Real-time:** Socket.io-client

---
=======
# 🚀 HTS Trading System + Bolt AI Crypto

A professional-grade algorithmic cryptocurrency trading system with real-time market analysis, AI predictions, and advanced technical indicators.

## 🎯 Features

### Real-time Market Analysis
- Live prices from Binance testnet
- Technical indicators (RSI, MACD, ATR, Bollinger Bands)
- Price charts with candlesticks
- WebSocket real-time updates

### Advanced Analytics
- Market sentiment (Fear & Greed Index)
- News aggregation with sentiment analysis
- Whale transaction tracking
- Portfolio P&L tracking

### AI Predictions
- Machine learning-based price predictions
- Multi-symbol forecasting
- Training simulation
- Risk assessment

### Professional UI
- Dark-themed responsive dashboard
- Real-time data updates
- Feature flags for progressive rollout
- Mobile/desktop optimized
>>>>>>> 44c995af8c1e645205c1ee3e41e3890b3d6fc75a

## 🏗️ Architecture

```
<<<<<<< HEAD
┌─────────────────────────────────────────┐
│     Browser (React Frontend)            │
│  ├─ Dashboard View                      │
│  ├─ Training View                       │
│  ├─ Portfolio View                      │
│  ├─ Charts & Analysis                   │
│  ├─ News Feed                           │
│  └─ Settings                            │
└─────────────────────────────────────────┘
           ↕ WebSocket + REST API
┌─────────────────────────────────────────┐
│     Node.js Backend (Express)           │
│  ├─ BinanceService                      │
│  ├─ IndicatorService                    │
│  ├─ SentimentService                    │
│  ├─ NewsService                         │
│  ├─ WhaleTrackingService                │
│  ├─ AIPredictionService                 │
│  └─ WebSocketService                    │
└─────────────────────────────────────────┘
           ↕
┌─────────────────────────────────────────┐
│     Multiple Data Sources               │
│  ├─ Binance Testnet API                 │
│  ├─ Alternative.me (Fear & Greed)       │
│  ├─ NewsAPI                             │
│  └─ Mock Data (Demo Mode)               │
└─────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites
- Node.js 18+ ([Download](https://nodejs.org/))
- npm or yarn
- Git (optional)

### Step 1: Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd hts-trading-system

# Or download and extract ZIP
cd hts-trading-system
```

### Step 2: Backend Setup

```bash
cd backend-node

# Install dependencies
npm install

# Configuration is already set in .env file
# Verify .env contains:
# PORT=3001
# SYMBOLS=BTC,ETH,BNB

# Build TypeScript (optional)
npm run build
```

### Step 3: Frontend Setup

```bash
cd ../frontend-react

# Install dependencies
npm install

# Configuration is already set in vite.config.ts
```

---

## 🚀 Running the Application

### Option 1: Development Mode (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend-node
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend-react
npm run dev
```

### Option 2: Production Build

**Backend:**
```bash
cd backend-node
npm run build
npm start
```

**Frontend:**
```bash
cd frontend-react
npm run build
npm run preview
```

### Access the Application

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:3001
- **API Health Check:** http://localhost:3001/api/health

---

## 📚 API Documentation

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/prices` | GET | Current cryptocurrency prices |
| `/api/indicators/:symbol` | GET | Technical indicators for symbol |
| `/api/sentiment` | GET | Aggregated market sentiment |
| `/api/news` | GET | Latest news articles |
| `/api/whale-transactions` | GET | Large transactions |
| `/api/prediction/:symbol` | GET | AI prediction for symbol |
| `/api/training/start` | POST | Start AI training |
| `/api/training/stop` | POST | Stop AI training |
| `/api/training/metrics` | GET | Get training metrics |

### WebSocket Events

**Client → Server:**
- `connection` - Initial connection
- `disconnect` - Client disconnect

**Server → Client:**
- `priceUpdate` - Real-time price & indicators (1s)
- `sentimentUpdate` - Sentiment update (5m)
- `newsUpdate` - News update (5m)
- `whaleUpdate` - Whale transactions (2m)

---

## 🧪 Testing

### Backend API Testing

```bash
# Test health endpoint
curl http://localhost:3001/api/health

# Test prices
curl http://localhost:3001/api/prices

# Test indicators
curl http://localhost:3001/api/indicators/BTC

# Test sentiment
curl http://localhost:3001/api/sentiment

# Test news
curl http://localhost:3001/api/news
```

### Frontend Testing Checklist

- [ ] Dashboard loads without errors
- [ ] WebSocket connects (green indicator)
- [ ] Price cards display real values
- [ ] Prices update every 1 second
- [ ] RSI gauge shows 0-100 value
- [ ] MACD chart displays correctly
- [ ] Sentiment gauge shows aggregated score
- [ ] News articles load with sentiment tags
- [ ] AI Predictor shows BUY/SELL/HOLD signals
- [ ] Navigation works (all 6 tabs)
- [ ] Settings page shows feature flags
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Smooth performance (60 FPS)

---
=======
Frontend (React + TypeScript) ←→ Backend (Node.js + Express)
                ↕
        WebSocket + REST API
                ↕
    Multiple Data Sources (Binance, NewsAPI, etc.)
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hts-trading-system

# Backend setup
cd backend
npm install
npm run dev

# Frontend setup (in another terminal)
cd ../frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3001
- **WebSocket**: ws://localhost:3001

## 📊 Data Sources

- **Binance Testnet API** - Live cryptocurrency prices
- **Alternative.me** - Fear & Greed Index
- **NewsAPI** - Cryptocurrency news
- **CoinGecko** - Social metrics
- **Etherscan** - Whale transactions

## 🛠️ Tech Stack

### Backend
- Node.js + Express
- TypeScript
- Socket.io (WebSocket)
- Axios (HTTP client)
- Redis (caching)

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Recharts (charts)
- Socket.io-client
>>>>>>> 44c995af8c1e645205c1ee3e41e3890b3d6fc75a

## 📁 Project Structure

```
hts-trading-system/
<<<<<<< HEAD
├── backend-node/                    # Node.js/TypeScript Backend
│   ├── src/
│   │   ├── services/               # All services
│   │   │   ├── BinanceService.ts
│   │   │   ├── IndicatorService.ts
│   │   │   ├── SentimentService.ts
│   │   │   ├── NewsService.ts
│   │   │   ├── WhaleTrackingService.ts
│   │   │   ├── AIService.ts
│   │   │   └── WebSocketService.ts
│   │   ├── types/
│   │   │   └── index.ts           # Type definitions
│   │   └── index.ts               # Main server
│   ├── .env                       # Environment variables
│   ├── package.json
│   └── tsconfig.json
│
├── frontend-react/                 # React/TypeScript Frontend
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   │   ├── StatusBar.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── PriceCard.tsx
│   │   │   ├── RSIGauge.tsx
│   │   │   ├── MACDChart.tsx
│   │   │   ├── SentimentGauge.tsx
│   │   │   ├── AIPredictor.tsx
│   │   │   └── NewsCard.tsx
│   │   ├── views/                 # Page views
│   │   │   ├── DashboardView.tsx
│   │   │   ├── ChartView.tsx
│   │   │   ├── TrainingView.tsx
│   │   │   ├── PortfolioView.tsx
│   │   │   ├── NewsView.tsx
│   │   │   └── SettingsView.tsx
│   │   ├── contexts/              # React contexts
│   │   │   └── FeatureFlagContext.tsx
│   │   ├── hooks/                 # Custom hooks
│   │   │   └── useWebSocket.ts
│   │   ├── types/                 # Type definitions
│   │   │   └── index.ts
│   │   ├── App.tsx                # Main app component
│   │   ├── main.tsx               # Entry point
│   │   └── index.css              # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
└── README.md                       # This file
```

---

## 🔄 Phase 2 Roadmap

### Smart Money Concepts (SMC)
- [ ] Order block detection & visualization
- [ ] Support/resistance level identification
- [ ] Volume profile analysis
- [ ] Liquidity cluster detection

### Pattern Recognition
- [ ] Candlestick pattern detection (40+ patterns)
- [ ] Trend confirmation patterns
- [ ] Breakout/breakdown signals
- [ ] Chart pattern recognition

### Enhanced Sentiment
- [ ] Twitter/X sentiment integration
- [ ] Professional trader sentiment
- [ ] On-chain metrics sentiment
- [ ] Macro market sentiment

### Advanced Scoring System
```
Final Score = 40% RSI+MACD + 25% SMC + 20% Patterns + 10% Sentiment + 5% ML
```

### New Features
- [ ] Signal Breakdown Panel
- [ ] Historical Signal Performance
- [ ] Risk Management Dashboard
- [ ] Automated Alert System
- [ ] Trade Journal & Performance Tracker

---

## 🐛 Troubleshooting

### Common Issues

**Port 3001 already in use:**
```bash
# Find and kill process
lsof -i :3001
kill -9 <PID>

# Or use different port
PORT=3002 npm run dev
```

**Cannot find module 'express':**
```bash
cd backend-node
rm -rf node_modules package-lock.json
npm install
```

**WebSocket connection fails:**
1. Verify backend is running on port 3001
2. Check CORS configuration
3. Check browser console for errors
4. Try refreshing page (Ctrl+R)

**No prices showing:**
1. Check Binance testnet API accessibility
2. Verify internet connection
3. Check backend console for errors
4. Try different symbol (ETH, BNB)

---

## 📝 License

This project is provided as-is for educational and development purposes.

---

## 🙏 Acknowledgments

- Binance Testnet API
- Alternative.me (Fear & Greed Index)
- React & TypeScript communities
- All open-source contributors

---

## 📧 Support

For issues, questions, or contributions, please:
1. Check the troubleshooting section
2. Review the API documentation
3. Check existing issues/discussions

---

**Built with ❤️ by the HTS Team**

*Last Updated: 2025-10-16*
=======
├── backend/
│   ├── src/
│   │   ├── services/     # API services
│   │   ├── types/        # TypeScript types
│   │   └── index.ts      # Main server
│   ├── package.json
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── views/        # Page views
│   │   ├── hooks/        # Custom hooks
│   │   ├── contexts/     # React contexts
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🧪 Testing

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## 📈 Performance

- Dashboard load time: < 2 seconds
- Price update latency: < 500ms
- Chart rendering: 60 FPS
- Memory usage: < 150MB

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
PORT=3001
NODE_ENV=development
BINANCE_TESTNET_URL=https://testnet.binance.vision/api
SYMBOLS=BTC,ETH,BNB
```

### Feature Flags

The system includes a comprehensive feature flag system for progressive rollout:

- **Core Features**: 100% rollout
- **Advanced Features**: 0-60% rollout
- **Experimental**: 5-10% rollout

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Component Guide](docs/COMPONENTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This application is for educational and demonstration purposes only. It is not financial advice. Always do your own research before making investment decisions.

---

**Built with ❤️ using React, TypeScript, and Node.js**
>>>>>>> 44c995af8c1e645205c1ee3e41e3890b3d6fc75a
