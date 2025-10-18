import React, { useState, useEffect } from 'react';
import { MarketTicker } from './components/MarketTicker';
import { PriceChart } from './components/PriceChart';
import { AIPredictor } from './components/AIPredictor';
import { TrainingDashboard } from './components/TrainingDashboard';
import { Portfolio } from './components/Portfolio';
import { NewsFeed } from './components/NewsFeed';
import { MarketSentiment } from './components/MarketSentiment';
import { CryptoDashboard } from './components/crypto/CryptoDashboard';
import { FeatureFlagManager } from './components/FeatureFlagManager';
import { FeatureFlagProvider } from './contexts/FeatureFlagContext';
import { useFeatureFlags } from './hooks/useFeatureFlags';
import { FeatureGate, FeatureGateSimple, FeatureGateWithDependencies } from './components/FeatureGate';
import { FeatureFlagDemo } from './components/FeatureFlagDemo';
import { marketDataService } from './services/marketDataService';
import { aiPredictionService } from './services/aiPredictionService';
import { MarketData, CandlestickData, TechnicalIndicators, PredictionData, TrainingMetrics } from './types';
import { Brain, BarChart3, Wallet, Newspaper, Settings, Activity, TrendingUp } from 'lucide-react';

// HTS Trading System Components
import StatusBar from './components/StatusBar';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import ChartView from './components/ChartView';
import TrainingView from './components/TrainingView';
import PortfolioView from './components/PortfolioView';
import NewsView from './components/NewsView';
import SettingsView from './components/SettingsView';
import useWebSocket from './hooks/useWebSocket';
import { WebSocketData, ViewType } from './types';

