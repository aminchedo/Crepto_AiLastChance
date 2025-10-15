# Bolt AI Crypto - Real-Time Cryptocurrency Trading Dashboard

A fully functional cryptocurrency trading dashboard with AI-powered predictions, real-time market data, and portfolio management.

## Features

### 🚀 Real-Time Market Data
- Live cryptocurrency prices from CoinGecko API
- WebSocket integration for real-time updates (Binance)
- Fallback to polling when WebSocket fails
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)

### 🤖 AI-Powered Predictions
- TensorFlow.js neural network for price predictions
- Real-time AI training with live market data
- Bullish/Bearish/Neutral predictions with confidence scores
- Risk assessment and trading signals

### 📊 Technical Analysis
- Real-time technical indicators (RSI, MACD, SMA, Bollinger Bands)
- Interactive candlestick charts
- Multiple chart types and timeframes
- Technical indicator overlays

### 💼 Portfolio Management
- Real portfolio tracking with P&L calculations
- Add/remove positions
- Real-time portfolio value updates
- Asset allocation visualization
- Persistence with Supabase (optional)

### 📰 Market News
- Real cryptocurrency news from CoinGecko
- Sentiment analysis
- Impact assessment
- News filtering by sentiment

### 🎨 Modern UI/UX
- Dark theme with responsive design
- Smooth animations and transitions
- Real-time data updates
- Loading states and error handling

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **AI/ML**: TensorFlow.js
- **Data**: CoinGecko API, Binance WebSocket
- **Database**: Supabase (optional)
- **Icons**: Lucide React

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bolt-ai-crypto
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables** (optional)
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # CoinGecko API (Free tier - no key required)
   VITE_COINGECKO_API_URL=https://api.coingecko.com/api/v3
   
   # Supabase Configuration (optional)
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5173`

## Usage

### Dashboard
- View real-time cryptocurrency prices
- Select different assets to view detailed charts
- See AI predictions with confidence scores
- Monitor technical indicators

### AI Training
- Start/stop neural network training
- Monitor training metrics (MSE, MAE, R²)
- View training progress and stability
- Early stopping when model converges

### Portfolio
- Add cryptocurrency positions
- Track real-time P&L
- View asset allocation
- Remove positions

### News
- Read latest cryptocurrency news
- Filter by sentiment (positive/negative/neutral)
- See impact assessment

## API Configuration

### CoinGecko API
- **Free tier**: No API key required
- **Rate limit**: 50 calls/minute
- **Endpoints**: Market data, price charts, news

### Binance WebSocket
- **Free**: Real-time price streams
- **Rate limit**: None for WebSocket
- **Fallback**: Automatic polling if WebSocket fails

### Supabase (Optional)
- **Free tier**: 500MB database
- **Features**: Portfolio persistence
- **Fallback**: Local storage if not configured

## Development

### Project Structure
```
src/
├── components/          # React components
├── services/           # API services
├── utils/              # Utility functions
├── types/              # TypeScript types
└── App.tsx            # Main application
```

### Key Services
- `marketDataService.ts`: CoinGecko API integration
- `aiPredictionService.ts`: TensorFlow.js AI model
- `portfolioService.ts`: Portfolio management
- `websocketService.ts`: Real-time data streams

### Adding New Features
1. Create new components in `src/components/`
2. Add services in `src/services/`
3. Update types in `src/types/index.ts`
4. Integrate with main App component

## Production Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

## Performance Optimization

- **Lazy loading**: Components loaded on demand
- **Caching**: API responses cached locally
- **WebSocket**: Real-time updates without polling
- **TensorFlow.js**: Efficient browser-based ML
- **Code splitting**: Smaller bundle sizes

## Error Handling

- **API failures**: Graceful fallbacks to mock data
- **WebSocket disconnection**: Automatic reconnection
- **Network issues**: Retry mechanisms
- **User feedback**: Loading states and error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This application is for educational and demonstration purposes only. It is not financial advice. Always do your own research before making investment decisions. Cryptocurrency trading involves significant risk.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

---

**Built with ❤️ using React, TypeScript, and TensorFlow.js**
