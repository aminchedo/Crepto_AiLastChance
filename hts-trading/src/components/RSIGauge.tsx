import React from 'react';

interface RSIGaugeProps {
  rsi: number;
  trend: string;
}

const RSIGauge: React.FC<RSIGaugeProps> = ({ rsi, trend }) => {
  const getColor = () => {
    if (rsi < 30) return '#ef4444'; // red - oversold
    if (rsi > 70) return '#ef4444'; // red - overbought
    return '#10b981'; // green - neutral
  };

  const getTrendLabel = () => {
    if (rsi < 30) return '🔴 OVERSOLD';
    if (rsi > 70) return '🔴 OVERBOUGHT';
    return '🟢 NEUTRAL';
  };

  const getBackgroundColor = () => {
    if (rsi < 30) return 'from-red-900/20 to-red-900/5';
    if (rsi > 70) return 'from-red-900/20 to-red-900/5';
    return 'from-green-900/20 to-green-900/5';
  };

  return (
    <div className={`bg-gradient-to-br ${getBackgroundColor()} border border-gray-700 rounded-xl p-6`}>
      <div className="text-gray-400 text-sm mb-4 font-semibold">RSI (14)</div>

      <div className="flex justify-center mb-6">
        <svg viewBox="0 0 200 120" width="200" height="120">
          {/* Background arc */}
          <path
            d="M 30 100 A 70 70 0 0 1 170 100"
            fill="none"
            stroke="#374151"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Value arc */}
          <path
            d={`M 30 100 A 70 70 0 0 1 ${30 + (140 * rsi / 100)} ${100 - (Math.sin((rsi / 100) * Math.PI) * 70)}`}
            fill="none"
            stroke={getColor()}
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Center text */}
          <text
            x="100"
            y="85"
            textAnchor="middle"
            fill="#ffffff"
            fontSize="32"
            fontWeight="bold"
          >
            {rsi.toFixed(1)}
          </text>
        </svg>
      </div>

      <div className="text-center">
        <div className="text-gray-400 text-xs mb-2">Status</div>
        <div className="text-white font-bold text-lg">{getTrendLabel()}</div>
      </div>
    </div>
  );
};

export default RSIGauge;