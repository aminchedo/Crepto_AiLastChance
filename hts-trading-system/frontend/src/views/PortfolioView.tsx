import React from 'react';
import { Briefcase, TrendingUp, DollarSign, PieChart } from 'lucide-react';
import { WebSocketPriceUpdate } from '../types';

interface PortfolioViewProps {
  priceData: Map<string, WebSocketPriceUpdate>;
  isLoading: boolean;
}

const PortfolioView: React.FC<PortfolioViewProps> = ({ 
  priceData, 
  isLoading 
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center space-x-2">
            <Briefcase size={32} />
            <span>Portfolio Management</span>
          </h1>
          <p className="text-gray-400">
            Track and manage your cryptocurrency investments
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2">
          <TrendingUp size={16} className="text-green-400 animate-pulse" />
          <span className="text-sm text-gray-400">Live P&L</span>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { name: 'Total Value', value: '$0.00', change: '+0.00%', icon: DollarSign, color: 'text-green-400' },
          { name: 'Total P&L', value: '$0.00', change: '+0.00%', icon: TrendingUp, color: 'text-green-400' },
          { name: 'Positions', value: '0', change: '0', icon: Briefcase, color: 'text-blue-400' },
          { name: 'Cash', value: '$10,000.00', change: '0', icon: PieChart, color: 'text-gray-400' }
        ].map(metric => (
          <div key={metric.name} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <metric.icon size={20} className={metric.color} />
              <span className="text-xs text-gray-400">{metric.change}</span>
            </div>
            <div className="text-2xl font-bold text-white">{metric.value}</div>
            <div className="text-sm text-gray-400">{metric.name}</div>
          </div>
        ))}
      </div>

      {/* Portfolio Chart */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Loading portfolio data...</p>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <PieChart size={64} className="text-blue-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              Portfolio Overview
            </h3>
            <p className="text-gray-400 mb-4">
              Track your cryptocurrency investments and performance
            </p>
            <div className="bg-gray-800 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-sm text-gray-400 mb-2">
                Portfolio features will include:
              </p>
              <ul className="text-sm text-gray-300 space-y-1">
                <li>• Position tracking</li>
                <li>• P&L calculations</li>
                <li>• Asset allocation</li>
                <li>• Performance analytics</li>
                <li>• Risk management</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Positions Table */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Positions</h3>
        </div>
        <div className="p-6">
          <div className="text-center text-gray-400">
            <Briefcase size={48} className="mx-auto mb-4" />
            <p>No positions yet</p>
            <p className="text-sm">Add positions to start tracking your portfolio</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioView;