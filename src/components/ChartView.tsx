import React from 'react';
import { TrendingUp, BarChart3, Activity } from 'lucide-react';
import { WebSocketPriceUpdate } from '../types';

interface ChartViewProps {
  selectedSymbol: string;
  priceData: Map<string, WebSocketPriceUpdate>;
  isLoading: boolean;
}

const ChartView: React.FC<ChartViewProps> = ({ 
  selectedSymbol, 
  priceData, 
  isLoading 
}) => {
  const currentData = priceData.get(selectedSymbol);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-2">
            <TrendingUp size={32} />
            <span>Advanced Charts</span>
          </h1>
          <p className="text-gray-400">
            Professional charting tools with technical indicators
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <Activity size={16} className="text-green-400 animate-pulse" />
          <span className="text-sm text-gray-400">Live Updates</span>
        </div>
      </div>

      {/* Chart Placeholder */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-8">
        {isLoading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading chart data...</p>
            </div>
          </div>
        ) : currentData ? (
          <div className="text-center">
            <BarChart3 size={64} className="text-blue-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              {selectedSymbol} Chart
            </h3>
            <p className="text-gray-400 mb-4">
              Current Price: ${currentData.currentPrice.toLocaleString()}
            </p>
            <div className="bg-gray-800 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-gray-400">
                Advanced charting features will be implemented here, including:
              </p>
              <ul className="text-sm text-gray-300 mt-2 space-y-1">
                <li>• TradingView integration</li>
                <li>• Multiple timeframes</li>
                <li>• Drawing tools</li>
                <li>• Technical indicators overlay</li>
                <li>• Volume analysis</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <BarChart3 size={64} className="text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No Data Available
            </h3>
            <p className="text-gray-400">
              Select a cryptocurrency to view detailed charts
            </p>
          </div>
        )}
      </div>

      {/* Technical Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {['RSI', 'MACD', 'Bollinger Bands', 'Stochastic', 'Williams %R', 'ATR'].map(indicator => (
          <div key={indicator} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-white mb-2">{indicator}</h4>
            <div className="h-24 bg-gray-800 rounded flex items-center justify-center">
              <span className="text-gray-500 text-sm">Chart placeholder</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChartView;