import React, { useState } from 'react';
import useWebSocket from './hooks/useWebSocket';
import { FeatureFlagsProvider } from './contexts/FeatureFlagContext';
import StatusBar from './components/StatusBar';
import Navbar from './components/Navbar';
import DashboardView from './views/DashboardView';
import ChartView from './views/ChartView';
import TrainingView from './views/TrainingView';
import PortfolioView from './views/PortfolioView';
import NewsView from './views/NewsView';
import SettingsView from './views/SettingsView';

type ViewType = 'dashboard' | 'charts' | 'training' | 'portfolio' | 'news' | 'settings';

function App() {
  const { priceData, sentiment, news, connected, lastUpdate } = useWebSocket();
  const [activeView, setActiveView] = useState<ViewType>('dashboard');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');

  const symbols = Array.from(priceData.keys()).sort();

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <DashboardView
            priceData={priceData}
            sentiment={sentiment}
            news={news}
            symbols={symbols}
          />
        );
      case 'charts':
        return (
          <ChartView
            selectedSymbol={selectedSymbol}
            priceData={priceData}
          />
        );
      case 'training':
        return <TrainingView />;
      case 'portfolio':
        return <PortfolioView priceData={priceData} />;
      case 'news':
        return <NewsView news={news} />;
      case 'settings':
        return <SettingsView />;
      default:
        return null;
    }
  };

  return (
    <FeatureFlagsProvider>
      <div className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950 text-white">
        {/* Status Bar */}
        <StatusBar connected={connected} lastUpdate={lastUpdate} />

        {/* Navigation */}
        <Navbar activeView={activeView} onViewChange={setActiveView} />

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {renderView()}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-800 px-6 py-4 text-center text-gray-500 text-sm mt-12">
          <p>
            HTS Trading System v1.0 • Powered by AI • Real-time Analysis •{' '}
            {new Date().toLocaleString()}
          </p>
        </footer>
      </div>
    </FeatureFlagsProvider>
  );
}

export default App;
