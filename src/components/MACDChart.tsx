import React from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { MACDChartProps } from '../types';

const MACDChart: React.FC<MACDChartProps> = ({ 
  data, 
  currentMACD, 
  isLoading = false 
}) => {
  const isBullish = currentMACD.histogram > 0;

  if (isLoading) {
    return (
      <div className="sentiment-gauge animate-pulse">
        <div className="flex justify-between items-center mb-4">
          <div className="h-4 bg-gray-700 rounded w-32"></div>
          <div className="h-6 bg-gray-700 rounded w-20"></div>
        </div>
        <div className="h-64 bg-gray-700 rounded"></div>
        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="h-16 bg-gray-700 rounded"></div>
          <div className="h-16 bg-gray-700 rounded"></div>
          <div className="h-16 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="sentiment-gauge">
        <div className="flex justify-between items-center mb-4">
          <div className="text-gray-400 text-sm font-semibold">MACD Indicator</div>
          <span className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
            No Data
          </span>
        </div>
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-4xl mb-2">📊</div>
            <p>No chart data available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="sentiment-gauge group hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-gray-400 text-sm font-semibold">MACD Indicator</div>
        <span className={`text-xs font-bold px-2 py-1 rounded ${
          isBullish
            ? 'bg-green-900/40 text-green-400'
            : 'bg-red-900/40 text-red-400'
        }`}>
          {isBullish ? '↑ BULLISH' : '↓ BEARISH'}
        </span>
      </div>

      {/* Chart */}
      <div className="h-64 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <XAxis 
              dataKey="time" 
              tick={false} 
              stroke="#6b7280"
              axisLine={false}
            />
            <YAxis 
              stroke="#6b7280" 
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#ffffff'
              }}
              labelStyle={{ color: '#ffffff' }}
              formatter={(value: any, name: string) => {
                const formattedValue = typeof value === 'number' ? value.toFixed(4) : value;
                return [formattedValue, name];
              }}
            />

            {/* Zero line */}
            <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="2 2" />

            {/* Histogram bars */}
            <Bar 
              dataKey="histogram" 
              fill="#6366f1" 
              opacity={0.6}
              radius={[2, 2, 0, 0]}
            />

            {/* MACD line */}
            <Line
              type="monotone"
              dataKey="macd"
              stroke="#3b82f6"
              dot={false}
              isAnimationActive={false}
              strokeWidth={2}
            />

            {/* Signal line */}
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
      </div>

      {/* Current Values */}
      <div className="grid grid-cols-3 gap-3 text-sm">
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">MACD</div>
          <div className="text-blue-400 font-bold">
            {currentMACD.macd.toFixed(4)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Signal</div>
          <div className="text-yellow-400 font-bold">
            {currentMACD.signal.toFixed(4)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Histogram</div>
          <div className={`font-bold ${
            currentMACD.histogram > 0
              ? 'text-green-400'
              : 'text-red-400'
          }`}>
            {currentMACD.histogram.toFixed(4)}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center space-x-4 text-xs">
        <div className="flex items-center space-x-1">
          <div className="w-3 h-0.5 bg-blue-400"></div>
          <span className="text-gray-400">MACD</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-0.5 bg-yellow-400"></div>
          <span className="text-gray-400">Signal</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-indigo-500 rounded-sm"></div>
          <span className="text-gray-400">Histogram</span>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </div>
  );
};

export default MACDChart;