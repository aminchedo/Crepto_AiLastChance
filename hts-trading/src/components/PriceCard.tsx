import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface PriceCardProps {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
}

const PriceCard: React.FC<PriceCardProps> = ({ symbol, price, change24h, volume }) => {
  const isPositive = change24h >= 0;

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6 min-w-[250px] hover:border-blue-500 transition-all duration-300 shadow-lg">
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="text-gray-400 text-sm mb-1">{symbol}/USDT</div>
          <div className="text-white text-3xl font-bold">
            ${price.toFixed(2)}
          </div>
        </div>
        {isPositive ? (
          <TrendingUp className="text-green-500" size={32} />
        ) : (
          <TrendingDown className="text-red-500" size={32} />
        )}
      </div>

      <div className={`text-lg font-semibold mb-3 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
        {isPositive ? '+' : ''}{change24h.toFixed(2)}%
      </div>

      <div className="text-gray-500 text-sm">
        Volume: ${(volume / 1000000).toFixed(2)}M
      </div>
    </div>
  );
};

export default PriceCard;