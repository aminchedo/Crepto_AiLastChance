import React from 'react';

interface Props {
  score: number;
  fearGreed: number;
  reddit: number;
  coinGecko: number;
  trend: string;
}

const SentimentGauge: React.FC<Props> = ({
  score,
  fearGreed,
  reddit,
  coinGecko,
  trend
}) => {
  const getColor = (value: number) => {
    if (value < 25) return '#ef4444';
    if (value < 45) return '#f97316';
    if (value < 55) return '#eab308';
    if (value < 75) return '#84cc16';
    return '#22c55e';
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="text-gray-400 text-sm font-semibold mb-4">
        📊 Market Sentiment
      </div>

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
              30 + (140 * score) / 100
            } ${100 - Math.sin((score / 100) * Math.PI) * 70}`}
            fill="none"
            stroke={getColor(score)}
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
            {score}
          </text>
        </svg>
      </div>

      <div className="text-center mb-4">
        <div className="text-white font-bold text-lg uppercase">{trend}</div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Fear & Greed</span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${fearGreed}%` }}
              ></div>
            </div>
            <span className="text-blue-400 font-bold w-8">{fearGreed}</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Reddit</span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-700 rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full"
                style={{ width: `${reddit}%` }}
              ></div>
            </div>
            <span className="text-orange-400 font-bold w-8">{reddit}</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">CoinGecko</span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-700 rounded-full h-2">
              <div
                className="bg-yellow-500 h-2 rounded-full"
                style={{ width: `${coinGecko}%` }}
              ></div>
            </div>
            <span className="text-yellow-400 font-bold w-8">{coinGecko}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentGauge;
