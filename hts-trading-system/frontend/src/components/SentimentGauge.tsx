import React from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { SentimentGaugeProps } from '../types';

const SentimentGauge: React.FC<SentimentGaugeProps> = ({
  score,
  fearGreed,
  reddit,
  coinGecko,
  trend,
  isLoading = false
}) => {
  const getColor = (value: number) => {
    if (value < 25) return '#ef4444'; // Red
    if (value < 45) return '#f97316'; // Orange
    if (value < 55) return '#eab308'; // Yellow
    if (value < 75) return '#84cc16'; // Light Green
    return '#22c55e'; // Green
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'extreme fear':
        return <AlertTriangle size={20} className="text-red-400" />;
      case 'fear':
        return <TrendingDown size={20} className="text-orange-400" />;
      case 'greed':
        return <TrendingUp size={20} className="text-green-400" />;
      case 'extreme greed':
        return <AlertTriangle size={20} className="text-yellow-400" />;
      default:
        return <Minus size={20} className="text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'extreme fear':
        return 'text-red-400';
      case 'fear':
        return 'text-orange-400';
      case 'neutral':
        return 'text-gray-400';
      case 'greed':
        return 'text-green-400';
      case 'extreme greed':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <div className="sentiment-gauge animate-pulse">
        <div className="text-gray-400 text-sm font-semibold mb-4">📊 Market Sentiment</div>
        <div className="flex justify-center mb-6">
          <div className="w-48 h-24 bg-gray-700 rounded-full"></div>
        </div>
        <div className="text-center">
          <div className="h-6 bg-gray-700 rounded w-32 mx-auto mb-4"></div>
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-700 rounded w-full"></div>
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="sentiment-gauge group hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="text-gray-400 text-sm font-semibold mb-4 flex items-center space-x-2">
        <span>📊</span>
        <span>Market Sentiment</span>
      </div>

      {/* Main Gauge */}
      <div className="flex justify-center mb-6">
        <svg viewBox="0 0 200 120" width="200" height="120" className="drop-shadow-lg">
          {/* Background arc */}
          <path
            d="M 30 100 A 70 70 0 0 1 170 100"
            fill="none"
            stroke="#374151"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Colored arc based on score */}
          <path
            d={`M 30 100 A 70 70 0 0 1 ${
              30 + (140 * score) / 100
            } ${100 - Math.sin((score / 100) * Math.PI) * 70}`}
            fill="none"
            stroke={getColor(score)}
            strokeWidth="12"
            strokeLinecap="round"
            className="transition-all duration-500"
          />

          {/* Score value */}
          <text
            x="100"
            y="85"
            textAnchor="middle"
            fill="#ffffff"
            fontSize="32"
            fontWeight="bold"
          >
            {score}
          </text>

          {/* Scale markers */}
          <text x="30" y="115" textAnchor="middle" fill="#6b7280" fontSize="12">0</text>
          <text x="100" y="25" textAnchor="middle" fill="#6b7280" fontSize="12">50</text>
          <text x="170" y="115" textAnchor="middle" fill="#6b7280" fontSize="12">100</text>

          {/* Threshold lines */}
          <line x1="30" y1="100" x2="30" y2="95" stroke="#6b7280" strokeWidth="2" />
          <line x1="100" y1="30" x2="100" y2="25" stroke="#6b7280" strokeWidth="2" />
          <line x1="170" y1="100" x2="170" y2="95" stroke="#6b7280" strokeWidth="2" />
        </svg>
      </div>

      {/* Trend Label */}
      <div className="text-center mb-4">
        <div className={`flex items-center justify-center space-x-2 font-bold text-lg ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="uppercase">{trend}</span>
        </div>
      </div>

      {/* Breakdown */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Fear & Greed</span>
          <div className="flex items-center gap-2">
            <div className="w-24 bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${fearGreed}%` }}
              ></div>
            </div>
            <span className="text-blue-400 font-bold w-8">{fearGreed}</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Reddit</span>
          <div className="flex items-center gap-2">
            <div className="w-24 bg-gray-700 rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${reddit}%` }}
              ></div>
            </div>
            <span className="text-orange-400 font-bold w-8">{reddit}</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">CoinGecko</span>
          <div className="flex items-center gap-2">
            <div className="w-24 bg-gray-700 rounded-full h-2">
              <div
                className="bg-yellow-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${coinGecko}%` }}
              ></div>
            </div>
            <span className="text-yellow-400 font-bold w-8">{coinGecko}</span>
          </div>
        </div>
      </div>

      {/* Sentiment Scale */}
      <div className="mt-4 grid grid-cols-5 gap-1 text-xs">
        <div className="text-center">
          <div className="text-red-400 font-semibold">0-20</div>
          <div className="text-gray-500">Extreme Fear</div>
        </div>
        <div className="text-center">
          <div className="text-orange-400 font-semibold">20-40</div>
          <div className="text-gray-500">Fear</div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 font-semibold">40-60</div>
          <div className="text-gray-500">Neutral</div>
        </div>
        <div className="text-center">
          <div className="text-green-400 font-semibold">60-80</div>
          <div className="text-gray-500">Greed</div>
        </div>
        <div className="text-center">
          <div className="text-yellow-400 font-semibold">80-100</div>
          <div className="text-gray-500">Extreme Greed</div>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </div>
  );
};

export default SentimentGauge;