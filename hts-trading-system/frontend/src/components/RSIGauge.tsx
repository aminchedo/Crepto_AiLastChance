import React from 'react';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { RSIGaugeProps } from '../types';

const RSIGauge: React.FC<RSIGaugeProps> = ({ 
  rsi, 
  trend, 
  isLoading = false 
}) => {
  const getColor = (): string => {
    if (rsi < 30) return '#ef4444'; // Red for oversold
    if (rsi > 70) return '#ef4444'; // Red for overbought
    return '#10b981'; // Green for neutral
  };

  const getTrendLabel = (): { text: string; icon: React.ReactNode; color: string } => {
    if (rsi < 30) {
      return {
        text: 'OVERSOLD',
        icon: <XCircle size={16} />,
        color: 'text-red-400'
      };
    }
    if (rsi > 70) {
      return {
        text: 'OVERBOUGHT',
        icon: <AlertTriangle size={16} />,
        color: 'text-red-400'
      };
    }
    return {
      text: 'NEUTRAL',
      icon: <CheckCircle size={16} />,
      color: 'text-green-400'
    };
  };

  const getRSIColor = (): string => {
    if (rsi < 30) return 'text-red-400';
    if (rsi > 70) return 'text-red-400';
    return 'text-green-400';
  };

  if (isLoading) {
    return (
      <div className="sentiment-gauge animate-pulse">
        <div className="text-gray-400 text-sm font-semibold mb-4">RSI (14)</div>
        <div className="flex justify-center mb-6">
          <div className="w-48 h-24 bg-gray-700 rounded-full"></div>
        </div>
        <div className="text-center">
          <div className="h-6 bg-gray-700 rounded w-24 mx-auto"></div>
        </div>
      </div>
    );
  }

  const trendInfo = getTrendLabel();
  const color = getColor();

  return (
    <div className="sentiment-gauge group hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-gray-400 text-sm font-semibold">RSI (14)</div>
        <div className={`text-xs px-2 py-1 rounded-full ${trendInfo.color} bg-gray-800`}>
          {rsi.toFixed(1)}
        </div>
      </div>

      {/* Gauge */}
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

          {/* Colored arc based on RSI value */}
          <path
            d={`M 30 100 A 70 70 0 0 1 ${
              30 + (140 * rsi) / 100
            } ${100 - Math.sin((rsi / 100) * Math.PI) * 70}`}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            className="transition-all duration-500"
          />

          {/* RSI Value */}
          <text
            x="100"
            y="85"
            textAnchor="middle"
            fill="#ffffff"
            fontSize="32"
            fontWeight="bold"
            className={getRSIColor()}
          >
            {rsi.toFixed(1)}
          </text>

          {/* Scale markers */}
          <text x="30" y="115" textAnchor="middle" fill="#6b7280" fontSize="12">0</text>
          <text x="100" y="25" textAnchor="middle" fill="#6b7280" fontSize="12">50</text>
          <text x="170" y="115" textAnchor="middle" fill="#6b7280" fontSize="12">100</text>

          {/* Threshold lines */}
          <line x1="30" y1="100" x2="30" y2="95" stroke="#6b7280" strokeWidth="2" />
          <line x1="100" y1="30" x2="100" y2="25" stroke="#6b7280" strokeWidth="2" />
          <line x1="170" y1="100" x2="170" y2="95" stroke="#6b7280" strokeWidth="2" />

          {/* 30 and 70 markers */}
          <line x1="58" y1="100" x2="58" y2="95" stroke="#ef4444" strokeWidth="2" />
          <line x1="142" y1="100" x2="142" y2="95" stroke="#ef4444" strokeWidth="2" />
        </svg>
      </div>

      {/* Trend Label */}
      <div className="text-center">
        <div className={`flex items-center justify-center space-x-2 font-bold text-lg ${trendInfo.color}`}>
          {trendInfo.icon}
          <span>{trendInfo.text}</span>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <div className="text-center">
          <div className="text-gray-500">Oversold</div>
          <div className="text-red-400 font-semibold">&lt; 30</div>
        </div>
        <div className="text-center">
          <div className="text-gray-500">Neutral</div>
          <div className="text-green-400 font-semibold">30-70</div>
        </div>
        <div className="text-center">
          <div className="text-gray-500">Overbought</div>
          <div className="text-red-400 font-semibold">&gt; 70</div>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </div>
  );
};

export default RSIGauge;