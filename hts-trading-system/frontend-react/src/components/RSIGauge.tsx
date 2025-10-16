import React from 'react';

interface Props {
  rsi: number;
  trend: string;
}

const RSIGauge: React.FC<Props> = ({ rsi, trend }) => {
  const getColor = () => {
    if (rsi < 30) return '#ef4444';
    if (rsi > 70) return '#ef4444';
    return '#10b981';
  };

  const getTrendLabel = () => {
    if (rsi < 30) return '🔴 OVERSOLD';
    if (rsi > 70) return '🔴 OVERBOUGHT';
    return '🟢 NEUTRAL';
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="text-gray-400 text-sm font-semibold mb-4">RSI (14)</div>

      <div className="flex justify-center mb-6">
        <svg viewBox="0 0 200 120" width="200" height="120">
          <path
            d="M 30 100 A 70 70 0 0 1 170 100"
            fill="none"
            stroke="#374151"
            strokeWidth="12"
          />

          <path
            d={`M 30 100 A 70 70 0 0 1 ${
              30 + (140 * rsi) / 100
            } ${100 - Math.sin((rsi / 100) * Math.PI) * 70}`}
            fill="none"
            stroke={getColor()}
            strokeWidth="12"
          />

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
        <div className="text-white font-bold text-lg">{getTrendLabel()}</div>
      </div>
    </div>
  );
};

export default RSIGauge;
