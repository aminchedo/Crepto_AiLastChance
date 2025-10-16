# HTS Trading System - Frontend

## React/TypeScript Frontend with Vite & Tailwind CSS

---

## 📋 Overview

Professional cryptocurrency trading dashboard built with React and TypeScript. Features real-time data visualization, technical analysis, and AI predictions.

---

## 🛠️ Technology Stack

- **Framework:** React 18+
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Icons:** Lucide React
- **Real-time:** Socket.io-client
- **HTTP:** Axios

---

## 📦 Installation

```bash
npm install
```

---

## 🚀 Running

### Development Mode
```bash
npm run dev
```
Access: http://localhost:5173

### Production Build
```bash
npm run build
npm run preview
```

### Linting
```bash
npm run lint
```

---

## 🎨 Features

### Core Components

**StatusBar** - Connection status & last update time  
**Navbar** - Navigation between views  
**PriceCard** - Cryptocurrency price display  
**RSIGauge** - RSI indicator visualization  
**MACDChart** - MACD chart with Recharts  
**SentimentGauge** - Market sentiment display  
**AIPredictor** - AI prediction signals  
**NewsCard** - News article cards

### Views

**DashboardView** - Main overview (default)  
**ChartView** - Advanced charts (Phase 2)  
**TrainingView** - AI training metrics (Phase 2)  
**PortfolioView** - Portfolio tracking (Phase 2)  
**NewsView** - News feed  
**SettingsView** - Feature flag management

---

## 🔌 WebSocket Integration

### Custom Hook: `useWebSocket`

```typescript
const { priceData, sentiment, news, connected, lastUpdate } = useWebSocket();
```

Returns:
- `priceData` - Map of symbol to price/indicators
- `sentiment` - Aggregated sentiment data
- `news` - Array of news articles
- `connected` - WebSocket connection status
- `lastUpdate` - Last update timestamp

---

## 🎛️ Feature Flags

### Context: `FeatureFlagsContext`

```typescript
const { flags, isFeatureEnabled, toggleFeature } = useContext(FeatureFlagsContext);
```

**Core Features (100% rollout):**
- AI Predictions
- Portfolio Management
- Real-time Charts
- News Feed
- Market Sentiment
- Training Dashboard

**Advanced Features (0-60% rollout):**
- Advanced Charts (50%)
- Backtesting (25%)
- Risk Management (30%)
- Whale Tracking (20%)
- Paper Trading (40%)
- Alerts System (60%)

**Experimental (5-10% rollout):**
- Quantum AI (5%)
- Blockchain Analysis (10%)

---

## 🎨 Styling

### Tailwind Configuration

Custom theme:
```javascript
colors: {
  'dark-bg': '#0f0f0f',
  'dark-card': '#1a1a1a',
  'dark-border': '#333333',
}
```

### Dark Theme
- Optimized for trading
- Reduced eye strain
- Professional appearance
- Consistent color scheme

---

## 📊 State Management

### Global State
- `FeatureFlagsContext` - Feature flags
- `useWebSocket` - Real-time data

### Local State
- Component-level useState
- View navigation
- Chart history tracking

---

## 🏗️ Architecture

```
src/
├── components/        # Reusable UI components
│   ├── StatusBar.tsx
│   ├── Navbar.tsx
│   ├── PriceCard.tsx
│   ├── RSIGauge.tsx
│   ├── MACDChart.tsx
│   ├── SentimentGauge.tsx
│   ├── AIPredictor.tsx
│   └── NewsCard.tsx
├── views/            # Page views
│   ├── DashboardView.tsx
│   ├── ChartView.tsx
│   ├── TrainingView.tsx
│   ├── PortfolioView.tsx
│   ├── NewsView.tsx
│   └── SettingsView.tsx
├── contexts/         # React contexts
│   └── FeatureFlagContext.tsx
├── hooks/           # Custom hooks
│   └── useWebSocket.ts
├── types/           # TypeScript types
│   └── index.ts
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Dashboard loads
- [ ] WebSocket connects (green indicator)
- [ ] Prices update every 1s
- [ ] RSI displays 0-100
- [ ] MACD chart renders
- [ ] Sentiment shows score
- [ ] News articles load
- [ ] AI predictions display
- [ ] Navigation works
- [ ] Settings toggles work
- [ ] Mobile responsive
- [ ] No console errors

---

## 📱 Responsive Design

### Breakpoints
- **Mobile:** < 768px
- **Tablet:** 768px - 1024px
- **Desktop:** > 1024px

### Grid Layouts
- Price cards: 1 col (mobile) → 3 cols (desktop)
- News: 1 col (mobile) → 3 cols (desktop)
- Indicators: 1 col (mobile) → 2 cols (desktop)

---

## 🔄 Data Flow

1. **WebSocket Connect** → Establish connection
2. **Receive Updates** → priceUpdate, sentimentUpdate, newsUpdate
3. **Update State** → React useState/Context
4. **Re-render Components** → Display new data
5. **Chart History** → Track for visualization

---

## 🎯 Performance

- **Initial Load:** < 2s
- **Price Updates:** < 100ms
- **Chart Rendering:** 60 FPS
- **Memory Usage:** < 100MB
- **Bundle Size:** ~500KB (gzipped)

### Optimizations
- Code splitting by route
- Lazy loading images
- Debounced chart updates
- Memoized calculations
- Virtual scrolling (future)

---

## 🐛 Troubleshooting

### WebSocket Not Connecting
1. Check backend is running (port 3001)
2. Verify proxy config in vite.config.ts
3. Check browser console
4. Clear cache and refresh

### Charts Not Rendering
1. Verify Recharts installed
2. Check data format
3. Inspect browser console
4. Check component props

### Styles Not Applied
1. Verify Tailwind installed
2. Check tailwind.config.js
3. Ensure PostCSS configured
4. Rebuild with `npm run dev`

---

## 🔧 Configuration

### Vite Config
```typescript
{
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
}
```

### TypeScript Config
- Strict mode enabled
- React JSX transform
- Path aliases supported
- Source maps enabled

---

## 📈 Future Enhancements

### Phase 2 Features
- [ ] Advanced TradingView charts
- [ ] Portfolio tracking
- [ ] AI training visualization
- [ ] Backtesting interface
- [ ] Alert management
- [ ] Performance analytics

---

## 🎨 Design System

### Colors
- **Primary:** Blue (#3b82f6)
- **Success:** Green (#10b981)
- **Warning:** Yellow (#eab308)
- **Danger:** Red (#ef4444)
- **Neutral:** Gray scale

### Typography
- **Headings:** Bold, 2xl-3xl
- **Body:** Regular, base
- **Captions:** Small, gray-400

---

## 📝 Development Notes

- TypeScript strict mode
- ESLint configured
- Tailwind JIT mode
- Hot Module Replacement
- Source maps in dev mode

---

**Built with React, TypeScript, Vite & Tailwind CSS**
