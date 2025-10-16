import React, { useState, useEffect } from 'react';
import { FeatureFlagsProvider } from './contexts/FeatureFlagContext';
import useWebSocket from './hooks/useWebSocket';
import StatusBar from './components/StatusBar';
import Navbar from './components/Navbar';
import DashboardView from './views/DashboardView';
import ChartView from './views/ChartView';
import TrainingView from './views/TrainingView';
import PortfolioView from './views/PortfolioView';
import NewsView from './views/NewsView';
import SettingsView from './views/SettingsView';
import { ViewType, WebSocketData } from './types';

function App() {
  const { priceData, sentiment, news, connected, lastUpdate }: WebSocketData = useWebSocket();
  const [activeView, setActiveView] = useState<ViewType>('dashboard');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');
  const [isLoading, setIsLoading] = useState(true);

  // Extract symbols from price data
  const symbols = Array.from(priceData.keys()).sort();

  // Set loading state
  useEffect(() => {
    if (connected && priceData.size > 0) {
      setIsLoading(false);
    }
  }, [connected, priceData.size]);

  // Render view based on active view
  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <DashboardView
            priceData={priceData}
            sentiment={sentiment}
            news={news}
            symbols={symbols}
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
    <FeatureFlagsProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
        {/* Status Bar */}
        <StatusBar 
          connected={connected} 
          lastUpdate={lastUpdate}
          isLoading={isLoading}
        />

        {/* Navigation */}
        <Navbar 
          activeView={activeView} 
          onViewChange={setActiveView}
        />

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8 flex-1">
          {renderView()}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 px-6 py-4 text-center text-gray-500 text-sm mt-12">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div>
              HTS Trading System v1.0 • Powered by AI • Real-time Analysis
            </div>
            <div className="flex items-center space-x-4 mt-2 sm:mt-0">
              <span className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                <span>{connected ? 'Connected' : 'Disconnected'}</span>
              </span>
              <span className="text-xs">
                {new Date().toLocaleString()}
              </span>
            </div>
          </div>
        </footer>
      </div>
    </FeatureFlagsProvider>
  );
}

export default App;