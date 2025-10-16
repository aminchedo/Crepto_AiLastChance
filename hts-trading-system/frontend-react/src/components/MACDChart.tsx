import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface ChartDataPoint {
  time: number;
  macd: number;
  signal: number;
  histogram: number;
}

interface Props {
  data: ChartDataPoint[];
  currentMACD: {
    macd: number;
    signal: number;
    histogram: number;
    trend: string;
  };
}

const MACDChart: React.FC<Props> = ({ data, currentMACD }) => {
  const isBullish = currentMACD.histogram > 0;

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <div className="text-gray-400 text-sm font-semibold">MACD Indicator</div>
        <span
          className={`text-xs font-bold px-2 py-1 rounded ${
            isBullish
              ? 'bg-green-900/40 text-green-400'
              : 'bg-red-900/40 text-red-400'
          }`}
        >
          {isBullish ? '↑ BULLISH' : '↓ BEARISH'}
        </span>
      </div>

      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <XAxis dataKey="time" tick={false} stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151'
              }}
              labelStyle={{ color: '#ffffff' }}
            />

            <Bar dataKey="histogram" fill="#6366f1" opacity={0.6} />

            <Line
              type="monotone"
              dataKey="macd"
              stroke="#3b82f6"
              dot={false}
              isAnimationActive={false}
              strokeWidth={2}
            />

            <Line
              type="monotone"
              dataKey="signal"
              stroke="#f59e0b"
              dot={false}
              isAnimationActive={false}
              strokeWidth={2}
            />
          </ComposedChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          Loading chart data...
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 mt-4 text-sm">
        <div className="bg-gray-800/50 rounded p-3">
          <div className="text-gray-400 text-xs mb-1">MACD</div>
          <div className="text-blue-400 font-bold">
            {currentMACD.macd.toFixed(4)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3">
          <div className="text-gray-400 text-xs mb-1">Signal</div>
          <div className="text-yellow-400 font-bold">
            {currentMACD.signal.toFixed(4)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3">
          <div className="text-gray-400 text-xs mb-1">Histogram</div>
          <div
            className={
              currentMACD.histogram > 0
                ? 'text-green-400 font-bold'
                : 'text-red-400 font-bold'
            }
          >
            {currentMACD.histogram.toFixed(4)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MACDChart;