function AppContent() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');
  const [candlestickData, setCandlestickData] = useState<CandlestickData[]>([]);
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicators>();
  const [predictions, setPredictions] = useState<Record<string, PredictionData>>({});
  const [isTraining, setIsTraining] = useState(false);
  const [currentMetrics, setCurrentMetrics] = useState<TrainingMetrics>();
  const [trainingHistory, setTrainingHistory] = useState<TrainingMetrics[]>([]);
  const [activeView, setActiveView] = useState<'dashboard' | 'training' | 'portfolio' | 'news' | 'crypto' | 'settings'>('dashboard');
  
  // HTS Trading System WebSocket integration
  const { priceData, sentiment, news, connected, lastUpdate }: WebSocketData = useWebSocket();
  const [htsActiveView, setHtsActiveView] = useState<ViewType>('dashboard');
  const [isLoading, setIsLoading] = useState(true);
  
  // Get feature flags
  const {
    isAIPredictionsEnabled,
    isPortfolioEnabled,
    isTrainingDashboardEnabled,
    isNewsFeedEnabled,
    isRealTimeChartsEnabled,
    isAdvancedChartsEnabled,
    isBacktestingEnabled,
    isRiskManagementEnabled,
    isWhaleTrackingEnabled,
    isSocialSentimentEnabled,
    isAIOptimizationEnabled,
    isPaperTradingEnabled,
    isAlertsSystemEnabled,
    isQuantumAIEnabled,
    isBlockchainAnalysisEnabled
  } = useFeatureFlags();

  // Extract symbols from HTS price data
  const htsSymbols = Array.from(priceData.keys()).sort();

  // Set loading state for HTS system
  useEffect(() => {
    if (connected && priceData.size > 0) {
      setIsLoading(false);
    }
  }, [connected, priceData.size]);

  useEffect(() => {
    // Initialize services
    const initializeServices = async () => {
      await marketDataService.initialize();
      await aiPredictionService.initialize();
    };

    initializeServices();

    // Subscribe to market data updates
    const unsubscribeMarket = marketDataService.subscribe((data) => {
      setMarketData(data);
    });

    // Subscribe to AI predictions
    const unsubscribePredictions = aiPredictionService.subscribeToPredictions((prediction) => {
      setPredictions(prev => ({
        ...prev,
        [prediction.symbol]: prediction
      }));
    });

    // Subscribe to training metrics
    const unsubscribeTraining = aiPredictionService.subscribeToTraining((metrics) => {
      setCurrentMetrics(metrics);
      setTrainingHistory(prev => [...prev, metrics]);
    });

    return () => {
      unsubscribeMarket();
      unsubscribePredictions();
      unsubscribeTraining();
    };
  }, []);

  useEffect(() => {
    // Load chart data when symbol changes
    const loadChartData = async () => {
      const candleData = await marketDataService.getCandlestickData(selectedSymbol);
      const indicators = await marketDataService.getTechnicalIndicators(selectedSymbol);
      setCandlestickData(candleData);
      setTechnicalIndicators(indicators);
    };

    loadChartData();
  }, [selectedSymbol]);

  useEffect(() => {
    // Update training state
    setIsTraining(aiPredictionService.getIsTraining());
  }, [currentMetrics]);

  const handleStartTraining = () => {
    aiPredictionService.startTraining();
  };

  const handleStopTraining = () => {
    aiPredictionService.stopTraining();
  };

  // Build navigation items based on enabled features
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, enabled: true },
    { 
      id: 'crypto', 
      label: 'Enhanced Crypto', 
      icon: TrendingUp, 
      enabled: isRealTimeChartsEnabled || isAdvancedChartsEnabled 
    },
    { 
      id: 'training', 
      label: 'AI Training', 
      icon: Brain, 
      enabled: isTrainingDashboardEnabled 
    },
    { 
      id: 'portfolio', 
      label: 'Portfolio', 
      icon: Wallet, 
      enabled: isPortfolioEnabled 
    },
    { 
      id: 'news', 
      label: 'News', 
      icon: Newspaper, 
      enabled: isNewsFeedEnabled 
    },
    { id: 'settings', label: 'Settings', icon: Settings, enabled: true },
  ].filter(item => item.enabled);

  // Render HTS Trading System view
  const renderHtsView = () => {
    switch (htsActiveView) {
      case 'dashboard':
        return (
          <DashboardView
            priceData={priceData}
            sentiment={sentiment}
            news={news}
            symbols={htsSymbols}
            isLoading={isLoading}
          />
        );
      case 'charts':
        return (
          <ChartView
            selectedSymbol={selectedSymbol}
            priceData={priceData}
            isLoading={isLoading}
          />
        );
      case 'training':
        return <TrainingView isLoading={isLoading} />;
      case 'portfolio':
        return <PortfolioView priceData={priceData} isLoading={isLoading} />;
      case 'news':
        return <NewsView news={news} isLoading={isLoading} />;
      case 'settings':
        return <SettingsView />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
        {/* Status Bar for HTS System */}
        <StatusBar 
          connected={connected} 
          lastUpdate={lastUpdate}
          isLoading={isLoading}
        />

        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-800">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Brain className="text-blue-400" size={32} />
                <h1 className="text-2xl font-bold text-white">
                  <span className="text-blue-400">Bolt</span> AI Crypto + HTS Trading
                </h1>
              </div>
              <div className="hidden md:flex items-center space-x-1 ml-8">
                <Activity size={16} className="text-green-400" />
                <span className="text-green-400 text-sm font-medium">Live</span>
              </div>
            </div>

            <nav className="flex items-center space-x-1">
              {navigationItems.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveView(id as any)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${activeView === id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800'
                    }`}
                >
                  <Icon size={20} />
                  <span className="hidden md:inline">{label}</span>
                </button>
              ))}
            </nav>
          </div>
        </header>

        {/* HTS Navigation */}
        <Navbar 
          activeView={htsActiveView} 
          onViewChange={setHtsActiveView}
        />

      {/* Market Ticker */}
      <MarketTicker marketData={marketData} />

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        {/* HTS Trading System Views */}
        {htsActiveView !== 'dashboard' && (
          <div className="mb-8">
            {renderHtsView()}
          </div>
        )}

        {/* Original Bolt AI Crypto Views */}
        {activeView === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chart Section */}
            <div className="lg:col-span-2 space-y-6">
              <FeatureGateSimple featureId="real-time-charts">
                <PriceChart
                  symbol={selectedSymbol}
                  data={candlestickData}
                  indicators={technicalIndicators}
                />
              </FeatureGateSimple>

              {/* Asset Selection */}
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Assets</h3>
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {marketData.slice(0, 5).map((coin) => (
                    <button
                      key={coin.symbol}
                      onClick={() => setSelectedSymbol(coin.symbol)}
                      className={`p-3 rounded-lg border transition-colors ${selectedSymbol === coin.symbol
                          ? 'border-blue-500 bg-blue-900/20'
                          : 'border-gray-700 bg-gray-800 hover:bg-gray-700'
                        }`}
                    >
                      <div className="text-center">
                        <div className="text-white font-semibold text-sm">{coin.symbol}</div>
                        <div className="text-gray-400 text-xs">${coin.price.toLocaleString()}</div>
                        <div className={`text-xs font-medium ${coin.changePercent24h >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                          {coin.changePercent24h >= 0 ? '+' : ''}
                          {coin.changePercent24h.toFixed(2)}%
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Predictor */}
            <div>
              <FeatureGateSimple featureId="ai-predictions">
                <AIPredictor predictions={predictions} />
              </FeatureGateSimple>

              {/* Market Sentiment */}
              <div className="mt-6">
                <FeatureGateSimple featureId="market-sentiment">
                  <MarketSentiment />
                </FeatureGateSimple>
              </div>
            </div>
          </div>
        )}

        {activeView === 'training' && (
          <div className="space-y-6">
            <FeatureGateWithDependencies 
              featureId="training-dashboard"
              dependencies={isAIOptimizationEnabled ? ['ai-optimization'] : []}
            >
              <TrainingDashboard
                isTraining={isTraining}
                currentMetrics={currentMetrics}
                trainingHistory={trainingHistory}
                onStartTraining={handleStartTraining}
                onStopTraining={handleStopTraining}
              />
            </FeatureGateWithDependencies>
          </div>
        )}

        {activeView === 'portfolio' && (
          <div className="space-y-6">
            <FeatureGateWithDependencies 
              featureId="portfolio-management"
              dependencies={isRiskManagementEnabled ? ['risk-management'] : []}
            >
              <Portfolio marketData={marketData} />
            </FeatureGateWithDependencies>
          </div>
        )}

        {activeView === 'news' && (
          <div className="space-y-6">
            <FeatureGateWithDependencies 
              featureId="news-feed"
              dependencies={isSocialSentimentEnabled ? ['social-sentiment'] : []}
            >
              <NewsFeed />
            </FeatureGateWithDependencies>
          </div>
        )}

        {activeView === 'crypto' && (
          <FeatureGate 
            featureId="advanced-charts"
            requireAny={['real-time-charts', 'advanced-charts']}
            showFeatureInfo={true}
          >
            <CryptoDashboard />
          </FeatureGate>
        )}

        {activeView === 'settings' && (
          <div className="space-y-6">
            <FeatureFlagDemo />
          </div>
        )}
      </main>

        {/* Footer */}
        <footer className="bg-gray-900 border-t border-gray-800 px-6 py-4 mt-8">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div>
              © 2025 Bolt AI Crypto + HTS Trading System. Not financial advice. Trade at your own risk.
            </div>
            <div className="flex items-center space-x-4">
              <span>Neural Network: Stable Training Active</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Live Data Feed</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                <span>HTS WebSocket: {connected ? 'Connected' : 'Disconnected'}</span>
              </div>
            </div>
          </div>
        </footer>

        {/* Feature Flag Manager */}
        <FeatureFlagManager />
      </div>
  );
}

function App() {
  return (
    <FeatureFlagProvider>
      <AppContent />
    </FeatureFlagProvider>
  );
}

export default App;