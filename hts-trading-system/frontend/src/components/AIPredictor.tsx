import React from 'react';
import { Brain, TrendingUp, TrendingDown, Minus, AlertTriangle, Target } from 'lucide-react';
import { AIPredictorProps } from '../types';

const AIPredictor: React.FC<AIPredictorProps> = ({ 
  prediction, 
  symbol, 
  isLoading = false 
}) => {
  if (isLoading) {
    return (
      <div className="ai-predictor animate-pulse">
        <div className="flex justify-between items-center mb-4">
          <div className="h-4 bg-gray-700 rounded w-24"></div>
          <div className="h-6 bg-gray-700 rounded w-20"></div>
        </div>
        <div className="h-16 bg-gray-700 rounded mb-4"></div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="h-16 bg-gray-700 rounded"></div>
          <div className="h-16 bg-gray-700 rounded"></div>
          <div className="h-16 bg-gray-700 rounded"></div>
        </div>
        <div className="h-12 bg-gray-700 rounded"></div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="ai-predictor">
        <div className="text-center py-8">
          <Brain size={48} className="text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Prediction Available</h3>
          <p className="text-gray-400 text-sm">
            AI analysis for {symbol} is not ready yet
          </p>
        </div>
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

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return <TrendingUp size={20} />;
      case 'SELL':
        return <TrendingDown size={20} />;
      default:
        return <Minus size={20} />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 80) return 'text-green-400';
    if (confidence > 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceLevel = (confidence: number) => {
    if (confidence > 80) return 'High';
    if (confidence > 60) return 'Medium';
    return 'Low';
  };

  return (
    <div className="ai-predictor group hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-gray-400 text-sm font-semibold flex items-center space-x-2">
          <Brain size={16} />
          <span>AI Prediction</span>
        </div>
        <div className="text-xs bg-blue-900/30 text-blue-400 px-2 py-1 rounded">
          Confidence: {prediction.confidence}%
        </div>
      </div>

      {/* Signal Display */}
      <div className="mb-4">
        <div
          className={`border rounded-lg p-4 text-center font-bold text-lg ${getSignalColor(prediction.signal)}`}
        >
          <div className="flex items-center justify-center space-x-2">
            {getSignalIcon(prediction.signal)}
            <span>{prediction.signal} SIGNAL</span>
          </div>
        </div>
      </div>

      {/* Probability Breakdown */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Bullish</div>
          <div className="text-green-400 font-bold text-lg">
            {prediction.bullishProbability}%
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Neutral</div>
          <div className="text-yellow-400 font-bold text-lg">
            {prediction.neutralProbability}%
          </div>
        </div>
        <div className="bg-gray-800/50 rounded p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Bearish</div>
          <div className="text-red-400 font-bold text-lg">
            {prediction.bearishProbability}%
          </div>
        </div>
      </div>

      {/* Confidence and Risk */}
      <div className="border-t border-gray-700 pt-3 space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Confidence</span>
          <div className="flex items-center space-x-2">
            <span className={`font-bold ${getConfidenceColor(prediction.confidence)}`}>
              {prediction.confidence}%
            </span>
            <span className={`text-xs px-2 py-1 rounded ${
              prediction.confidence > 80 ? 'bg-green-900/30 text-green-400' :
              prediction.confidence > 60 ? 'bg-yellow-900/30 text-yellow-400' :
              'bg-red-900/30 text-red-400'
            }`}>
              {getConfidenceLevel(prediction.confidence)}
            </span>
          </div>
        </div>
        
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Risk Score</span>
          <div className="flex items-center space-x-2">
            <span className="text-orange-400 font-bold">{prediction.riskScore}%</span>
            <div className="w-16 bg-gray-700 rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${prediction.riskScore}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Timeframe */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Timeframe</span>
          <span className="text-blue-400 font-semibold">{prediction.timeframe}</span>
        </div>

        {/* Model Version */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">Model</span>
          <span className="text-gray-300 font-mono text-xs">{prediction.modelVersion}</span>
        </div>
      </div>

      {/* Price Targets */}
      {prediction.priceTarget && (
        <div className="mt-4 border-t border-gray-700 pt-3">
          <div className="flex items-center space-x-2 mb-2">
            <Target size={16} className="text-purple-400" />
            <span className="text-sm font-semibold text-white">Price Targets</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className="text-gray-400">Short</div>
              <div className="text-white font-semibold">
                ${prediction.priceTarget.short.toFixed(2)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-gray-400">Medium</div>
              <div className="text-white font-semibold">
                ${prediction.priceTarget.medium.toFixed(2)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-gray-400">Long</div>
              <div className="text-white font-semibold">
                ${prediction.priceTarget.long.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Warning for Low Confidence */}
      {prediction.confidence < 60 && (
        <div className="mt-4 flex items-center space-x-2 text-yellow-400 text-xs bg-yellow-900/20 border border-yellow-700 rounded p-2">
          <AlertTriangle size={14} />
          <span>Low confidence prediction - use with caution</span>
        </div>
      )}

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
    </div>
  );
};

export default AIPredictor;