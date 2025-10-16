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

## 🏗️ Architecture

```
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

## 📁 Project Structure

```
hts-trading-system/
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