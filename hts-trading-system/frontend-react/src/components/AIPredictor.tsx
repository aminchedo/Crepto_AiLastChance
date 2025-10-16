import React from 'react';
import { PredictionData } from '../types/index';

interface Props {
  prediction: PredictionData | null;
  symbol: string;
}

const AIPredictor: React.FC<Props> = ({ prediction, symbol }) => {
  if (!prediction) {
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 text-center text-gray-400">
        No prediction available
      </div>
    );
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return 'bg-green-900/30 border-green-700 text-green-400';
      case 'SELL':
        return 'bg-red-900/30 border-red-700 text-red-400';
      default:
        return 'bg-yellow-900/30 border-yellow-700 text-yellow-400';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 80) return 'text-green-400';
    if (confidence > 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
      <div className="flex justify-between items-center mb-4">
        <div className="text-gray-400 text-sm font-semibold">🤖 AI Prediction</div>
        <div className="text-xs bg-blue-900/30 text-blue-400 px-2 py-1 rounded">
          Confidence: {prediction.confidence}%
        </div>
      </div>

      <div className="mb-4">
        <div
          className={`border rounded-lg p-4 text-center font-bold text-lg ${getSignalColor(
            prediction.signal
          )}`}
        >
          {prediction.signal} SIGNAL
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Bullish</div>
          <div className="text-green-400 font-bold">
            {prediction.bullishProbability}%
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Neutral</div>
          <div className="text-yellow-400 font-bold">
            {prediction.neutralProbability}%
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Bearish</div>
          <div className="text-red-400 font-bold">
            {prediction.bearishProbability}%
          </div>
        </div>
      </div>

      <div className="border-t border-gray-700 pt-3">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Confidence</span>
          <span className={`font-bold ${getConfidenceColor(prediction.confidence)}`}>
            {prediction.confidence}%
          </span>
        </div>
        <div className="flex justify-between items-center text-sm mt-2">
          <span className="text-gray-400">Risk Score</span>
          <span className="text-orange-400 font-bold">{prediction.riskScore}%</span>
        </div>
      </div>
    </div>
  );
};

export default AIPredictor;
