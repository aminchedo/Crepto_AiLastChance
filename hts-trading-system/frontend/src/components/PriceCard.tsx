import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';
import { PriceCardProps } from '../types';

const PriceCard: React.FC<PriceCardProps> = ({ 
  symbol, 
  price, 
  change24h, 
  volume, 
  isLoading = false 
}) => {
  const isPositive = change24h >= 0;
  const changeColor = isPositive ? 'text-green-400' : 'text-red-400';
  const changeBgColor = isPositive ? 'bg-green-900/20' : 'bg-red-900/20';
  const changeBorderColor = isPositive ? 'border-green-500/30' : 'border-red-500/30';

  if (isLoading) {
    return (
      <div className="price-card animate-pulse">
        <div className="flex justify-between items-start mb-4">
          <div className="space-y-2">
            <div className="h-4 bg-gray-700 rounded w-16"></div>
            <div className="h-8 bg-gray-700 rounded w-24"></div>
          </div>
          <div className="w-8 h-8 bg-gray-700 rounded"></div>
        </div>
        <div className="h-6 bg-gray-700 rounded w-20 mb-3"></div>
        <div className="h-4 bg-gray-700 rounded w-24"></div>
      </div>
    );
  }

  return (
    <div className="price-card group hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="text-gray-400 text-sm font-medium">{symbol}/USDT</span>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          </div>
          <div className="text-white text-3xl font-bold">
            ${price.toLocaleString(undefined, { 
              minimumFractionDigits: 2, 
              maximumFractionDigits: 2 
            })}
          </div>
        </div>
        
        <div className={`p-2 rounded-lg ${changeBgColor} ${changeBorderColor} border`}>
          {isPositive ? (
            <TrendingUp className="text-green-400" size={24} />
          ) : (
            <TrendingDown className="text-red-400" size={24} />
          )}
        </div>
      </div>

      {/* Price Change */}
      <div className={`text-lg font-semibold mb-3 ${changeColor}`}>
        <span className="flex items-center space-x-1">
          {isPositive ? (
            <TrendingUp size={16} />
          ) : (
            <TrendingDown size={16} />
          )}
          <span>
            {isPositive ? '+' : ''}{change24h.toFixed(2)}%
          </span>
        </span>
      </div>

      {/* Volume */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-1">
          <BarChart3 size={14} />
          <span>Volume</span>
        </div>
        <div className="flex items-center space-x-1">
          <DollarSign size={12} />
          <span>${(volume / 1000000).toFixed(2)}M</span>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </div>
  );
};

export default PriceCard;